---
name: sub-requirements-gatherer
description: Capture startup stage, sector, raise amount, and target investor audience before scoring a deck.
---

## Purpose
Set the context that calibrates investor expectations and benchmarks. This is the first gate of the harness — scoring is blocked until stage and audience are set.

## Inputs
Deck content, funding stage, sector, raise amount/use of funds, target audience (angel / pre-seed fund / seed fund / Series A fund / growth equity).

## Process
1. Confirm stage and audience — expectations differ sharply (traction matters more at Series A; team & why-now matter more at pre-seed).
2. Record sector for benchmark selection (CAC/LTV, NRR, growth norms).
3. Capture the ask and intended use of funds.
4. If stage/audience are not provided explicitly, infer them from the Ask slide (amount, "seed"/"angel" cues).
5. **Block if stage or audience is still unknown** — raise `RequirementsError`.

## Outputs
Context `{stage, sector, raise_amount_usd, use_of_funds, audience, company}`.

## Quality Gate
- Stage + audience explicitly set (or inferred from the Ask slide).

## Implementation
`pitchdeck_scorer.requirements_gatherer.RequirementsGatherer.gather(deck, ...)` →
`pitchdeck_scorer.models.Context`. Money strings like "$1.5M" are parsed to
USD; stage/audience aliases are normalized (e.g. "pre-seed fund" →
`Stage.PRE_SEED` / `TargetAudience.PRE_SEED_FUND`).