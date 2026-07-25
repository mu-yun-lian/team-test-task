# startup-pitch-deck-scorer

> Slide-by-slide investor scoring of a startup pitch deck against named VC
> frameworks (Sequoia, Guy Kawasaki 10/20/30, YC essentials, bottom-up
> TAM/SAM/SOM), stress-tested with investor objections, with a slide-level fix
> roadmap.

[![Tests](https://img.shields.io/badge/tests-77%20passing-brightgreen)](#)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](#)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

`pitchdeck-scorer` scores each canonical pitch slide on **persuasion (40%)**,
**logic (35%)**, and **clarity (25%)**, flags missing canonical slides as
gaps, raises ≥5 investor devil's-advocate objections, and emits a
slide-level before → after fix roadmap. The scoring engine is deterministic,
offline-first, and fully testable; an optional LLM adapter is wired for
production narrative polish.

## Install

```bash
pip install -e .              # core
pip install -e ".[dev]"       # + pytest, ruff
pip install -e ".[llm]"       # + openai (optional narrative polish)
pip install -e ".[crawl]"     # + crawl4ai (optional knowledge_updater crawl)
```

## Quick start

### CLI

```bash
# deck.json: {"company": "...", "slides": [{"kind": "problem", "title": ..., "headline": ..., "bullets": [...]}]}
# context.json: {"stage": "seed", "sector": "saas", "raise_amount": "$1.5M", "audience": "seed-fund"}

pitchdeck-scorer --deck deck.json --context context.json --format markdown
pitchdeck-scorer --deck deck.json --context context.json --format json -o report.json
cat deck.json | pitchdeck-scorer --deck - --context context.json
```

### Library

```python
from pitchdeck_scorer import run, Pipeline
from pitchdeck_scorer.models import Deck, SlideContent, SlideKind

deck = Deck(company="Acme", slides=[
    SlideContent(kind=SlideKind.PROBLEM, title="Problem",
                 headline="SMBs lose 10 hrs/week reconciling invoices",
                 bullets=["Who: SMB finance teams", "Pain: manual reconciliation",
                          "Why now: AI can read invoices"]),
    SlideContent(kind=SlideKind.ASK, title="Ask", headline="Raising $1.5M seed",
                 bullets=["$1.5M seed", "Use of funds: engineering, sales",
                          "Reach $500k MRR", "18 months runway"]),
])

report = run(deck, context={"stage": "seed", "sector": "saas",
                            "raise_amount": "$1.5M", "audience": "seed-fund"},
             fmt="report")
print(report.overall_score, report.fundability.value)
print(run(deck, context={"stage": "seed", "sector": "saas",
                         "raise_amount": "$1.5M", "audience": "seed-fund"},
          fmt="markdown"))
```

## Harness flow

```
requirements_gatherer   → Context        (gate: stage + audience set)
research                → dated sources  (gate: cited + dated; offline-safe)
scoring_engine          → per-slide scores + gaps
quality_reviewer        → ≥ 5 objections (gate: each maps to a slide + evidence)
improvement_roadmap     → slide-level before → after rewrites (gate: every objection addressed)
synthesize              → ScoreReport (Markdown / JSON)
```

## Canonical slides (11)

Problem · Solution · Market/TAM · Product · Business Model · Traction ·
Go-to-Market · Competition · Team · Financials · Ask.

Missing canonical slides are flagged as gaps and get add-slide roadmap items.

## Scoring model

Per slide, per axis:

```
axis_score = 100 * (sum of weights of satisfied rubric elements on axis)
             / (sum of all weights on that axis)
```

then detector-driven penalties/bonuses (e.g. top-down TAM → logic −25, vanity
metrics → persuasion −25, hockey-stick financials → logic −28), clamped to
[0, 100]. Overall deck score is the slide-weighted mean minus gap penalties;
fundability bands: `Fundable as-is` / `Fundable with refinement` / `Needs
material rework` / `Not fundable`.

## Quality gates

- Stage + audience captured (requirements gate).
- Every present slide scored on persuasion/logic/clarity; missing slides flagged.
- ≥ 5 investor objections, each mapped to a slide and resolving evidence.
- Roadmap items slide-specific with before/after + effort/impact; every
  objection addressed.
- Sources cited and dated; offline limitation flagged when live research is
  unavailable.

## Knowledge pipeline

`tools/knowledge_updater.py` grows `SECOND-KNOWLEDGE-BRAIN.md` with
deduplicated, dated entries crawled from public VC / entrepreneurial-finance
sources (Sequoia, YC, First Round, a16z, SSRN). Run weekly:

```bash
python tools/knowledge_updater.py --dry-run --limit 40
python tools/knowledge_updater.py            # appends
python tools/knowledge_updater.py --json     # print candidates, no write
```

## Online research

Live web research is **opt-in**. By default the harness runs offline using
`SECOND-KNOWLEDGE-BRAIN.md` and dated benchmark anchors (deterministic &
reproducible). Enable it with `PITCHDECK_ONLINE=1` or `--online`.

## Optional LLM polish

If `OPENAI_API_KEY` is set and the `openai` package is installed, pass
`--polish` (or `Pipeline.render(..., polish=True)`) to generate an
LLM-written executive summary. The LLM **never** changes scored numbers — it
only rewrites prose. Without the LLM, a deterministic summary is used.

## Project layout

```
pitchdeck_scorer/        # the Python package
  models.py              # typed contracts (pydantic)
  canonical.py           # 11-slide canon + title mapping
  frameworks.py          # VC frameworks + rubrics + detectors
  requirements_gatherer.py
  scoring_engine.py
  quality_reviewer.py
  improvement_roadmap.py
  research.py            # online/offline research adapter
  knowledge.py           # SECOND-KNOWLEDGE-BRAIN reader
  llm.py                 # optional LLM adapter
  report.py              # Markdown / JSON rendering
  pipeline.py            # harness orchestration
  cli.py / __main__.py   # CLI
tools/knowledge_updater.py
skills/*.md              # agent-facing sub-skill prompts (CLAUDE skill format)
tests/                   # 77 tests incl. the 6 documented scenarios
SECOND-KNOWLEDGE-BRAIN.md
```

## Testing

```bash
pip install -e ".[dev]"
pytest -q
ruff check .
```

## Design decisions

1. Score on persuasion + logic + clarity per slide (40/35/25).
2. Investor-objection pass is mandatory (≥ 5).
3. TAM must be bottom-up-defensible; top-down is penalized.
4. Missing canonical slides are flagged as gaps.
5. Benchmarks are dated by sector; offline runs are explicitly flagged.
6. The core is deterministic and offline-first so results are reproducible;
   LLM augmentation is opt-in and never touches the numbers.

## License

MIT — see [LICENSE](LICENSE).