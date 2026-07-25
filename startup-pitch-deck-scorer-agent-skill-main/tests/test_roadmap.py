from decks import (
    inflated_financials_deck,
    missing_business_model_deck,
    strong_deck,
    vanity_traction_deck,
    weak_topdown_tam_deck,
)

from pitchdeck_scorer.improvement_roadmap import ImprovementRoadmap
from pitchdeck_scorer.models import Context, Stage, TargetAudience
from pitchdeck_scorer.quality_reviewer import QualityReviewer
from pitchdeck_scorer.scoring_engine import ScoringEngine

SCORER = ScoringEngine()
REVIEWER = QualityReviewer()
ROADMAP = ImprovementRoadmap()
CTX = Context(stage=Stage.SEED, sector="saas", audience=TargetAudience.SEED_FUND, company="x")


def test_missing_slide_yields_add_slide_roadmap_item():
    per_slide, gaps = SCORER.score(missing_business_model_deck(), CTX)
    objs = REVIEWER.review(per_slide, gaps, CTX)
    items = ROADMAP.build(per_slide, gaps, objs, CTX)
    bm_items = [i for i in items if i.slide_kind.value == "business-model"]
    assert bm_items
    assert bm_items[0].before.startswith("(missing)")


def test_every_objection_addressed_by_roadmap():
    for deck in (
        strong_deck(),
        weak_topdown_tam_deck(),
        vanity_traction_deck(),
        missing_business_model_deck(),
        inflated_financials_deck(),
    ):
        per_slide, gaps = SCORER.score(deck, CTX)
        objs = REVIEWER.review(per_slide, gaps, CTX)
        items = ROADMAP.build(per_slide, gaps, objs, CTX)
        addressed = {i.objection_addressed for i in items if i.objection_addressed}
        for o in objs:
            assert o.question in addressed, f"Objection not addressed: {o.question}"


def test_roadmap_items_have_before_after_and_tags():
    per_slide, gaps = SCORER.score(weak_topdown_tam_deck(), CTX)
    objs = REVIEWER.review(per_slide, gaps, CTX)
    items = ROADMAP.build(per_slide, gaps, objs, CTX)
    assert items
    for it in items:
        assert it.before
        assert it.after
        assert it.effort in ("S", "M", "L")
        assert it.impact in ("Low", "Med", "High")


def test_topdown_tam_roadmap_rewrites_to_bottomup():
    per_slide, gaps = SCORER.score(weak_topdown_tam_deck(), CTX)
    objs = REVIEWER.review(per_slide, gaps, CTX)
    items = ROADMAP.build(per_slide, gaps, objs, CTX)
    tam_items = [i for i in items if i.slide_kind.value == "market-tam"]
    assert tam_items
    assert "bottom-up" in tam_items[0].after.lower()
