"""sub-improvement-roadmap.

Converts per-slide scores and investor objections into concrete, slide-level
edits: a before -> after rewrite per weak slide, plus content outlines for any
missing canonical slide. Every raised objection must be addressed somewhere
in the roadmap.
"""

from __future__ import annotations

from typing import Optional

from .canonical import CANONICAL_LABELS
from .models import (
    Context,
    Effort,
    Gap,
    Impact,
    Objection,
    RoadmapItem,
    SlideKind,
    SlideScore,
)

# Before/after guidance per finding code, keyed by code.
_FIX_GUIDANCE: dict[str, tuple[str, str, Effort, Impact]] = {
    "top-down-tam": (
        "Market slide claims 'X% of a $YB market'.",
        "Rewrite to bottom-up: '#addressable customers x ACV = TAM; SAM = ...; "
        "SOM (3yr) = ...' with the sizing math and a cited customer-base source.",
        Effort.M,
        Impact.HIGH,
    ),
    "vanity-metrics": (
        "Traction slide leads with vanity metrics (signups / visitors).",
        "Lead with revenue (MRR/ARR), then retention/NRR, churn, and CAC payback "
        "for the same period; keep signups only as context.",
        Effort.M,
        Impact.HIGH,
    ),
    "inflated-projection": (
        "Financials show a hockey-stick to large ARR with no basis.",
        "Replace with a bottom-up build: state the 3-5 key drivers (conversion, "
        "price, churn, capacity) and show the curve that falls out of them.",
        Effort.L,
        Impact.HIGH,
    ),
    "no-moat": (
        "Competition slide names rivals but not defensibility.",
        "Add a 'Why we win / moat' row: name the defensible advantage (data, "
        "network effect, switching cost, IP, distribution).",
        Effort.S,
        Impact.MED,
    ),
    "no-headline": (
        "Slides lack headlines; deck isn't skimmable in 20 seconds.",
        "Give each slide a one-line takeaway headline (<=12 words) stating the "
        "single point an investor should remember.",
        Effort.S,
        Impact.MED,
    ),
    "sparse-bullets": (
        "Slides have too few bullets and read as thin.",
        "Add 3-5 supporting bullets that each back the headline with a fact or number.",
        Effort.S,
        Impact.LOW,
    ),
    "dense-bullets": (
        "Slides are bullet dumps (>8 bullets).",
        "Collapse to <=5 bullets grouped under the headline; move detail to an appendix.",
        Effort.S,
        Impact.MED,
    ),
}

# Per-slide content outline for missing canonical slides.
_MISSING_OUTLINE: dict[SlideKind, str] = {
    SlideKind.PROBLEM: (
        "Outline: (1) one-sentence problem statement; (2) who has it (audience); "
        "(3) the cost/pain of the status quo; (4) why now (urgency)."
    ),
    SlideKind.SOLUTION: (
        "Outline: (1) one-line value proposition headline; (2) how it works "
        "(mechanism); (3) how it maps to each problem; (4) what is uniquely "
        "better."
    ),
    SlideKind.MARKET_TAM: (
        "Outline: (1) headline bottom-up TAM; (2) the sizing math "
        "(#customers x ACV); (3) SAM and SOM; (4) cited customer-base source."
    ),
    SlideKind.PRODUCT: (
        "Outline: (1) a screenshot/demo proof of existence; (2) features tied to "
        "outcomes; (3) defensible technology; (4) plain-language explanation."
    ),
    SlideKind.BUSINESS_MODEL: (
        "Outline: (1) one-line business model; (2) revenue model; (3) pricing / "
        "ACV; (4) unit economics (CAC/LTV/payback/margin)."
    ),
    SlideKind.TRACTION: (
        "Outline: (1) revenue/ARR with growth trend; (2) retention/NRR; (3) CAC payback; (4) cadence and time period."
    ),
    SlideKind.GTM: (
        "Outline: (1) one-line motion; (2) named channels; (3) CAC and payback; (4) why it is repeatable/scalable."
    ),
    SlideKind.COMPETITION: (
        "Outline: (1) honest landscape of real competitors; (2) comparison "
        "matrix on 2-3 axes; (3) how you win; (4) your moat/defensibility."
    ),
    SlideKind.TEAM: (
        "Outline: (1) founders with roles; (2) relevant domain/operating "
        "experience; (3) prior outcomes/credibility; (4) how role gaps are "
        "covered."
    ),
    SlideKind.FINANCIALS: (
        "Outline: (1) revenue/ARR projection with horizon; (2) key assumptions; "
        "(3) realistic (non-hockey-stick) curve; (4) margin/burn/runway."
    ),
    SlideKind.ASK: (
        "Outline: (1) raise amount; (2) use-of-funds breakdown; (3) milestones "
        "the round reaches; (4) runway the round provides."
    ),
}


