import pathlib
import tempfile

from pitchdeck_scorer.knowledge import Brain, parse_entries

BRAIN_TEXT = """# Brain
## Core Concepts & Frameworks
- Sequoia template
- Kawasaki 10/20/30

### Auto-update 2026-06-18
- [2026-06-18] Great pitch decks — Sequoia — https://sequoiacap.com <!--h:abc123def456-->
- [2026-06-20] YC advice — YC — https://ycombinator.com <!--h:def789abc012-->
"""


def test_parse_entries():
    entries = parse_entries(BRAIN_TEXT)
    assert len(entries) == 2
    assert entries[0].date == "2026-06-18"
    assert entries[0].source == "Sequoia"
    assert entries[1].url == "https://ycombinator.com"


def test_load_from_file_and_citations():
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "BRAIN.md"
        p.write_text(BRAIN_TEXT, encoding="utf-8")
        brain = Brain.load(p)
        assert brain.is_available()
        cites = brain.citation_list()
        # Most recent first
        assert cites[0].startswith("[2026-06-20]")
        assert brain.framework_summary().lower().startswith("## core concepts")


def test_load_missing_file_is_safe():
    brain = Brain.load(pathlib.Path("/nonexistent/brain.md"))
    assert not brain.is_available()
    assert brain.citation_list() == []
    assert brain.framework_summary() == ""
