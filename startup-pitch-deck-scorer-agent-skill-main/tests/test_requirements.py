import pytest

from pitchdeck_scorer.models import Deck, SlideContent, SlideKind, Stage, TargetAudience
from pitchdeck_scorer.requirements_gatherer import RequirementsError, RequirementsGatherer


def _gatherer():
    return RequirementsGatherer()


def test_gate_blocks_when_stage_and_audience_missing():
    deck = Deck(company="x", slides=[])
    with pytest.raises(RequirementsError):
        _gatherer().gather(deck)


def test_gate_blocks_when_only_stage_known():
    deck = Deck(company="x", slides=[])
    with pytest.raises(RequirementsError):
        _gatherer().gather(deck, stage="seed", audience=None)


def test_parses_money_and_normalizes_aliases():
    deck = Deck(company="x", slides=[])
    ctx = _gatherer().gather(
        deck, stage="pre-seed", sector="saas", raise_amount="$1.5M", audience="seed fund", use_of_funds="engineering"
    )
    assert ctx.stage == Stage.PRE_SEED
    assert ctx.audience == TargetAudience.SEED_FUND
    assert ctx.raise_amount_usd == 1_500_000
    assert ctx.use_of_funds == "engineering"
    assert ctx.sector == "saas"


def test_infer_stage_and_audience_from_ask_slide():
    ask = SlideContent(
        kind=SlideKind.ASK,
        title="Ask",
        headline="Raising $500k from angels",
        bullets=["$500k pre-seed from angels", "Use of funds: engineering"],
    )
    deck = Deck(company="AngelCo", slides=[ask])
    ctx = _gatherer().gather(deck)
    assert ctx.stage == Stage.PRE_SEED
    assert ctx.audience == TargetAudience.ANGEL
    assert ctx.raise_amount_usd == 500_000


def test_unknown_stage_value_raises():
    deck = Deck(company="x", slides=[])
    with pytest.raises(RequirementsError):
        _gatherer().gather(deck, stage="mezzanine", audience="angel")
