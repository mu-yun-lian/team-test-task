"""sub-scoring-engine.

Scores each canonical slide on three axes — persuasion (40%), logic (35%),
clarity (25%) — against the rubrics defined in ``frameworks.RUBRICS``.

The engine is deliberately deterministic and offline-first so it is fully
testable and reproducible; an optional ``LLMScorer`` augmentation hook is
exposed for production deployments that want narrative refinement (see
``llm`` adapter). Missing canonical slides are flagged as gaps.

Per-axis score model
    axis_score = 100 * (sum of weights of satisfied rubric elements on axis)
                 / (sum of all weights on that axis)
then adjusted by detector-driven penalties/bonuses, clamped to [0, 100].
"""

from __future__ import annotations

import re
from typing import Callable

from . import frameworks as fw
from .canonical import CANONICAL_ORDER, canonical_slides
from .frameworks import RUBRICS, SlideRubric
from .models import (
    AxisScore,
    Context,
    Deck,
    Finding,
    FundabilityBand,
    Gap,
    SlideContent,
    SlideKind,
    SlideScore,
    Stage,
)

# ---------------------------------------------------------------------------
# Per-element detectors
# ---------------------------------------------------------------------------

_AUDIENCE_WORDS = re.compile(
    r"\b(smb|smes|enterprises?|companies|teams?|developers?|marketers?|hospitals?|"
    r"students?|consumers?|buyers?|users?|customers?|creators?|operators?|"
    r"restaurants?|clinics?|banks?|retailers?|agents?|founders?)\b",
    re.I,
)
_PAIN_WORDS = re.compile(
    r"\b(cost|lose|lost|waste|hours?|friction|slow|broken|inefficient|inefficienc|"
    r"pain|suffer|struggle|manual|error|errors?|delay|bottleneck|expensive|risk)\b",
    re.I,
)
_WHY_NOW = re.compile(
    r"\b(why now|today|right now|regulation|regulatory|ai\b|ml\b|cloud|mobile|"
    r"shift|rising|emerging|post-?covid|new regulation|compliance|mandate)\b",
    re.I,
)
_SPECIFIC = re.compile(r"(\d|\$|%)|for example|e\.g\.|i\.e\.|case study|example", re.I)
_DIFF_WORDS = re.compile(
    r"\b(unlike|only|first|better|faster|cheaper|proprietary|exclusive|"
    r"differentiat|advantage|unique|10x)\b",
    re.I,
)
_HOW_WORDS = re.compile(
    r"\b(how|works?|uses?|via|through|engine|ai|ml|model|api|pipeline|"
    r"algorithm|platform|infrastructure)\b",
    re.I,
)
_REVENUE_MODEL = re.compile(
    r"\b(saas|marketplace|subscription|transaction|licens|usage|freemium|"
    r"advertis|ad\s+supported|take\s+rate|interchange|consumption|tiered)\b",
    re.I,
)
_OUTCOME_WORDS = re.compile(
    r"\b(outcome|result|reduce|increase|save|cut|improve|enable|deliver|"
    r"automate|accelerate|shorten|boost)\b",
    re.I,
)
_TECH_WORDS = re.compile(r"\b(ai|ml|model|api|platform|engine|proprietary|infrastructure|llm)\b", re.I)
_GROWTH_WORDS = re.compile(r"\b(growth|grew|growing|mom|qoq|yoy|increase|up\s+\d|x\s+growth)\b|%", re.I)
_CADENCE_WORDS = re.compile(
    r"\b(mom|qoq|yoy|last\s+\d+\s*days?|trailing|per month|monthly|quarterly|"
    r"annually|2024|2025|2026|year over year|month over month)\b",
    re.I,
)
_CHANNEL_WORDS = re.compile(
    r"\b(seo|ads|advertising|content|outbound|inbound|sales|partnership|referral|"
    r"community|linkedin|events?|webinar|podcast|email|pr|affiliate)\b",
    re.I,
)
_CAC_WORDS = re.compile(r"\b(cac|payback|cost\s+to\s+acquire|ltv|lvc|caca)\b", re.I)
_REPEAT_WORDS = re.compile(
    r"\b(repeatable|scalable|funnel|playbook|motion|engine|programmatic|"
    r"systematic|machine|loop)\b",
    re.I,
)
_TRACK_WORDS = re.compile(
    r"\b(founded|ex-|formerly|previously|built|scaled|led|exit|ipo|acquired|"
    r"y combinator|phd|worked at|alumn)\b",
    re.I,
)
_GAP_WORDS = re.compile(
    r"\b(looking for|hiring|seeking|advisors?|to round out|gap|next hire|"
    r"recruit|building out|expanding)\b",
    re.I,
)
_MILESTONE_WORDS = re.compile(
    r"\b(milestone|launch|reach|targets?|ship|goal|by end of|next \d+|milestones|"
    r" Series A|product-market fit|\\$\\d+m arr)\b",
    re.I,
)
_SOURCE_WORDS = re.compile(r"\b(source|per|according|statista|gartner|census|report|study|ibc|forrester|idc)\b", re.I)
_SEGMENT_WORDS = re.compile(r"\b(sam|som|segment|beachhead|target\s+segment|first\s+customers?|niche|wedge)\b", re.I)
_MATH_WORDS = re.compile(
    r"[x×=*]|customers?\s*[x×]\s*(acv|arpu|price)|per (customer|account|user) per (month|year)", re.I
)


