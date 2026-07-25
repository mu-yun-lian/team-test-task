---
name: sub-quality-reviewer
description: Investor devil's-advocate pass — raises the tough questions a partner meeting would, before the deck is finalized.
---

## Purpose
Stress-test the deck so the founder isn't blindsided in a real pitch.

## Inputs
Deck + per-slide scores + gaps + context.

## Process
1. Convert each major/blocker finding into an objection (e.g. top-down TAM → "show the bottom-up TAM and the #customers × ACV math").
2. Convert each missing canonical slide into a blocker objection.
3. Raise cross-slide inconsistency objections (e.g. top-down TAM + rapid financial scale don't reconcile; missing raise amount).
4. Add stage-appropriate baseline objections (pre-seed: discovery, MVP, why-this-team; seed: CAC/payback, retention, moat; Series A: repeatable GTM, NRR, path to $10–20M ARR; growth: LTV/CAC, path to profitability, moat at scale).
5. Guarantee **≥ 5** substantive objections; each maps to a slide and to the evidence that would resolve it.

## Outputs
Objection list (question → slide → resolving evidence) + inconsistency flags.

## Quality Gate
- ≥ 5 substantive objections raised.
- Each maps to a slide and a resolving evidence ask.

## Implementation
`pitchdeck_scorer.quality_reviewer.QualityReviewer.review(per_slide, gaps, ctx)`
→ `list[Objection]`.