---
name: sub-scoring-engine
description: Score each canonical pitch slide on persuasion, logic, and clarity, and flag missing slides.
---

## Purpose
Produce per-slide scores against the canonical 11-slide set and named VC frameworks, plus an overall deck score and fundability band.

## Inputs
Deck slides, context (stage/sector/audience).

## Canonical Slides
Problem, Solution, Market/TAM, Product, Business model, Traction, GTM, Competition, Team, Financials, Ask.

## Scoring Axes & Weights
Persuasion 40% · Logic 35% · Clarity 25%.

## Process
1. Map deck slides to the canonical set (title heuristics when kind is unset); flag any missing as gaps.
2. For each present slide, check each rubric element (see SECOND-KNOWLEDGE-BRAIN.md rubric summary); axis score = 100 × (satisfied weight / total weight on that axis).
3. Apply detector-driven penalties: top-down TAM (logic −25), vanity metrics (persuasion −25), hockey-stick financials (logic −28), no moat (logic −8); apply bonuses for bottom-up TAM / retention / realistic projections.
4. Apply structural clarity adjustments (missing headline, too few/many bullets).
5. Weighted slide score → overall deck score (slide-weighted mean minus gap penalties) → fundability band.

## Outputs
Per-slide score table (axes + weighted + findings) + gaps + overall score + band.

## Quality Gate
- Every present slide scored on all 3 axes.
- Missing canonical slides explicitly flagged as blockers.

## Implementation
`pitchdeck_scorer.scoring_engine.ScoringEngine.score(deck, ctx)` →
`(list[SlideScore], list[Gap])`; `ScoringEngine.overall(...)` →
`(overall: float, FundabilityBand)`. Rubrics live in
`pitchdeck_scorer.frameworks.RUBRICS`; detectors in
`pitchdeck_scorer.frameworks` (top-down TAM, vanity metrics, inflated
projections, moat, unit economics, etc.).