class ImprovementRoadmap:
    """Fifth sub-skill of the harness: slide-level fix plan."""

    def build(
        self,
        per_slide: list[SlideScore],
        gaps: list[Gap],
        objections: list[Objection],
        ctx: Context,
    ) -> list[RoadmapItem]:
        items: list[RoadmapItem] = []
        addressed: set[str] = set()

        # 1) Per-slide rewrites driven by major/blocker findings.
        for s in per_slide:
            if not s.present:
                continue
            if s.weighted >= 85 and not any(f.severity in ("major", "blocker") for f in s.findings):
                continue  # strong slide, no rewrite needed
            item = self._rewrite_for_slide(s)
            if item is not None:
                items.append(item)

        # 2) Missing canonical slides -> add-slide roadmap items.
        for g in gaps:
            outline = _MISSING_OUTLINE.get(g.kind, "Add this canonical slide.")
            items.append(
                RoadmapItem(
                    slide_kind=g.kind,
                    before=f"(missing) {CANONICAL_LABELS[g.kind]} slide is absent.",
                    after=f"Add a {CANONICAL_LABELS[g.kind]} slide. {outline}",
                    effort=Effort.M,
                    impact=Impact.HIGH,
                )
            )

        # 3) Ensure every objection is addressed by an item (link + backfill).
        for obj in objections:
            self._ensure_addressed(obj, items, addressed)

        # 4) Sort: gaps + lowest-scoring first.
        def sort_key(it: RoadmapItem):
            pres = next((s for s in per_slide if s.kind == it.slide_kind), None)
            score = pres.weighted if (pres and pres.present) else -1
            return (0 if it.slide_kind in {g.kind for g in gaps} else 1, score, it.slide_kind.value)

        items.sort(key=sort_key)
        return items

    # ------------------------------------------------------------------
    def _rewrite_for_slide(self, s: SlideScore) -> Optional[RoadmapItem]:
        # Prefer the highest-impact finding's guidance; else a generic rewrite.
        major = [f for f in s.findings if f.severity in ("major", "blocker")]
        if major:
            f = sorted(major, key=lambda x: x.deduction, reverse=True)[0]
            guidance = _FIX_GUIDANCE.get(f.code)
            if guidance:
                before, after, effort, impact = guidance
                return RoadmapItem(
                    slide_kind=s.kind,
                    before=before,
                    after=after,
                    effort=effort,
                    impact=impact,
                    objection_addressed=None,
                )
            return RoadmapItem(
                slide_kind=s.kind,
                before=f"{s.label} slide is weak ({s.weighted}/100): {f.message}",
                after=f"Strengthen the {s.label} slide by addressing: {f.message}",
                effort=Effort.M,
                impact=Impact.MED,
            )
        # Minor-only weakness: clarity/density nudge.
        minor_msgs = "; ".join(f.message for f in s.findings if f.severity == "minor") or "Polish for clarity."
        return RoadmapItem(
            slide_kind=s.kind,
            before=f"{s.label} slide scored {s.weighted}/100 with minor issues.",
            after=f"Polish the {s.label} slide: {minor_msgs}",
            effort=Effort.S,
            impact=Impact.LOW,
        )

    def _ensure_addressed(self, obj: Objection, items: list[RoadmapItem], addressed: set[str]) -> bool:
        # If an existing item covers this slide, link the objection to it.
        for it in items:
            if it.slide_kind == obj.slide_kind and it.objection_addressed is None:
                it.objection_addressed = obj.question
                addressed.add(obj.question)
                return True
        # Otherwise backfill a dedicated item mapped to the objection.
        kind = obj.slide_kind or SlideKind.TEAM
        items.append(
            RoadmapItem(
                slide_kind=kind,
                before=f"Objection not yet covered: {obj.question}",
                after=f"Address on the {CANONICAL_LABELS.get(kind, kind.value)} slide "
                f"by providing: {obj.resolving_evidence}",
                effort=Effort.M,
                impact=Impact.HIGH,
                objection_addressed=obj.question,
            )
        )
        addressed.add(obj.question)
        return True
