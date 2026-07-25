# PROJECT-detail.md — Startup Pitch Deck Builder & Scorer (Idea 57)

## Executive Summary
A harness that scores a startup pitch deck slide-by-slide on persuasion, logic, and clarity against named VC frameworks, stress-tests it with investor objections, and emits a slide-level fix roadmap. Implemented as the production Python package `pitchdeck_scorer`.

## Problem Statement
Decks bury the story, lack proof, and don't answer the questions investors actually ask. This skill provides objective, framework-grounded feedback.

## Target Users & Use Cases
- **Pre-seed founder:** "Score my deck for angels" → slide scores + fixes.
- **Seed/Series A:** "Is my traction slide credible?" → metric-credibility critique.
- **Accelerator coach:** batch deck review against a rubric.

## Harness Architecture
```
/startup-pitch-deck-scorer
  → sub-requirements-gatherer  (stage, sector, raise, audience)  [gate: stage + audience set]
  → [main] research            (current investor expectations)   [gate: cited + dated; offline-safe]
  → sub-scoring-engine         (per-slide scores + gaps)         [gate: each slide 3 axes]
  → sub-quality-reviewer       (investor objections)             [gate: ≥ 5 tough questions]
  → sub-improvement-roadmap    (slide-level rewrites)            [gate: each slide actionable; every objection addressed]
  → [main] synthesize          (Markdown / JSON report)
```

## Full Sub-Skill Catalog
| Sub-skill | Purpose | Inputs | Outputs | Tools | Gate |
|-----------|---------|--------|---------|-------|------|
| sub-requirements-gatherer | Context | deck, stage, sector | Context | Read | Stage + audience set |
| sub-scoring-engine | Score slides | deck, frameworks | per-slide scores + gaps | Read | Each slide on 3 axes |
| sub-quality-reviewer | Investor objections | deck, scores, gaps | objection list | Read | ≥ 5 tough questions |
| sub-improvement-roadmap | Fix plan | scores, objections, gaps | slide rewrites | Write | Each slide actionable; every objection addressed |

## E2E Execution Flow
1. Gather stage (pre-seed/seed/A), sector, raise amount, audience type (or infer from the Ask slide).
2. Research current investor expectations & benchmarks (sector CAC/LTV, NRR, growth norms); offline → brain + flag.
3. Score each canonical slide on persuasion/logic/clarity; flag missing canonical slides as gaps.
4. Quality reviewer raises ≥ 5 investor objections (TAM basis, unit economics, moat, team gaps, use-of-funds).
5. Roadmap gives slide-level before → after rewrites + missing-slide additions; every objection addressed.
6. Render Markdown/JSON.

Error handling: missing critical slide → flag as gap; unrealistic TAM/financials → challenge; offline → use brain + flag.

## SECOND-KNOWLEDGE-BRAIN Integration
Sources: Sequoia/YC/a16z/First Round, SSRN, teardown libraries. Weekly append via `tools/knowledge_updater.py`; dedupe by hash.

## Supporting Tools Spec
- `pitchdeck_scorer/` package: `models`, `canonical`, `frameworks`, `requirements_gatherer`, `scoring_engine`, `quality_reviewer`, `improvement_roadmap`, `research`, `knowledge`, `llm`, `report`, `pipeline`, `cli`.
- `tools/knowledge_updater.py`: queries pitch/VC trends & benchmarks; weekly cron; dedupe by hash; `--dry-run`, `--json`, `--sources`, `--limit`.

## Quality Gates
- Every present slide scored on persuasion/logic/clarity.
- Missing canonical slides flagged as gaps.
- ≥ 5 investor objections raised; each mapped to a slide + resolving evidence.
- Roadmap items slide-specific with before/after + effort/impact; every objection addressed.
- Benchmarks dated by sector; offline flagged.

## Test Scenarios (summary)
1. Pre-seed deck for angels. 2. Top-down TAM challenge. 3. Weak traction slide (vanity). 4. Missing business-model slide. 5. Inflated financials. 6. Offline / degraded mode. (Full set in `tests/test-scenarios.md` and `tests/test_pipeline.py`.)

## Key Design Decisions
1. Score on persuasion+logic+clarity per slide (40/35/25).
2. Investor-objection pass mandatory (≥ 5).
3. TAM must be bottom-up-defensible.
4. Missing slides flagged as gaps.
5. Benchmarks dated by sector.
6. Deterministic, offline-first core; LLM augmentation opt-in and never touches the numbers.