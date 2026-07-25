"""End-to-end pipeline tests covering the 6 documented test scenarios."""

import pytest
from decks import (
    inflated_financials_deck,
    missing_business_model_deck,
    pre_seed_angel_deck,
    strong_deck,
    vanity_traction_deck,
    weak_topdown_tam_deck,
)

from pitchdeck_scorer import Pipeline, run
from pitchdeck_scorer.models import SlideKind
from pitchdeck_scorer.requirements_gatherer import RequirementsError

PIPE = Pipeline()


def _run(deck, **ctx):
    return PIPE.run(deck, context_raw={"sector": "saas", **ctx})


# Scenario 1 — pre-seed deck for angels
def test_scenario1_pre_seed_angels():
    rep = _run(pre_seed_angel_deck(), stage="pre-seed", audience="angel", raise_amount="$500k")
    assert rep.stage.value == "pre-seed"
    assert rep.audience.value == "angel"
    assert rep.overall_score <= 100
    assert len(rep.objections) >= 5
    assert rep.roadmap


# Scenario 2 — top-down TAM challenge
def test_scenario2_topdown_tam():
    rep = _run(weak_topdown_tam_deck(), stage="seed", audience="seed-fund")
    qs = " ".join(o.question for o in rep.objections).lower()
    assert "bottom-up" in qs
    tam = next(s for s in rep.per_slide if s.kind == SlideKind.MARKET_TAM)
    assert any(f.code == "top-down-tam" for f in tam.findings)


# Scenario 3 — weak traction (vanity)
def test_scenario3_vanity_traction():
    rep = _run(vanity_traction_deck(), stage="seed", audience="seed-fund")
    assert any("revenue" in o.question.lower() or "retention" in o.question.lower() for o in rep.objections)
    assert any(f.code == "vanity-metrics" for s in rep.per_slide for f in s.findings)


# Scenario 4 — missing business model
def test_scenario4_missing_business_model():
    rep = _run(missing_business_model_deck(), stage="seed", audience="seed-fund")
    assert any(g.kind == SlideKind.BUSINESS_MODEL for g in rep.gaps)
    assert any("business" in o.question.lower() or "make money" in o.question.lower() for o in rep.objections)
    assert any(i.slide_kind == SlideKind.BUSINESS_MODEL for i in rep.roadmap)


# Scenario 5 — inflated financials
def test_scenario5_inflated_financials():
    rep = _run(inflated_financials_deck(), stage="seed", audience="seed-fund")
    assert any("assumption" in o.question.lower() for o in rep.objections)
    assert any(f.code == "inflated-projection" for s in rep.per_slide for f in s.findings)


# Scenario 6 — offline / degraded mode
def test_scenario6_offline_mode():
    rep = _run(strong_deck(), stage="seed", audience="seed-fund", raise_amount="$1.5M", online=False)
    assert rep.offline is True
    assert rep.sources  # brain-based or dated anchor citations present
    assert any("offline" in n.lower() for n in rep.notes)


def test_strong_deck_overall_fundable():
    rep = _run(strong_deck(), stage="seed", audience="seed-fund", raise_amount="$1.5M")
    assert rep.overall_score >= 75
    assert rep.fundability.value.startswith("Fundable")


def test_gate_blocks_without_stage_or_audience():
    with pytest.raises(RequirementsError):
        PIPE.run(strong_deck())  # no context -> gate fails


def test_run_function_accepts_dict_deck():
    deck_dict = {
        "company": "DictCo",
        "slides": [
            {
                "kind": "ask",
                "title": "Ask",
                "headline": "Raising $1.5M seed",
                "bullets": ["$1.5M seed", "Use of funds: engineering", "Milestone: $500k MRR", "18 months runway"],
            },
        ],
    }
    md = run(deck_dict, context={"stage": "seed", "sector": "saas", "audience": "seed-fund"}, fmt="markdown")
    assert "DictCo" in md


def test_every_objection_addressed_in_roadmap_e2e():
    rep = _run(strong_deck(), stage="seed", audience="seed-fund", raise_amount="$1.5M")
    addressed = {i.objection_addressed for i in rep.roadmap if i.objection_addressed}
    for o in rep.objections:
        assert o.question in addressed


def test_report_cited_and_dated_sources():
    rep = _run(strong_deck(), stage="seed", audience="seed-fund", raise_amount="$1.5M")
    assert rep.sources  # cited + dated gate
