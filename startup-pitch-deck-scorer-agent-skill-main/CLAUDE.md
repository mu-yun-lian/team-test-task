# CLAUDE.md — Startup Pitch Deck Builder & Scorer Skill (Idea 57)

**Skill name:** `startup-pitch-deck-scorer`
**Tagline:** Slide-by-slide investor scoring of a pitch deck against VC frameworks, with a fix roadmap.
**Status:** Phases 0–5 complete. Production-grade Python package `pitchdeck_scorer` implemented (deterministic, offline-first, fully tested). Open-source ready.
**Source idea:** 57 — *Build & evaluate a startup pitch deck / fundraising materials, scoring each slide on persuasion, logic and clarity, grounded in world-renowned investment & evaluation methods, with improvement recommendations; continuously crawl papers/docs to stay current.*
**Cluster:** `business-operations`

## Problem This Skill Solves
Founders build decks that fail to answer investor questions. This skill scores each slide against named VC frameworks (Sequoia template, Guy Kawasaki 10/20/30, YC essentials, problem-solution-market-traction-team logic), and emits a slide-level fix roadmap.

## Harness Flow Summary
1. **Requirements** (`sub-requirements-gatherer`) — stage, sector, raise amount, audience (angel/seed/Series A). Gate: stage + audience set.
2. **Research** (main) — verify current investor expectations vs SECOND-KNOWLEDGE-BRAIN.md. Gate: cited + dated; offline-safe.
3. **Scoring** (`sub-scoring-engine`) — per-slide persuasion/logic/clarity scores + gaps.
4. **Challenge** (`sub-quality-reviewer`) — investor devil's-advocate questions. Gate: ≥ 5 objections.
5. **Roadmap** (`sub-improvement-roadmap`) — slide-level rewrite plan. Gate: every objection addressed.
6. **Synthesize** — Markdown/JSON report.

## Sub-skills
- `sub-requirements-gatherer.md` · `sub-scoring-engine.md` · `sub-quality-reviewer.md` · `sub-improvement-roadmap.md`

## Tools Required
WebSearch, WebFetch, Read, Write, Bash.

## Knowledge Sources
Sequoia/YC/a16z/First Round public guidance, SSRN entrepreneurial-finance, pitch-deck teardown libraries, venture benchmark reports.

## Supporting Python Tools
- `pitchdeck_scorer/` — the production package (models, scoring engine, pipeline, CLI).
- `tools/knowledge_updater.py` — crawl → SECOND-KNOWLEDGE-BRAIN.md.

## Active Development Tasks
- [x] Scaffold deliverables.
- [x] Sector-specific metric benchmarks (dated anchors in SECOND-KNOWLEDGE-BRAIN.md).
- [x] Production Python implementation + test-suite (77 tests).

## Reference Docs
PROJECT-detail.md · PROJECT-DEVELOPMENT-PHASE-TRACKING.md · SECOND-KNOWLEDGE-BRAIN.md · README.md