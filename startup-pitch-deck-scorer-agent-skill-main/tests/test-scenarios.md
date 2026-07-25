# Test Scenarios — Startup Pitch Deck Builder & Scorer (Idea 57)

Each scenario is implemented as a pytest case in `tests/test_pipeline.py` (and
supported by unit tests in `tests/test_*.py`). Fixtures live in `tests/decks.py`.

## Scenario 1 — Pre-seed deck for angels
- **Input:** 10-slide SaaS deck, pre-seed, raising $500k from angels.
- **Expected:** per-slide persuasion/logic/clarity scores, fundability verdict, ≥ 5 objections, fix roadmap.
- **Pass:** all present slides scored; objections raised; benchmark dates cited.
- **Test:** `test_scenario1_pre_seed_angels`, `test_models`, `test_scoring`.

## Scenario 2 — Top-down TAM challenge
- **Input:** market slide claims "1% of $50B market".
- **Expected:** logic penalty; objection demanding bottom-up sizing; roadmap rewrites to bottom-up.
- **Pass:** top-down TAM flagged; bottom-up requested.
- **Test:** `test_scenario2_topdown_tam`, `test_frameworks::test_top_down_tam_detector`.

## Scenario 3 — Weak traction slide
- **Input:** vanity metrics (signups) with no revenue/retention ("no revenue yet").
- **Expected:** traction credibility critique; request for retention/revenue; lower persuasion score.
- **Pass:** vanity metrics flagged; better metrics suggested.
- **Test:** `test_scenario3_vanity_traction`, `test_frameworks::test_vanity_metrics_detector`, `test_negated_revenue_not_counted`.

## Scenario 4 — Missing business-model slide
- **Input:** deck has no monetization slide.
- **Expected:** gap flagged; roadmap adds business-model slide with outline.
- **Pass:** missing canonical slide flagged and added.
- **Test:** `test_scenario4_missing_business_model`, `test_scoring::test_missing_canonical_slides_flagged_as_gaps`.

## Scenario 5 — Inflated financials
- **Input:** hockey-stick projection to $100M ARR in 2 years with no basis.
- **Expected:** logic challenge; assumptions requested; realistic re-baselining.
- **Pass:** unrealistic projection challenged.
- **Test:** `test_scenario5_inflated_financials`, `test_frameworks::test_inflated_projection_detector`.

## Scenario 6 — Offline / degraded mode
- **Input:** any deck with WebSearch unavailable.
- **Expected:** uses SECOND-KNOWLEDGE-BRAIN.md; flags benchmark-currency limitation.
- **Pass:** offline limitation stated; sources still cited from the brain.
- **Test:** `test_scenario6_offline_mode`, `test_knowledge`.

## Coverage
- Gates: requirements gate (`test_gate_blocks_*`), ≥ 5 objections (`test_at_least_five_substantive_objections_always`), every objection addressed (`test_every_objection_addressed_*`).
- CLI: `tests/test_cli.py` (markdown, json, stdin, missing-file).
- 77 tests total; run `pytest -q`.