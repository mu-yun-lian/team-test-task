import pytest

from pitchdeck_scorer.canonical import (
    CANONICAL_ORDER,
    canonical_slides,
    map_title_to_kind,
)
from pitchdeck_scorer.models import SlideContent, SlideKind


def test_canonical_order_has_eleven_slides():
    assert len(CANONICAL_ORDER) == 11
    assert SlideKind.ASK in CANONICAL_ORDER


@pytest.mark.parametrize(
    "title,kind",
    [
        ("The Problem", SlideKind.PROBLEM),
        ("Market Size / TAM", SlideKind.MARKET_TAM),
        ("How we make money", SlideKind.BUSINESS_MODEL),
        ("Competition & Moat", SlideKind.COMPETITION),
        ("Go-to-Market", SlideKind.GTM),
        ("Traction", SlideKind.TRACTION),
        ("Team", SlideKind.TEAM),
        ("The Ask", SlideKind.ASK),
        ("Financials 2026", SlideKind.FINANCIALS),
    ],
)
def test_map_title_to_kind(title, kind):
    assert map_title_to_kind(title) == kind


def test_map_unknown_title_returns_none():
    assert map_title_to_kind("Something weird") is None
    assert map_title_to_kind("") is None


def test_canonical_slides_splits_and_finds_missing():
    slides = [
        SlideContent(kind=SlideKind.PROBLEM, title="Problem", headline="x", bullets=["a"]),
        SlideContent(title="Random Intro", headline="y"),
    ]
    canonical, extras, missing = canonical_slides(slides)
    assert SlideKind.PROBLEM in {s.kind for s in canonical}
    assert len(extras) == 1  # the random intro
    assert SlideKind.ASK in missing
    assert len(missing) == 10


def test_canonical_slides_dedupe_prefers_richer_slide():
    thin = SlideContent(title="Traction", headline="thin")
    rich = SlideContent(title="Traction", headline="rich", bullets=["a", "b", "c"])
    canonical, extras, missing = canonical_slides([thin, rich])
    traction = [s for s in canonical if s.kind == SlideKind.TRACTION][0]
    assert traction.headline == "rich"
    assert len(extras) == 1
