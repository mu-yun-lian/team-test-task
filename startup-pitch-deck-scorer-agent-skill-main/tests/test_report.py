import json

from decks import strong_deck

from pitchdeck_scorer import run
from pitchdeck_scorer.models import SlideKind
from pitchdeck_scorer.report import render_json, render_markdown


def _report():
    return run(
        strong_deck(),
        context={"stage": "seed", "sector": "saas", "raise_amount": "$1.5M", "audience": "seed-fund"},
        fmt="report",
    )


def test_markdown_has_all_sections():
    md = render_markdown(_report())
    for header in [
        "## 1. Summary",
        "## 2. Per-Slide Scores",
        "## 3. Gaps",
        "## 4. Investor Objections",
        "## 5. Fix Roadmap",
        "## 6. Sources & Currency",
    ]:
        assert header in md


def test_markdown_includes_executive_summary_when_provided():
    md = render_markdown(_report(), executive_summary="A tight summary.")
    assert "A tight summary." in md


def test_json_serializes_enums_as_values():
    js = render_json(_report())
    data = json.loads(js)
    assert data["stage"] == "seed"
    assert data["audience"] == "seed-fund"
    assert isinstance(data["overall_score"], (int, float))
    assert data["per_slide"][0]["kind"] in {k.value for k in SlideKind}


def test_markdown_notes_offline_when_offline():
    rep = _report()
    rep = rep.model_copy(update={"offline": True})
    md = render_markdown(rep)
    assert "Offline" in md


def test_run_returns_markdown_string():
    md = run(
        strong_deck(),
        context={"stage": "seed", "sector": "saas", "raise_amount": "$1.5M", "audience": "seed-fund"},
        fmt="markdown",
    )
    assert isinstance(md, str)
    assert "Pitch Deck Score Report" in md
