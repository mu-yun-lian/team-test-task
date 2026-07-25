"""Canonical slide set and canonical-slide mapping utilities.

The canonical 11-slide set is the spine of the scorer: every deck slide is
mapped to one canonical kind, and any canonical kind with no mapped slide is
reported as a gap by the scoring engine.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping

from .models import SlideContent, SlideKind

# Ordered canonical set (presentation order a deck typically follows).
CANONICAL_ORDER: tuple[SlideKind, ...] = (
    SlideKind.PROBLEM,
    SlideKind.SOLUTION,
    SlideKind.MARKET_TAM,
    SlideKind.PRODUCT,
    SlideKind.BUSINESS_MODEL,
    SlideKind.TRACTION,
    SlideKind.GTM,
    SlideKind.COMPETITION,
    SlideKind.TEAM,
    SlideKind.FINANCIALS,
    SlideKind.ASK,
)

CANONICAL_LABELS: Mapping[SlideKind, str] = {
    SlideKind.PROBLEM: "Problem",
    SlideKind.SOLUTION: "Solution",
    SlideKind.MARKET_TAM: "Market / TAM",
    SlideKind.PRODUCT: "Product",
    SlideKind.BUSINESS_MODEL: "Business Model",
    SlideKind.TRACTION: "Traction",
    SlideKind.GTM: "Go-to-Market",
    SlideKind.COMPETITION: "Competition",
    SlideKind.TEAM: "Team",
    SlideKind.FINANCIALS: "Financials",
    SlideKind.ASK: "Ask / Use of Funds",
}

CANONICAL: tuple[SlideKind, ...] = CANONICAL_ORDER


# Keyword patterns used to auto-map raw slides to canonical kinds.
# Order matters: more specific patterns first (e.g. "market size" before "market").
_SLIDE_PATTERNS: tuple[tuple[SlideKind, tuple[str, ...]], ...] = (
    (SlideKind.PROBLEM, ("problem", "pain point", "pain", "issue we solve", "why now")),
    (SlideKind.SOLUTION, ("solution", "how it works", "what we do", "product overview")),
    (SlideKind.GTM, ("go-to-market", "go to market", "gtm", "sales motion", "distribution", "marketing")),
    (SlideKind.MARKET_TAM, ("market size", "tam", "sam", "som", "market opportunity", "market")),
    (SlideKind.PRODUCT, ("product", "demo", "features", "technology", "how it works")),
    (SlideKind.BUSINESS_MODEL, ("business model", "monetization", "pricing", "revenue model", "how we make money")),
    (SlideKind.TRACTION, ("traction", "growth", "metrics", "results", "customers")),
    (SlideKind.COMPETITION, ("competition", "competitors", "competitive landscape", "moat", "differentiation")),
    (SlideKind.TEAM, ("team", "founders", "advisors", "leadership", "about us")),
    (SlideKind.FINANCIALS, ("financials", "projections", "forecast", "unit economics", "p&l", "financial model")),
    (SlideKind.ASK, ("ask", "use of funds", "raising", "fundraise", "the ask", "round")),
)


def map_title_to_kind(title: str) -> SlideKind | None:
    """Best-effort mapping of a slide title to a canonical kind.

    Patterns are matched with word boundaries so that, e.g., 'som' does not
    match 'something', and 'go to market' resolves to GTM rather than the
    generic 'market' Market pattern.
    """
    if not title:
        return None
    t = _normalize(title)
    for kind, patterns in _SLIDE_PATTERNS:
        for p in patterns:
            # Word-boundary match via character classes (no backslash escapes).
            if re.search(r"(^|[^a-z0-9])" + re.escape(p) + r"([^a-z0-9]|$)", t):
                return kind
    return None


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9$%/\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def canonical_slides(
    slides: Iterable[SlideContent],
) -> tuple[list[SlideContent], list[SlideContent], list[SlideKind]]:
    """Split raw slides into (canonical, extras, missing_kinds).

    Slides whose ``kind`` is already set are trusted. Otherwise the title is
    mapped heuristically. If two raw slides map to the same kind, the richer
    one (longer text) wins and the other becomes an extra.
    """
    canonical: dict[SlideKind, SlideContent] = {}
    extras: list[SlideContent] = []

    for s in slides:
        kind = s.kind if s.kind is not None else map_title_to_kind(s.title)
        if kind is None:
            extras.append(s)
            continue
        resolved = s.model_copy(update={"kind": kind})
        existing = canonical.get(kind)
        if existing is None or len(resolved.text) > len(existing.text):
            if existing is not None:
                extras.append(existing)
            canonical[kind] = resolved
        else:
            extras.append(resolved)

    ordered = [canonical[k] for k in CANONICAL_ORDER if k in canonical]
    missing = [k for k in CANONICAL_ORDER if k not in canonical]
    return ordered, extras, missing


def all_labels() -> dict[str, str]:
    return {k.value: CANONICAL_LABELS[k] for k in CANONICAL_ORDER}
