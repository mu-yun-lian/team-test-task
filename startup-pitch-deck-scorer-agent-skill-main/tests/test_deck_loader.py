from pitchdeck_scorer.deck_loader import build_deck, build_slide, load_context_raw, load_deck
from pitchdeck_scorer.models import SlideKind


def test_build_slide_coerces_kind():
    s = build_slide({"kind": "market-tam", "title": "Market", "headline": "TAM", "bullets": ["1.2M SMBs x $1,000 ACV"]})
    assert s.kind == SlideKind.MARKET_TAM
    assert s.headline == "TAM"


def test_build_deck_from_dict():
    d = build_deck({"company": "X", "slides": [{"kind": "ask", "title": "Ask"}]})
    assert d.company == "X"
    assert len(d.slides) == 1


def test_load_deck_and_context_from_files():
    d = load_deck("tests/fixtures/example_deck.json")
    assert d.company == "ExampleCo"
    assert len(d.slides) == 11
    ctx = load_context_raw("tests/fixtures/example_context.json")
    assert ctx["stage"] == "seed"
    assert ctx["audience"] == "seed-fund"


def test_load_context_raw_none_returns_empty():
    assert load_context_raw(None) == {}
