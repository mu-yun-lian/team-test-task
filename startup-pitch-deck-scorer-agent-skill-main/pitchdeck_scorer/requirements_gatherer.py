"""sub-requirements-gatherer.

Captures the context that calibrates investor expectations and benchmarks:
funding stage, sector, raise amount, use of funds, and target investor
audience. It is the first gate of the harness — scoring is blocked until
``stage`` and ``audience`` are set.

The gatherer accepts a raw mapping (e.g. parsed from a deck's Ask slide or a
form) and a deck, then normalizes and validates it into a ``Context``.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, Optional

from .canonical import map_title_to_kind
from .models import Context, Deck, SlideKind, Stage, TargetAudience

_STAGE_ALIASES: dict[str, Stage] = {
    "pre-seed": Stage.PRE_SEED,
    "preseed": Stage.PRE_SEED,
    "pre seed": Stage.PRE_SEED,
    "seed": Stage.SEED,
    "series a": Stage.SERIES_A,
    "series-a": Stage.SERIES_A,
    "a round": Stage.SERIES_A,
    "series b": Stage.SERIES_B_PLUS,
    "series-b": Stage.SERIES_B_PLUS,
    "series b+": Stage.SERIES_B_PLUS,
    "series-b-plus": Stage.SERIES_B_PLUS,
    "growth": Stage.SERIES_B_PLUS,
    "series c": Stage.SERIES_B_PLUS,
}

_AUDIENCE_ALIASES: dict[str, TargetAudience] = {
    "angel": TargetAudience.ANGEL,
    "angels": TargetAudience.ANGEL,
    "pre-seed fund": TargetAudience.PRE_SEED_FUND,
    "pre-seed-fund": TargetAudience.PRE_SEED_FUND,
    "pre seed fund": TargetAudience.PRE_SEED_FUND,
    "accelerator": TargetAudience.PRE_SEED_FUND,
    "seed fund": TargetAudience.SEED_FUND,
    "seed-fund": TargetAudience.SEED_FUND,
    "series a fund": TargetAudience.SERIES_A_FUND,
    "series-a-fund": TargetAudience.SERIES_A_FUND,
    "vc": TargetAudience.SEED_FUND,
    "institutional": TargetAudience.SEED_FUND,
    "growth equity": TargetAudience.GROWTH,
    "growth-equity": TargetAudience.GROWTH,
    "growth": TargetAudience.GROWTH,
    "late stage": TargetAudience.GROWTH,
}

_MONEY = re.compile(r"\$\s?\s*(\d+(?:\.\d+)?)\s*([bmk])", re.IGNORECASE)


class RequirementsError(ValueError):
    """Raised when required context (stage/audience) cannot be resolved."""


def _normalize_stage(value: Any) -> Optional[Stage]:
    if value is None:
        return None
    if isinstance(value, Stage):
        return value
    key = str(value).strip().lower()
    if key in {s.value for s in Stage}:
        return Stage(key)
    return _STAGE_ALIASES.get(key)


def _normalize_audience(value: Any) -> Optional[TargetAudience]:
    if value is None:
        return None
    if isinstance(value, TargetAudience):
        return value
    key = str(value).strip().lower()
    if key in {a.value for a in TargetAudience}:
        return TargetAudience(key)
    return _AUDIENCE_ALIASES.get(key)


def parse_money(text: str) -> Optional[float]:
    """Parse a money string like '$1.5M' / '$500k' into a USD float."""
    m = _MONEY.search(text or "")
    if not m:
        return None
    num = float(m.group(1))
    unit = m.group(2).lower()
    return num * (1_000_000_000 if unit == "b" else 1_000_000 if unit == "m" else 1_000)


class RequirementsGatherer:
    """First sub-skill of the harness: produce a validated ``Context``."""

    def gather(
        self,
        deck: Deck,
        *,
        stage: Any = None,
        sector: str = "",
        raise_amount: Any = None,
        use_of_funds: str = "",
        audience: Any = None,
        company: Optional[str] = None,
        raw: Optional[Mapping[str, Any]] = None,
    ) -> Context:
        raw = raw or {}
        company = company or raw.get("company") or deck.company or "Untitled"
        sector = sector or raw.get("sector") or "general"

        stage_val = stage if stage is not None else raw.get("stage")
        audience_val = audience if audience is not None else raw.get("audience")
        raise_val = raise_amount if raise_amount is not None else raw.get("raise_amount")
        uof = use_of_funds or raw.get("use_of_funds") or ""

        # Try to recover missing fields from the deck's Ask slide.
        ask = deck.slide(SlideKind.ASK) if hasattr(deck, "slide") else None
        if ask is None and deck.slides:
            for s in deck.slides:
                if map_title_to_kind(s.title) == SlideKind.ASK:
                    ask = s
                    break
        if stage_val is None and ask is not None:
            inferred = self._infer_stage_from_text(ask.text)
            if inferred is not None:
                stage_val = inferred
        if audience_val is None and ask is not None:
            inferred = self._infer_audience_from_text(ask.text)
            if inferred is not None:
                audience_val = inferred
        if raise_val is None and ask is not None:
            raise_val = parse_money(ask.text)
        if not uof and ask is not None:
            uof = self._infer_use_of_funds(ask.text)

        stage_n = _normalize_stage(stage_val)
        audience_n = _normalize_audience(audience_val)

        missing = []
        if stage_n is None:
            missing.append("stage")
        if audience_n is None:
            missing.append("audience")
        if missing:
            raise RequirementsError(
                "Requirements gate failed: missing required context: "
                + ", ".join(missing)
                + ". Provide stage (pre-seed/seed/series-a/series-b-plus) and "
                "audience (angel/seed-fund/series-a-fund/...)."
            )

        raise_usd = raise_val if isinstance(raise_val, (int, float)) else parse_money(str(raise_val or ""))

        return Context(
            stage=stage_n,
            sector=sector.strip() or "general",
            raise_amount_usd=raise_usd,
            use_of_funds=uof.strip(),
            audience=audience_n,
            company=company,
        )

    # --- inference helpers -------------------------------------------------

    _STAGE_KEYWORDS = (
        (re.compile(r"\bpre[\s-]?seed\b", re.I), Stage.PRE_SEED),
        (re.compile(r"\bseries\s*a\b", re.I), Stage.SERIES_A),
        (re.compile(r"\bseries\s*[bc]\b|\bgrowth\b", re.I), Stage.SERIES_B_PLUS),
        (re.compile(r"\bseed\b", re.I), Stage.SEED),
    )

    _AUDIENCE_KEYWORDS = (
        (re.compile(r"\bangels?\b", re.I), TargetAudience.ANGEL),
        (re.compile(r"\baccelerator\b|\bpre[\s-]?seed\s*fund\b", re.I), TargetAudience.PRE_SEED_FUND),
        (re.compile(r"\bseed\s*fund\b|\binstitutional\b|\bvc\b", re.I), TargetAudience.SEED_FUND),
        (re.compile(r"\bseries\s*a\s*fund\b", re.I), TargetAudience.SERIES_A_FUND),
        (re.compile(r"\bgrowth\s*(equity)?\b|\blate[\s-]?stage\b", re.I), TargetAudience.GROWTH),
    )

    def _infer_stage_from_text(self, text: str) -> Optional[Stage]:
        for pat, stage in self._STAGE_KEYWORDS:
            if pat.search(text or ""):
                return stage
        return None

    def _infer_audience_from_text(self, text: str) -> Optional[TargetAudience]:
        for pat, aud in self._AUDIENCE_KEYWORDS:
            if pat.search(text or ""):
                return aud
        return None

    def _infer_use_of_funds(self, text: str) -> str:
        text = text or ""
        m = re.search(r"use\s+of\s+funds?\s*[:\-]?\s*(.+)", text, re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(1).strip().splitlines()[0][:240]
        # fall back to a comma-separated bucket list (engineering, hiring, ...)
        buckets = re.findall(
            r"\b(engineering|hiring|sales|marketing|product|gtm|ops|operations|rnd|infrastructure)\b",
            text,
            re.IGNORECASE,
        )
        if buckets:
            return ", ".join(sorted({b.lower() for b in buckets}))
        return ""
