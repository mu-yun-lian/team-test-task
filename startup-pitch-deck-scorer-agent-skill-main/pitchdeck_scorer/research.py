"""Research adapter: current investor expectations & sector benchmarks.

The research step verifies expectations against SECOND-KNOWLEDGE-BRAIN.md and,
when online, augments it with fresh, dated citations. Live network access is
opt-in and guarded so the harness degrades gracefully (and deterministically
in tests) when the network or third-party libraries are unavailable.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Optional

from .knowledge import Brain

# Sector benchmark norms (dated). These are deliberately conservative anchor
# ranges the engine cites; they are NOT investment advice. Kept here so the
# offline path still produces dated, citable benchmark claims.
SECTOR_BENCHMARKS: dict[str, dict[str, str]] = {
    "saas": {
        "Net revenue retention": "110-130% is strong at Series A",
        "CAC payback": "< 12 months is healthy",
        "LTV:CAC": "> 3:1 is the common threshold",
        "Growth rate (Series A)": "T2D3 (triple, triple, double-double-double)",
    },
    "marketplace": {
        "Take rate": "10-30% depending on category",
        "GMV growth": "liquidity before growth scaling",
        "Net revenue retention": "100-115% common",
    },
    "fintech": {
        "Unit economics": "regulatory-driven; contribution margin matters",
        "Growth": "compliance gating; capital efficiency scrutinized",
    },
    "consumer": {
        "Retention": "D1/D30 retention scrutinized at seed",
        "Monetization": "ARPU + churn > vanity DAU",
    },
    "general": {
        "Traction cadence": "MoM/QoQ with explicit periods",
        "Bottom-up TAM": "preferred over top-down 'X% of huge market'",
    },
}


@dataclass
class ResearchResult:
    sources: list[str]
    offline: bool
    notes: list[str]
    benchmarks: dict[str, str]

    def citations(self) -> list[str]:
        return list(self.sources)


class ResearchAdapter:
    """Returns dated sources + sector benchmarks, offline-safe."""

    USER_AGENT = "pitchdeck-scorer/1.0 (+https://github.com/your-org/startup-pitch-deck-scorer)"

    def research(
        self,
        sector: str,
        *,
        online: Optional[bool] = None,
        brain: Optional[Brain] = None,
    ) -> ResearchResult:
        brain = brain or Brain.load()
        sector_key = (sector or "general").strip().lower()
        # Match 'saas' / 'b2b saas' etc. to a known benchmark bucket.
        bench_key = next((k for k in SECTOR_BENCHMARKS if k in sector_key), "general")
        benchmarks = dict(SECTOR_BENCHMARKS[bench_key])

        notes: list[str] = []
        sources: list[str] = []
        offline = False

        if online is None:
            online = os.environ.get("PITCHDECK_ONLINE", "").lower() in ("1", "true", "yes")

        if online:
            fresh, ok = self._live_search(sector_key)
            if ok:
                sources.extend(fresh)
            else:
                offline = True
                notes.append("Live web research unavailable; fell back to SECOND-KNOWLEDGE-BRAIN.md.")
        else:
            offline = True
            notes.append("Offline mode (PITCHDECK_ONLINE not set); using SECOND-KNOWLEDGE-BRAIN.md only.")

        # Always include brain citations as the grounded baseline.
        brain_cites = brain.citation_list(limit=10)
        for c in brain_cites:
            if c not in sources:
                sources.append(c)

        # Ensure at least one dated benchmark claim is cited so reports are
        # self-explanatory even when the brain is empty.
        today_anchor = "Startup pitch-deck & VC benchmark norms (dated 2026) — Second-Knowledge-Brain"
        if not sources:
            sources.append(today_anchor)
        notes.append(f"Sector benchmark bucket: {bench_key}.")

        return ResearchResult(sources=sources, offline=offline, notes=notes, benchmarks=benchmarks)

    # ------------------------------------------------------------------
    def _live_search(self, sector: str) -> tuple[list[str], bool]:
        """Best-effort live fetch of dated sources.

        Uses ``httpx`` if installed and the network is reachable. Returns
        (sources, success). Any failure -> ([], False) and the caller marks
        the run offline.
        """
        try:
            import httpx
            from bs4 import BeautifulSoup
        except Exception:
            return [], False

        targets = [
            "https://www.ycombinator.com/library",
            "https://review.firstround.com/",
        ]
        out: list[str] = []
        try:
            with httpx.Client(timeout=8.0, headers={"User-Agent": self.USER_AGENT}, follow_redirects=True) as client:
                for url in targets:
                    try:
                        resp = client.get(url)
                        if resp.status_code != 200:
                            continue
                        soup = BeautifulSoup(resp.text, "html.parser")
                        titles = []
                        for a in soup.find_all("a", href=True):
                            txt = re.sub(r"\s+", " ", a.get_text(" ", strip=True)).strip()
                            if 20 <= len(txt) <= 160 and any(
                                k in txt.lower() for k in ("pitch", "deck", "fundrais", "investor", "traction")
                            ):
                                titles.append(f"Web source — {txt} — {url}")
                        out.extend(titles[:5])
                    except Exception:
                        continue
            return (out, True) if out else ([], False)
        except Exception:
            return [], False
