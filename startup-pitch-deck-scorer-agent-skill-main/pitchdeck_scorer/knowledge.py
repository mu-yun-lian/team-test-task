"""Reader for SECOND-KNOWLEDGE-BRAIN.md.

The brain is a curated, weekly-updated knowledge file grown by
``tools.knowledge_updater.py``. This module parses it into structured pieces
the research step can cite, and surfaces the "offline" brain as the fallback
when live web research is unavailable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

BRAIN_FILENAME = "SECOND-KNOWLEDGE-BRAIN.md"

_ENTRY_RE = re.compile(
    r"^-\s*\[(?P<date>\d{4}-\d{2}-\d{2})\]\s*(?P<title>.+?)\s*—\s*(?P<source>.+?)\s*—\s*(?P<url>\S+)(?:\s*<!--h:(?P<hash>[0-9a-f]+)-->)?\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class BrainEntry:
    date: str
    title: str
    source: str
    url: str
    hash: Optional[str] = None

    def citation(self) -> str:
        return f"[{self.date}] {self.title} — {self.source} — {self.url}"


@dataclass
class Brain:
    path: Path
    text: str
    entries: list[BrainEntry]

    @classmethod
    def load(cls, path: Optional[Path] = None) -> Brain:
        path = path or _default_brain_path()
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        entries = parse_entries(text)
        return cls(path=path, text=text, entries=entries)

    def is_available(self) -> bool:
        return self.path.exists()

    def citation_list(self, limit: int = 12) -> list[str]:
        # Most recent first (entries are appended over time; sort by date desc).
        sorted_entries = sorted(self.entries, key=lambda e: e.date, reverse=True)
        return [e.citation() for e in sorted_entries[:limit]]

    def framework_summary(self) -> str:
        """Return the 'Core Concepts & Frameworks' section text for context."""
        m = re.search(
            r"##\s*Core Concepts\s*&\s*Frameworks.*?(?=\n##\s|\Z)",
            self.text,
            re.S | re.I,
        )
        return m.group(0).strip() if m else ""


def _default_brain_path() -> Path:
    here = Path(__file__).resolve().parent.parent
    return here / BRAIN_FILENAME


def parse_entries(text: str) -> list[BrainEntry]:
    out: list[BrainEntry] = []
    for line in (text or "").splitlines():
        m = _ENTRY_RE.match(line.strip())
        if not m:
            continue
        out.append(
            BrainEntry(
                date=m.group("date"),
                title=m.group("title").strip(),
                source=m.group("source").strip(),
                url=m.group("url").strip(),
                hash=m.group("hash"),
            )
        )
    return out
