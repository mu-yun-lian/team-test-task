"""sub-quality-reviewer.

The investor devil's-advocate pass. It converts scored findings and gaps into
the tough questions a real partner meeting would ask, plus a set of
stage-appropriate baseline objections, so the founder is never blindsided.

Quality gate: at least 5 substantive objections, each mapped to a slide and to
the evidence that would resolve it.
"""

from __future__ import annotations

from .models import Context, Gap, Objection, SlideKind, SlideScore, Stage

# Maps a finding code -> (objection question template, resolving evidence).
_FINDING_OBJECTIONS: dict[str, tuple[str, str]] = {
    "top-down-tam": (
        "Your TAM is top-down ('X% of a huge market'). What is the bottom-up TAM, "
        "and how many customers at what ACV does that require?",
        "Bottom-up TAM math: #addressable customers x realistic ACV, plus SAM and SOM.",
    ),
    "vanity-metrics": (
        "Traction is shown in signups/visitors. What are your revenue, retention, "
        "and payback — do users actually stay and pay?",
        "Revenue (MRR/ARR), retention/NRR, churn, and CAC payback for the same period.",
    ),
    "inflated-projection": (
        "Your financials project a hockey-stick to a large ARR within ~2 years. "
        "What assumptions drive that, and what gets you from today to that number?",
        "A bottoms-up build: top-line drivers, conversion, price, churn, and the hiring/spend plan behind the curve.",
    ),
    "no-moat": (
        "What stops a well-funded incumbent from copying this in 12 months? Where is your moat?",
        "Explicit defensibility: network effects, data, switching cost, IP, or distribution advantage.",
    ),
    "missing-business-model": (
        "There is no business-model slide. How do you actually make money, and what are the unit economics?",
        "Revenue model, pricing/ACV, and CAC/LTV/payback for at least one segment.",
    ),
    "missing-traction": (
        "There is no traction slide. What evidence do you have that this works?",
        "Quantitative traction — revenue, usage, retention, growth — with cadence.",
    ),
    "missing-team": (
        "We can't see the team. Why is this the team to win this market?",
        "Founders, roles, relevant experience, and how role gaps are covered.",
    ),
    "missing-problem": (
        "The deck never states the problem clearly. What exactly is the pain and who feels it?",
        "A named audience, the cost of the status quo, and why now.",
    ),
    "missing-solution": (
        "What is the solution and why is it the right one?",
        "A one-line value proposition mapped to each problem, plus the mechanism.",
    ),
    "missing-market-tam": (
        "There is no market slide. How big is this, and is it bottom-up defensible?",
        "Bottom-up TAM/SAM/SOM with the sizing math.",
    ),
    "missing-ask": (
        "How much are you raising and what does this round buy?",
        "A raise amount, use-of-funds breakdown, and the milestones the round reaches.",
    ),
    "no-headline": (
        "Several slides have no headline — I can't skim this in 20 seconds. Can "
        "each slide stand on a one-line takeaway?",
        "A crisp headline per slide stating the single takeaway.",
    ),
}

_STAGE_BASELINES: dict[Stage, list[tuple[str, str, str]]] = {
    Stage.PRE_SEED: [
        (
            "How did you discover this problem — is it something you personally lived?",
            "Founder story / domain evidence; customer discovery interviews.",
            "problem",
        ),
        (
            "What is the smallest experiment that would prove customers will pay?",
            "A pre-sold pilot, LOI, waitlist-to-paid conversion, or paid pilot results.",
            "traction",
        ),
        (
            "Why this team and why now — what is the unfair advantage at pre-seed?",
            "Founder-market fit and a why-now trigger.",
            "team",
        ),
        (
            "What is the 12-month milestone that this $Xk gets you to?",
            "Specific, measurable milestone tied to the ask.",
            "ask",
        ),
        (
            "Who is your first 10 customers and how do you reach them?",
            "A named beachhead segment and an acquisition path to the first 10.",
            "gtm",
        ),
    ],
    Stage.SEED: [
        (
            "What is your CAC and payback period by channel?",
            "CAC by channel, blended payback, and contribution margin.",
            "business-model",
        ),
        ("Is your TAM bottom-up? Show the math.", "Bottom-up TAM with #customers x ACV; SAM; SOM.", "market-tam"),
        ("What does retention look like — are users staying?", "NRR, logo retention, and a cohort curve.", "traction"),
        (
            "What stops an incumbent from building this in a quarter?",
            "A named moat: data, network effects, IP, or distribution.",
            "competition",
        ),
        (
            "What does this round buy in milestones, and what run rate does it reach?",
            "Milestones (e.g. $X MRR) and the runway/next-round plan.",
            "ask",
        ),
    ],
    Stage.SERIES_A: [
        (
            "You have growth, but is it repeatable and profitable per unit?",
            "Repeatable acquisition motion with CAC payback < 12 months.",
            "gtm",
        ),
        ("What is your net revenue retention, and is it >100%?", "NRR and expansion vs. churn cohorts.", "traction"),
        (
            "What is the path to $10M–$20M ARR and the hires required?",
            "An operating plan with quota-carrying sales capacity and CAC targets.",
            "financials",
        ),
        (
            "How concentrated is revenue — top 5 customers as % of ARR?",
            "Revenue concentration and logo retention.",
            "traction",
        ),
        (
            "Why is now the right time for Series A vs. another seed extension?",
            "Proof of product-market fit and a scalable GTM motion.",
            "ask",
        ),
    ],
    Stage.SERIES_B_PLUS: [
        (
            "Can you grow without the same marginal unit economics? Is LTV/CAC > 3?",
            "LTV/CAC by cohort and marginal channel economics.",
            "business-model",
        ),
        (
            "What is the path to profitability and the burn to get there?",
            "A path-to-profitability model with margin and burn assumptions.",
            "financials",
        ),
        (
            "How do you expand into adjacent markets without losing focus?",
            "A segment-expansion thesis with beachhead proof and TAM for new segments.",
            "market-tam",
        ),
        (
            "What is the competitive moat at scale vs. larger incumbents?",
            "Defensibility at scale: data, network effects, switching costs, brand.",
            "competition",
        ),
        (
            "What does this round's capital do that growth from revenue cannot?",
            "Use of funds mapped to specific inflection milestones.",
            "ask",
        ),
    ],
}

