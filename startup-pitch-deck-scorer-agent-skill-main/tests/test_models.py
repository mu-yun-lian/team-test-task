import pytest
from pydantic import ValidationError

from pitchdeck_scorer.models import (
    AxisScore,
    Context,
    FundabilityBand,
    ScoreReport,
    ScoringWeights,
    SlideKind,
    Stage,
    TargetAudience,
)


def test_axis_weighted_uses_40_35_25():
    a = AxisScore(persuasion=80, logic=60, clarity=40)
    assert a.weighted == pytest.approx(80 * 0.4 + 60 * 0.35 + 40 * 0.25)


def test_scoring_weights_must_sum_to_one():
    with pytest.raises(ValidationError):
        ScoringWeights(persuasion=0.5, logic=0.5, clarity=0.5)


def test_context_raise_label():
    assert (
        Context(stage=Stage.SEED, audience=TargetAudience.SEED_FUND, raise_amount_usd=1_500_000).raise_label == "$1.5M"
    )
    assert Context(stage=Stage.PRE_SEED, audience=TargetAudience.ANGEL, raise_amount_usd=500_000).raise_label == "$500k"
    assert Context(stage=Stage.SEED, audience=TargetAudience.SEED_FUND).raise_label == "undisclosed"


def test_slidekind_str_enum_values():
    assert SlideKind.MARKET_TAM.value == "market-tam"
    assert str(SlideKind.PROBLEM) == "problem"


def test_report_overall_range_enforced():
    with pytest.raises(ValidationError):
        ScoreReport(
            company="x",
            stage=Stage.SEED,
            audience=TargetAudience.SEED_FUND,
            overall_score=150.0,
            fundability=FundabilityBand.PASS,
            per_slide=[],
            gaps=[],
            objections=[],
            roadmap=[],
        )