def _has(pattern: re.Pattern, text: str) -> bool:
    return bool(pattern.search(text or ""))


CODE_CHECKERS: dict[str, Callable[[SlideContent], bool]] = {
    # problem
    "prob-who": lambda s: _has(_AUDIENCE_WORDS, s.text),
    "prob-pain": lambda s: _has(_PAIN_WORDS, s.text),
    "prob-urgency": lambda s: _has(_WHY_NOW, s.text),
    "prob-specific": lambda s: _has(_SPECIFIC, s.text),
    # solution
    "sol-clear": lambda s: bool(s.headline.strip()) and len(s.headline.split()) <= 16,
    "sol-fit": lambda s: bool(s.headline.strip()) and len(s.bullets) >= 2,
    "sol-how": lambda s: _has(_HOW_WORDS, s.text),
    "sol-diff": lambda s: _has(_DIFF_WORDS, s.text),
    # market
    "tam-bottom-up": lambda s: fw.has_bottom_up_tam(s.text),
    "tam-math": lambda s: _has(_MATH_WORDS, s.text),
    "tam-segments": lambda s: _has(_SEGMENT_WORDS, s.text),
    "tam-credible": lambda s: _has(_SOURCE_WORDS, s.text),
    "tam-headline": lambda s: bool(fw._MONEY_NUMBER.search(s.text or "")),
    # product
    "prod-evidence": lambda s: fw.has_evidence_words(s.text),
    "prod-outcomes": lambda s: _has(_OUTCOME_WORDS, s.text),
    "prod-tech": lambda s: _has(_TECH_WORDS, s.text),
    "prod-clear": lambda s: bool(s.headline.strip()) and len(s.headline.split()) <= 18,
    # business model
    "bm-revenue": lambda s: _has(_REVENUE_MODEL, s.text),
    "bm-price": lambda s: fw.has_pricing(s.text),
    "bm-units": lambda s: fw.has_unit_economics(s.text),
    "bm-clear": lambda s: bool(s.headline.strip()) and len(s.headline.split()) <= 14,
    # traction
    "trac-growth": lambda s: _has(_GROWTH_WORDS, s.text),
    "trac-revenue": lambda s: fw.has_revenue_metric(s.text),
    "trac-retention": lambda s: fw.has_retention_metric(s.text),
    "trac-cadence": lambda s: _has(_CADENCE_WORDS, s.text),
    # gtm
    "gtm-channel": lambda s: _has(_CHANNEL_WORDS, s.text),
    "gtm-cac": lambda s: _has(_CAC_WORDS, s.text) or fw.has_unit_economics(s.text),
    "gtm-repeat": lambda s: _has(_REPEAT_WORDS, s.text),
    "gtm-clear": lambda s: bool(s.headline.strip()),
    # competition
    "comp-landscape": lambda s: fw.has_named_competitors(s.text),
    "comp-matrix": lambda s: fw.has_comparison_axes(s.text),
    "comp-diff": lambda s: _has(_DIFF_WORDS, s.text),
    "comp-moat": lambda s: fw.has_moat(s.text),
    # team
    "team-founders": lambda s: fw.has_named_founders(s.text),
    "team-fit": lambda s: fw.has_domain_fit(s.text),
    "team-track": lambda s: _has(_TRACK_WORDS, s.text),
    "team-gaps": lambda s: _has(_GAP_WORDS, s.text),
    # financials
    "fin-projection": lambda s: fw.has_amount(s.text) or bool(re.search(r"arr|revenue|mrr", s.text, re.I)),
    "fin-assumptions": lambda s: fw.has_assumptions(s.text),
    "fin-realistic": lambda s: not fw.looks_inflated_projection(s.text),
    "fin-margin": lambda s: _has(re.compile(r"\b(margin|gross|burn|runway|ebitda|operating)\b", re.I), s.text),
    # ask
    "ask-amount": lambda s: fw.has_amount(s.text),
    "ask-use": lambda s: bool(
        re.search(
            r"\b(use of funds?|hire|hiring|engineering|sales|marketing|product|growth|ops|infrastructure|research)\b",
            s.text,
            re.I,
        )
    ),
    "ask-milestones": lambda s: _has(_MILESTONE_WORDS, s.text),
    "ask-runway": lambda s: fw.has_runway(s.text),
}


