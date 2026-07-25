#!/usr/bin/env python3
"""knowledge_updater.py — Startup Pitch Deck Builder & Scorer (Idea 57)

Grow SECOND-KNOWLEDGE-BRAIN.md with deduplicated, dated entries crawled from
public VC / entrepreneurial-finance sources. Entries are scored by recency
and keyword relevance, deduped by a stable hash, and appended under a dated
``### Auto-update YYYY-MM-DD`` block.

Usage:
    python tools/knowledge_updater.py [--dry-run] [--limit N] [--offline]
    python tools/knowledge_updater.py --sources Sequoia,YC

Schedule: weekly cron. Dependencies (optional, graceful degradation):
    httpx, beautifulsoup4 (rich HTML parsing); crawl4ai (optional richer crawl).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import logging
import pathlib
import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Optional

BRAIN = pathlib.Path(__file__).resolve().parent.parent / "SECOND-KNOWLEDGE-BRAIN.md"

SOURCES = [
    {"name": "Sequoia", "url": "https://www.sequoiacap.com/article/"},
    {"name": "YC", "url": "https://www.ycombinator.com/library"},
    {"name": "First Round Review", "url": "https://review.firstround.com/"},
    {"name": "a16z", "url": "https://a16z.com/"},
    {"name": "SSRN", "url": "https://www.ssrn.com/index.cfm/en/"},
]
QUERIES = ["pitch deck benchmark 2026", "seed round metrics", "VC pitch expectations", "startup traction benchmark"]
KEYWORDS = [
    "pitch",
    "deck",
    "fundrais",
    "investor",
    "traction",
    "tam",
    "valuation",
    "seed",
    "series a",
    "metrics",
    "startup",
    "unit economics",
    "cac",
    "ltv",
    "retention",
    "market size",
    "go-to-market",
]

USER_AGENT = "pitchdeck-scorer-knowledge-updater/1.0 (+https://github.com/your-org/startup-pitch-deck-scorer)"
HASH_RE = re.compile(r"<!--h:([0-9a-f]{12})-->")
LOG = logging.getLogger("knowledge_updater")


@dataclass
class Entry:
    title: str
    source: str
    url: str
    date: Optional[str] = None  # discovered publication date, if any

    def hash(self) -> str:
        return hashlib.sha1((self.url + "|" + self.title).encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------


def fetch(source: dict, *, timeout: float = 10.0) -> list[Entry]:
    """Fetch a source page and extract candidate titles.

    Prefers httpx + BeautifulSoup for robust, dependency-light parsing. Falls
    back to crawl4ai if installed. Any error is logged and returns [].
    """
    entries: list[Entry] = []
    # Try crawl4ai first if available (richer extraction).
    try:
        from crawl4ai import WebCrawler  # type: ignore

        c = WebCrawler()
        c.warmup()
        result = c.run(url=source["url"])
        text = getattr(result, "markdown", "") or ""
        entries.extend(_entries_from_text(text, source))
        if entries:
            return entries
    except Exception as exc:
        LOG.debug("crawl4ai unavailable for %s: %s", source["name"], exc)

    try:
        import httpx
        from bs4 import BeautifulSoup
    except Exception as exc:
        LOG.warning("httpx/bs4 unavailable for %s: %s", source["name"], exc)
        return []

    try:
        with httpx.Client(timeout=timeout, headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
            resp = client.get(source["url"])
            if resp.status_code != 200:
                LOG.warning("%s returned HTTP %s", source["name"], resp.status_code)
                return []
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                txt = re.sub(r"\s+", " ", a.get_text(" ", strip=True)).strip()
                if 20 <= len(txt) <= 200 and _is_relevant(txt):
                    href = a["href"]
                    if href.startswith("/"):
                        href = source["url"].rstrip("/") + href
                    entries.append(Entry(title=txt, source=source["name"], url=href))
    except Exception as exc:
        LOG.warning("fetch failed for %s: %s", source["name"], exc)
        return []
    return entries


def _entries_from_text(text: str, source: dict) -> list[Entry]:
    out: list[Entry] = []
    for line in (text or "").splitlines():
        t = line.strip("#*- ").strip()
        if 20 < len(t) < 200 and _is_relevant(t):
            out.append(Entry(title=t, source=source["name"], url=source["url"]))
    return out


def _is_relevant(text: str) -> bool:
    low = text.lower()
    return any(k in low for k in KEYWORDS)


# ---------------------------------------------------------------------------
# Scoring + dedup
# ---------------------------------------------------------------------------


def score(e: Entry) -> float:
    low = e.title.lower()
    return sum(1.0 for k in KEYWORDS if k in low) + (1.0 if e.date else 0.0)


def existing_hashes(text: str) -> set[str]:
    return set(HASH_RE.findall(text or ""))


def collect(sources: Iterable[dict]) -> list[Entry]:
    out: list[Entry] = []
    for s in sources:
        out.extend(fetch(s))
    out.sort(key=score, reverse=True)
    return out


# ---------------------------------------------------------------------------
# Brain append
# ---------------------------------------------------------------------------


def render_block(today: str, entries: list[Entry], seen: set[str]) -> list[str]:
    lines: list[str] = []
    for e in entries:
        h = e.hash()
        if h in seen:
            continue
        seen.add(h)
        lines.append(f"- [{today}] {e.title} — {e.source} — {e.url} <!--h:{h}-->")
    return lines


def update(
    brain_path: pathlib.Path, *, dry_run: bool, limit: int, sources_filter: Optional[list[str]], offline: bool
) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    if offline:
        LOG.info("Offline requested — nothing to fetch. Exiting.")
        return 0

    sources = SOURCES
    if sources_filter:
        wanted = {s.lower() for s in sources_filter}
        sources = [s for s in SOURCES if s["name"].lower() in wanted]
        if not sources:
            LOG.error("No sources matched filter: %s", sources_filter)
            return 2

    brain_text = brain_path.read_text(encoding="utf-8") if brain_path.exists() else ""
    seen = existing_hashes(brain_text)
    collected = collect(sources)[:limit] if limit > 0 else collect(sources)
    today = dt.date.today().isoformat()
    new_lines = render_block(today, collected, seen)

    if not new_lines:
        print("No new entries.")
        return 0

    block = f"\n### Auto-update {today}\n" + "\n".join(new_lines) + "\n"
    if dry_run:
        print(block)
        print(f"[dry-run] Would append {len(new_lines)} entries to {brain_path}.")
        return 0

    brain_path.parent.mkdir(parents=True, exist_ok=True)
    with brain_path.open("a", encoding="utf-8") as fh:
        fh.write(block)
    print(f"Appended {len(new_lines)} entries to {brain_path}.")
    return 0


def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="Print what would be appended; do not write.")
    ap.add_argument("--limit", type=int, default=40, help="Max candidate entries to consider (0 = no limit).")
    ap.add_argument("--sources", default=None, help="Comma-separated source names to restrict to.")
    ap.add_argument("--offline", action="store_true", help="Skip fetching; exit immediately.")
    ap.add_argument("--brain", default=str(BRAIN), help="Path to SECOND-KNOWLEDGE-BRAIN.md.")
    ap.add_argument("--json", action="store_true", help="Emit collected entries as JSON to stdout (no write).")
    return ap


def main(argv: Optional[list[str]] = None) -> int:
    args = build_argparser().parse_args(argv)
    brain_path = pathlib.Path(args.brain)
    sources_filter = args.sources.split(",") if args.sources else None

    if args.json:
        collected = collect(
            SOURCES
            if not sources_filter
            else [s for s in SOURCES if s["name"].lower() in {x.lower() for x in sources_filter}]
        )
        print(json.dumps([{"title": e.title, "source": e.source, "url": e.url} for e in collected], indent=2))
        return 0

    return update(
        brain_path, dry_run=args.dry_run, limit=args.limit, sources_filter=sources_filter, offline=args.offline
    )


if __name__ == "__main__":
    raise SystemExit(main())
