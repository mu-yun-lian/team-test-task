# PROJECT-DEVELOPMENT-PHASE-TRACKING.md — Startup Pitch Deck Builder & Scorer (Idea 57)

> Overall status: **Phases 0–5 are 100% complete.** Production-grade Python
> package `pitchdeck_scorer` implemented (deterministic, offline-first, fully
> tested, open-source ready). 77 tests pass; `ruff check` clean. No git/model
> flows executed during preparation (code is ready for real production runs).

Legend: `[x]` done · `[ ]` not started. All items below are `[x]`.

---

## Phase 0 — Research & Architecture  ✅ 100%
- [x] Catalog VC frameworks: Sequoia deck template, Guy Kawasaki 10/20/30, YC essentials, TAM/SAM/SOM.
- [x] Define canonical 11-slide set (Problem, Solution, Market/TAM, Product, Business model, Traction, GTM, Competition, Team, Financials, Ask).
- [x] Define 3 scoring axes + weights (Persuasion 40% / Logic 35% / Clarity 25%).
- [x] Define per-slide rubrics (required elements per slide) and detector signals.
- **Deliverables:** framework + slide canon + rubrics in `SECOND-KNOWLEDGE-BRAIN.md`; code in `pitchdeck_scorer/frameworks.py` and `pitchdeck_scorer/canonical.py`.
- **Success:** ≥ 3 frameworks + 11-slide canon documented; rubric element weights sum to 1.0 per slide. Effort: S. **Status: ✅ Done**
- **Tests:** `tests/test_frameworks.py`, `tests/test_canonical.py`.

## Phase 1 — Core Sub-Skills  ✅ 100%
- [x] `sub-requirements-gatherer` — capture/validate stage, sector, raise, audience; gate blocks if stage/audience unknown; infer from Ask slide.
- [x] `sub-scoring-engine` — per-slide persuasion/logic/clarity scores; missing-slide gaps; overall score + fundability band; detector penalties (top-down TAM, vanity, hockey-stick, no-moat).
- [x] `sub-improvement-roadmap` — slide-level before → after rewrites + missing-slide outlines; effort/impact tags; every objection addressed.
- [x] Typed contracts (pydantic models) flowing between sub-skills.
- **Deliverables:** `requirements_gatherer.py`, `scoring_engine.py`, `improvement_roadmap.py`, `models.py`.
- **Success:** deck → score → roadmap flows. Effort: M. **Status: ✅ Done**
- **Tests:** `tests/test_requirements.py`, `tests/test_scoring.py`, `tests/test_roadmap.py`, `tests/test_models.py`.

## Phase 2 — Main Harness + Quality Gates  ✅ 100%
- [x] `main.md` harness definition + `pipeline.Pipeline` orchestration (gather → research → score → review → roadmap → synthesize).
- [x] `sub-quality-reviewer` — investor devil's-advocate pass; ≥ 5 objections; each mapped to a slide + resolving evidence; inconsistency flags; stage-appropriate baselines.
- [x] All quality gates enforced (requirements gate, ≥ 5 objections, every objection addressed, cited+dated sources, offline flag).
- **Deliverables:** `skills/main.md`, `pipeline.py`, `quality_reviewer.py`, `report.py`.
- **Success:** E2E raises ≥ 5 objections; all gates pass. Effort: M. **Status: ✅ Done**
- **Tests:** `tests/test_reviewer.py`, `tests/test_pipeline.py`, `tests/test_report.py`.

## Phase 3 — Knowledge Pipeline  ✅ 100%
- [x] `tools/knowledge_updater.py` — crawl Sequoia/YC/a16z/First Round/SSRN; score by recency + relevance; dedupe by hash; append dated `### Auto-update YYYY-MM-DD` block.
- [x] Production-grade: httpx + BeautifulSoup parsing with crawl4ai fallback; `--dry-run`, `--json`, `--sources`, `--limit`, `--offline`; structured logging; graceful degradation.
- [x] `pitchdeck_scorer/knowledge.py` brain reader (entries, citations, framework summary) + `research.py` offline-safe research adapter.
- **Deliverables:** `tools/knowledge_updater.py`, `knowledge.py`, `research.py`, `SECOND-KNOWLEDGE-BRAIN.md` (seeded + dated entries).
- **Success:** dry-run appends deduped entries; offline path produces dated citations. Effort: M. **Status: ✅ Done**
- **Tests:** `tests/test_knowledge.py`. (Live network is opt-in via `PITCHDECK_ONLINE`/`--online`; not run during preparation.)

## Phase 4 — Testing & Validation  ✅ 100%
- [x] 6 scenarios incl. TAM challenge + inflated financials, implemented as pytest cases.
- [x] Unit tests for models, canonical mapping, frameworks/detectors, requirements, scoring, reviewer, roadmap, knowledge, report, deck loader.
- [x] CLI tests (markdown, json, stdin, missing-file).
- [x] E2E pipeline tests asserting all gates (≥ 5 objections, every objection addressed, gaps flagged, offline flag).
- **Deliverables:** `tests/` (conftest, decks, fixtures, 11 test modules).
- **Success:** all gated — 77 tests pass; `ruff check` clean. Effort: S. **Status: ✅ Done**
- **Tests:** `pytest -q` → 77 passed.

## Phase 5 — Cross-Skill Wiring  ✅ 100%
- [x] Document reuse contracts for sub-requirements-gatherer / sub-scoring-engine / sub-quality-reviewer with sibling skills (63, 67, 76, 96, 107, 147).
- [x] Stable, importable contracts (`Context`, `Deck`, `SlideContent`, `SlideScore`, `Objection`, `RoadmapItem`, `ScoreReport`) and a `Pipeline.run(...)` / `run(...)` entry point.
- [x] CLI + library + JSON contract for programmatic reuse.
- **Deliverables:** reuse notes (below), public API in `pitchdeck_scorer/__init__.py`, `README.md` project layout.
- **Success:** shared contracts documented and importable. Effort: S. **Status: ✅ Done**

### Cross-skill reuse notes
- `pitchdeck_scorer.requirements_gatherer.RequirementsGatherer` — reusable context capture for any business-evaluation skill (63/67/76/96/107/147).
- `pitchdeck_scorer.scoring_engine.ScoringEngine` — reusable per-slide/per-axis scoring rubric (swap `RUBRICS` for another domain).
- `pitchdeck_scorer.quality_reviewer.QualityReviewer` — reusable devil's-advocate objection generator.
- Shared typed contracts in `pitchdeck_scorer.models` keep integrations stable; `ScoreReport` JSON is the wire format.

---

## Production-readiness checklist (all phases)
- [x] Deterministic, offline-first core (reproducible).
- [x] Optional LLM adapter (`llm.py`) — opt-in, never changes scored numbers.
- [x] Optional online research — opt-in via `PITCHDECK_ONLINE` / `--online`.
- [x] UTF-8 safe CLI output (Windows codepage safe).
- [x] `pyproject.toml`, `requirements.txt`, `LICENSE` (MIT), `README.md`, `.gitignore`.
- [x] 77 passing tests; `ruff check` clean.
- [x] No git flows executed; no real model pull/train/run executed during preparation — code is ready for real production runs.