_KIND_FROM_STR = {k.value: k for k in SlideKind}


class QualityReviewer:
    """Fourth sub-skill of the harness: investor devil's-advocate pass."""

    def review(
        self,
        per_slide: list[SlideScore],
        gaps: list[Gap],
        ctx: Context,
    ) -> list[Objection]:
        objections: list[Objection] = []
        seen_q: set[str] = set()

        # 1) Findings -> objections (major / blocker only).
        for s in per_slide:
            if not s.present:
                continue
            for f in s.findings:
                if f.severity not in ("major", "blocker"):
                    continue
                # Only map by the finding's own code; a weak-but-present slide
                # is NOT a 'missing slide' objection (those come from gaps).
                tpl = _FINDING_OBJECTIONS.get(f.code)
                if tpl is None:
                    continue
                question, evidence = tpl
                if question in seen_q:
                    continue
                seen_q.add(question)
                objections.append(
                    Objection(
                        question=question,
                        slide_kind=s.kind,
                        resolving_evidence=evidence,
                        severity=f.severity,
                    )
                )

        # 2) Missing canonical slides -> objections.
        for g in gaps:
            tpl = _FINDING_OBJECTIONS.get(f"missing-{g.kind.value}")
            if tpl is None:
                continue
            question, evidence = tpl
            if question in seen_q:
                continue
            seen_q.add(question)
            objections.append(
                Objection(
                    question=question,
                    slide_kind=g.kind,
                    resolving_evidence=evidence,
                    severity="blocker",
                )
            )

        # 3) Inconsistency flags across slides.
        objections.extend(self._inconsistency_flags(per_slide, ctx, seen_q))

        # 4) Stage-appropriate baseline questions (ensure >= 5 substantive).
        for question, evidence, kind_str in _STAGE_BASELINES.get(ctx.stage, _STAGE_BASELINES[Stage.SEED]):
            if len(objections) >= 5 and question in seen_q:
                continue
            if question in seen_q:
                continue
            seen_q.add(question)
            objections.append(
                Objection(
                    question=question,
                    slide_kind=_KIND_FROM_STR.get(kind_str),
                    resolving_evidence=evidence,
                    severity="major",
                )
            )

        # Guarantee the gate: at least 5 objections.
        if len(objections) < 5:  # pragma: no cover - defensive
            objections.extend(self._generic_fallbacks(5 - len(objections), seen_q))

        return objections

    # ------------------------------------------------------------------
    def _inconsistency_flags(
        self,
        per_slide: list[SlideScore],
        ctx: Context,
        seen_q: set[str],
    ) -> list[Objection]:
        out: list[Objection] = []
        kinds = {s.kind: s for s in per_slide}
        # If TAM is top-down yet financials project rapid scale, the two
        # assumptions don't reconcile — flag the inconsistency.
        tam = kinds.get(SlideKind.MARKET_TAM)
        fin = kinds.get(SlideKind.FINANCIALS)
        if tam and tam.present and fin and fin.present:
            tam_topdown = any(f.code == "top-down-tam" for f in tam.findings)
            fin_inflated = any(f.code == "inflated-projection" for f in fin.findings)
            if tam_topdown or fin_inflated:
                q = (
                    "Your TAM is top-down yet your financials project rapid scale — "
                    "the two don't reconcile. Which assumption should we trust?"
                )
                if q not in seen_q:
                    seen_q.add(q)
                    out.append(
                        Objection(
                            question=q,
                            slide_kind=SlideKind.FINANCIALS,
                            resolving_evidence="Reconciled top-down vs bottom-up TAM with the financial build.",
                            severity="major",
                        )
                    )
        # Raise amount missing but ask slide present.
        ask = kinds.get(SlideKind.ASK)
        if ask and ask.present and ctx.raise_amount_usd is None:
            q = "The ask slide doesn't state a raise amount. How much are you raising?"
            if q not in seen_q:
                seen_q.add(q)
                out.append(
                    Objection(
                        question=q,
                        slide_kind=SlideKind.ASK,
                        resolving_evidence="A clear raise amount and use-of-funds breakdown.",
                        severity="major",
                    )
                )
        return out

    def _generic_fallbacks(self, n: int, seen_q: set[str]) -> list[Objection]:
        generics = [
            (
                "What is the one sentence that describes this company?",
                "A crisp one-liner value proposition.",
                "solution",
            ),
            ("Who is the ideal customer profile?", "A named ICP with segment size and access motion.", "gtm"),
            (
                "What is the biggest risk and how are you mitigating it?",
                "A stated risk plus a concrete mitigation.",
                "team",
            ),
            (
                "What are the key assumptions behind your numbers?",
                "The top 3-5 assumptions with sensitivity.",
                "financials",
            ),
            ("How do you acquire your first 100 customers?", "A specific channel and CAC estimate.", "gtm"),
        ]
        out = []
        for q, ev, kind in generics:
            if len(out) >= n:
                break
            if q in seen_q:
                continue
            seen_q.add(q)
            out.append(
                Objection(question=q, slide_kind=_KIND_FROM_STR.get(kind), resolving_evidence=ev, severity="major")
            )
        return out
