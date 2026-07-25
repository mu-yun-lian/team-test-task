from decks import (
    inflated_financials_deck,
    missing_business_model_deck,
    strong_deck,
    vanity_traction_deck,
    weak_topdown_tam_deck,
)

from pitchdeck_scorer.models import Context, Stage, TargetAudience
from pitchdeck_scorer.quality_reviewer import QualityReviewer
from pitchdeck_scorer.scoring_engine import ScoringEngine

SCORER = ScoringEngine()
REVIEWER = QualityReviewer()
CTX = Context(stage=Stage.SEED, sector="saas", audience=TargetAudience.SEED_FUND, company="x")


def test_at_least_five_substantive_objections_always():
    for deck in (
        strong_deck(),
        weak_topdown_tam_deck(),
        vanity_traction_deck(),
        missing_business_model_deck(),
        inflated_financials_deck(),
    ):
        per_slide, gaps = SCORER.score(deck, CTX)
        objs = REVIEWER.review(per_slide, gaps, CTX)
        assert len(objs) >= 5, f"expected >=5 objections, got {len(objs)}"


def test_each_objection_has_resolving_evidence():
    per_slide, gaps = SCORER.score(missing_business_model_deck(), CTX)
    objs = REVIEWER.review(per_slide, gaps, CTX)
    for o in objs:
        assert o.question
        assert o.resolving_evidence


def test_topdown_tam_raises_objection_demanding_bottomup():
    per_slide, gaps = SCORER.score(weak_topdown_tam_deck(), CTX)
    objs = REVIEWER.review(per_slide, gaps, CTX)
    qs = " ".join(o.question for o in objs).lower()
    assert "bottom-up" in qs


def test_vanity_traction_raises_objection():
    per_slide, gaps = SCORER.score(vanity_traction_deck(), CTX)
    objs = REVIEWER.review(per_slide, gaps, CTX)
    assert any("revenue" in o.question.lower() or "retention" in o.question.lower() for o in objs)


def test_missing_business_model_raises_objection():
    per_slide, gaps = SCORER.score(missing_business_model_deck(), CTX)
    objs = REVIEWER.review(per_slide, gaps, CTX)
    assert any("business" in o.question.lower() or "make money" in o.question.lower() for o in objs)


def test_inflated_financials_raises_objection():
    per_slide, gaps = SCORER.score(inflated_financials_deck(), CTX)
    objs = REVIEWER.review(per_slide, gaps, CTX)
    assert any("assumption" in o.question.lower() or "hockey" in o.question.lower() for o in objs)


def test_objections_mapped_to_slide_kind():
    per_slide, gaps = SCORER.score(strong_deck(), CTX)
    objs = REVIEWER.review(per_slide, gaps, CTX)
    # Most objections should map to a slide kind.
    mapped = [o for o in objs if o.slide_kind is not None]
    assert len(mapped) >= 5
