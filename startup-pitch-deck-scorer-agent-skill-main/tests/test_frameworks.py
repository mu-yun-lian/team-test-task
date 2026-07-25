import pytest

from pitchdeck_scorer import frameworks as fw
from pitchdeck_scorer.frameworks import FRAMEWORKS, RUBRICS, SlideRubric


def test_at_least_three_frameworks():
    assert len(FRAMEWORKS) >= 3
    names = {f.name for f in FRAMEWORKS}
    assert {"Sequoia deck template", "Guy Kawasaki 10/20/30", "YC essentials"} <= names


def test_eleven_rubrics():
    assert len(RUBRICS) == 11
    for r in RUBRICS.values():
        assert isinstance(r, SlideRubric)
        assert r.elements
        total = sum(e.weight for e in r.elements)
        assert total == pytest.approx(1.0, abs=1e-6)


def test_top_down_tam_detector():
    assert fw.is_top_down_tam("1% of a $50B market")
    assert fw.is_top_down_tam("Capture 2% of the $10B market")
    assert not fw.is_top_down_tam("1.2M SMBs x $1,000 ACV = $1.2B TAM")


def test_bottom_up_tam_detector():
    assert fw.has_bottom_up_tam("1.2M SMBs x $1,000 ACV = $1.2B TAM (bottom-up)")
    assert fw.has_bottom_up_tam("bottom-up sizing: 100k customers")


def test_vanity_metrics_detector():
    assert fw.has_vanity_metrics("10,000 signups and registered users")
    assert not fw.has_vanity_metrics("10,000 signups and $20k MRR")


def test_negated_revenue_not_counted():
    # 'No revenue yet' should not suppress the vanity flag.
    assert fw.has_vanity_metrics("10,000 signups, no revenue yet")
    assert not fw.has_revenue_metric("no revenue yet")
    assert fw.has_revenue_metric("$20k MRR and growing")


def test_inflated_projection_detector():
    assert fw.looks_inflated_projection("$100M ARR in 2 years, hockey-stick")
    assert fw.looks_inflated_projection("$60M ARR within two years")
    assert not fw.looks_inflated_projection("$5M ARR in 24 months with stated assumptions")


def test_unit_economics_and_moat():
    assert fw.has_unit_economics("CAC $4k, LTV $24k, payback 9 months")
    assert fw.has_moat("Moat: data network effect and switching cost")
    assert not fw.has_moat("we are faster")