CRITICAL_SLIDES: frozenset[SlideKind] = frozenset(
    {SlideKind.PROBLEM, SlideKind.SOLUTION, SlideKind.TRACTION, SlideKind.TEAM, SlideKind.ASK}
)

# Slides weighted slightly heavier in the overall deck score.
_SLIDE_WEIGHTS: dict[SlideKind, float] = {
    SlideKind.PROBLEM: 1.3,
    SlideKind.SOLUTION: 1.3,
    SlideKind.MARKET_TAM: 1.1,
    SlideKind.PRODUCT: 1.0,
    SlideKind.BUSINESS_MODEL: 1.1,
    SlideKind.TRACTION: 1.25,
    SlideKind.GTM: 0.9,
    SlideKind.COMPETITION: 0.9,
    SlideKind.TEAM: 1.15,
    SlideKind.FINANCIALS: 1.0,
    SlideKind.ASK: 1.05,
}


class ScoringEngine:
    """Second sub-skill of the harness: per-slide + overall scoring."""

    def score(self, deck: Deck, ctx: Context) -> tuple[list[SlideScore], list[Gap]]:
        canonical, _extras, missing = canonical_slides(deck.slides)
        # Reconcile deck's canonical list back onto the deck object for callers.
        deck.slides = canonical
        deck.extras = _extras

        per_slide: list[SlideScore] = []
        for kind in CANONICAL_ORDER:
            rubric = RUBRICS[kind]
            slide = next((s for s in canonical if s.kind == kind), None)
            if slide is None:
                per_slide.append(self._gap_score(rubric))
                continue
            per_slide.append(self._score_slide(slide, rubric, ctx))

        gaps = [Gap(kind=k, reason=f"Missing canonical {RUBRICS[k].label} slide.") for k in missing]
        return per_slide, gaps

    # ------------------------------------------------------------------
    def _gap_score(self, rubric: SlideRubric) -> SlideScore:
        return SlideScore(
            kind=rubric.kind,
            label=rubric.label,
            present=False,
            axes=AxisScore(persuasion=0.0, logic=0.0, clarity=0.0),
            findings=[
                Finding(
                    code=f"missing-{rubric.kind.value}",
                    severity="blocker",
                    message=f"{rubric.label} slide is missing — a critical gap.",
                    deduction=100.0,
                )
            ],
        )

    def _score_slide(self, slide: SlideContent, rubric: SlideRubric, ctx: Context) -> SlideScore:
        findings: list[Finding] = []

        # Aggregate weights per axis.
        totals = {"persuasion": 0.0, "logic": 0.0, "clarity": 0.0}
        satisfied = {"persuasion": 0.0, "logic": 0.0, "clarity": 0.0}
        evidence: list[str] = []

        for el in rubric.elements:
            totals[el.axis] += el.weight
            checker = CODE_CHECKERS.get(el.code)
            ok = checker(slide) if checker else False
            if ok:
                satisfied[el.axis] += el.weight
                evidence.append(f"{el.code}:pass")
            else:
                sev = "major" if el.required and el.weight >= 0.25 else "minor"
                findings.append(
                    Finding(
                        code=el.code,
                        severity=sev if el.required else "info",
                        message=f"Missing/weak: {el.label}.",
                        deduction=el.weight,
                    )
                )

        axes = AxisScore(
            persuasion=self._axis(satisfied["persuasion"], totals["persuasion"]),
            logic=self._axis(satisfied["logic"], totals["logic"]),
            clarity=self._axis(satisfied["clarity"], totals["clarity"]),
        )

        # Structural clarity adjustments.
        if not slide.headline.strip():
            axes = axes.model_copy(update={"clarity": max(0.0, axes.clarity - 8.0)})
            findings.append(
                Finding(
                    code="no-headline",
                    severity="minor",
                    message="Slide has no headline — clarity suffers.",
                    deduction=8.0,
                )
            )
        n_bullets = fw.count_bullets(slide.bullets)
        if n_bullets < 2:
            axes = axes.model_copy(update={"clarity": max(0.0, axes.clarity - 6.0)})
            findings.append(
                Finding(
                    code="sparse-bullets",
                    severity="minor",
                    message="Very few bullet points — slide reads as thin.",
                    deduction=6.0,
                )
            )
        elif n_bullets > 8:
            axes = axes.model_copy(update={"clarity": max(0.0, axes.clarity - 5.0)})
            findings.append(
                Finding(
                    code="dense-bullets",
                    severity="minor",
                    message="Too many bullets — slide is dense, not skimmable.",
                    deduction=5.0,
                )
            )

        # Slide-specific detector-driven penalties (these reflect named
        # investor objections beyond element presence).
        axes, findings = self._apply_special_penalties(slide, rubric, axes, findings)

        return SlideScore(
            kind=rubric.kind,
            label=rubric.label,
            present=True,
            axes=axes,
            findings=findings,
            evidence=evidence,
        )

    def _axis(self, satisfied_weight: float, total_weight: float, floor: float = 15.0) -> float:
        if total_weight <= 0:
            return 100.0
        score = 100.0 * (satisfied_weight / total_weight)
        return round(max(floor, min(100.0, score)), 1)

    def _apply_special_penalties(
        self,
        slide: SlideContent,
        rubric: SlideRubric,
        axes: AxisScore,
        findings: list[Finding],
    ) -> tuple[AxisScore, list[Finding]]:
        text = slide.text
        p, logic, c = axes.persuasion, axes.logic, axes.clarity

        if rubric.kind == SlideKind.MARKET_TAM:
            if fw.is_top_down_tam(text):
                logic = max(0.0, logic - 25.0)
                p = max(0.0, p - 10.0)
                findings.append(
                    Finding(
                        code="top-down-tam",
                        severity="major",
                        message="Top-down TAM ('X% of a $YB market') is not defensible. Show bottom-up sizing.",
                        deduction=25.0,
                    )
                )
            if fw.has_bottom_up_tam(text):
                logic = min(100.0, logic + 4.0)

        elif rubric.kind == SlideKind.TRACTION:
            if fw.has_vanity_metrics(text):
                p = max(0.0, p - 25.0)
                logic = max(0.0, logic - 10.0)
                findings.append(
                    Finding(
                        code="vanity-metrics",
                        severity="major",
                        message="Traction relies on vanity metrics (signups/visitors) without revenue or retention.",
                        deduction=25.0,
                    )
                )
            if fw.has_retention_metric(text):
                logic = min(100.0, logic + 4.0)

        elif rubric.kind == SlideKind.FINANCIALS:
            if fw.looks_inflated_projection(text):
                logic = max(0.0, logic - 28.0)
                p = max(0.0, p - 8.0)
                findings.append(
                    Finding(
                        code="inflated-projection",
                        severity="major",
                        message="Financial projection looks like a hockey-stick "
                        "without a stated basis. Provide assumptions.",
                        deduction=28.0,
                    )
                )

        elif rubric.kind == SlideKind.COMPETITION:
            if not fw.has_moat(text):
                logic = max(0.0, logic - 8.0)
                findings.append(
                    Finding(
                        code="no-moat",
                        severity="minor",
                        message="No explicit defensibility / moat articulated.",
                        deduction=8.0,
                    )
                )

        return AxisScore(persuasion=round(p, 1), logic=round(logic, 1), clarity=round(c, 1)), findings

    # ------------------------------------------------------------------
    @staticmethod
    def overall(per_slide: list[SlideScore], gaps: list[Gap], ctx: Context) -> tuple[float, FundabilityBand]:
        weighted_sum, weight_total = 0.0, 0.0
        for s in per_slide:
            if not s.present:
                continue
            w = _SLIDE_WEIGHTS.get(s.kind, 1.0)
            weighted_sum += s.weighted * w
            weight_total += w
        base = weighted_sum / weight_total if weight_total else 0.0

        # Gap penalties.
        gap_penalty = min(20.0, len(gaps) * 3.5)
        critical_missing = {g.kind for g in gaps if g.kind in CRITICAL_SLIDES}
        # Stage-aware: traction matters more from Series A onward.
        stage = ctx.stage
        if stage in (Stage.SERIES_A, Stage.SERIES_B_PLUS) and SlideKind.TRACTION in critical_missing:
            gap_penalty += 8.0
        if SlideKind.PROBLEM in critical_missing or SlideKind.SOLUTION in critical_missing:
            gap_penalty += 6.0

        overall = round(max(0.0, min(100.0, base - gap_penalty)), 1)

        # Blockers cap the band.
        has_blocker = any(
            (s.present and any(f.severity == "blocker" for f in s.findings))
            or (not s.present and s.kind in CRITICAL_SLIDES)
            for s in per_slide
        )
        if overall >= 80 and not has_blocker:
            band = FundabilityBand.PASS
        elif overall >= 65 and not has_blocker:
            band = FundabilityBand.REFINE
        elif overall >= 45:
            band = FundabilityBand.REWORK
        else:
            band = FundabilityBand.NOT_FUNDABLE
        # Critical missing always forces at most REWORK.
        if has_blocker and band == FundabilityBand.PASS:
            band = FundabilityBand.REFINE
        if critical_missing and band == FundabilityBand.REFINE:
            band = FundabilityBand.REWORK
        return overall, band
