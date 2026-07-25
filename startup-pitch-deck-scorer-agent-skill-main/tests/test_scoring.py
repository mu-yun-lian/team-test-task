from decks import (
    inflated_financials_deck,
    missing_business_model_deck,
    strong_deck,
    vanity_traction_deck,
    weak_topdown_tam_deck,
)

from pitchdeck_scorer.models import Context, Deck, SlideKind, Stage, TargetAudience
from pitchdeck_scorer.scoring_engine import CRITICAL_SLIDES, ScoringEngine

ENGINE = ScoringEngine()
CTX = Context(stage=Stage.SEED, sector="saas", audience=TargetAudience.SEED_FUND, company="x")


def test_every_present_slide_scored_on_three_axes():
    per_slide, gaps = ENGINE.score(strong_deck(), CTX)
    present = [s for s in per_slide if s.present]
    assert len(present) == 11  # strong deck has all canonical slides
    for s in present:
        assert 0 <= s.axes.persuasion <= 100
        assert 0 <= s.axes.logic <= 100
        assert 0 <= s.axes.clarity <= 100
        assert s.weighted == round(s.axes.weighted, 1)


def test_missing_canonical_slides_flagged_as_gaps():
    per_slide, gaps = ENGINE.score(missing_business_model_deck(), CTX)
    kinds = {g.kind for g in gaps}
    assert SlideKind.BUSINESS_MODEL in kinds
    assert SlideKind.ASK in kinds
    missing_scores = [s for s in per_slide if not s.present]
    for s in missing_scores:
        assert any(f.severity == "blocker" for f in s.findings)


def test_top_down_tam_gets_logic_penalty():
    per_slide, _ = ENGINE.score(weak_topdown_tam_deck(), CTX)
    tam = next(s for s in per_slide if s.kind == SlideKind.MARKET_TAM)
    assert any(f.code == "top-down-tam" and f.severity == "major" for f in tam.findings)
    assert tam.axes.logic < 50


def test_vanity_metrics_gets_persuasion_penalty():
    per_slide, _ = ENGINE.score(vanity_traction_deck(), CTX)
    trac = next(s for s in per_slide if s.kind == SlideKind.TRACTION)
    assert any(f.code == "vanity-metrics" for f in trac.findings)
    assert trac.axes.persuasion < 40


def test_inflated_financials_gets_logic_penalty():
    per_slide, _ = ENGINE.score(inflated_financials_deck(), CTX)
    fin = next(s for s in per_slide if s.kind == SlideKind.FINANCIALS)
    assert any(f.code == "inflated-projection" for f in fin.findings)
    assert fin.axes.logic < 30


def test_strong_deck_scores_high_and_fundable():
    per_slide, gaps = ENGINE.score(strong_deck(), CTX)
    overall, band = ScoringEngine.overall(per_slide, gaps, CTX)
    assert overall >= 75
    assert band.value.startswith("Fundable")


def test_overall_zero_when_all_missing():
    deck = Deck(company="x", slides=[])
    per_slide, gaps = ENGINE.score(deck, CTX)
    overall, band = ScoringEngine.overall(per_slide, gaps, CTX)
    assert overall == 0.0
    assert band.value.startswith("Not fundable")


def test_critical_slides_set():
    assert SlideKind.PROBLEM in CRITICAL_SLIDES
    assert SlideKind.TRACTION in CRITICAL_SLIDES
