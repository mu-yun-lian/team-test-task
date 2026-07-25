"""Deck & context loaders (JSON/dict -> typed models).

A deck is provided as a dict with ``company`` and ``slides``. Each slide may
already carry a canonical ``kind``; otherwise the title is mapped heuristically
in ``canonical.canonical_slides``. This keeps the CLI and library APIs
flexible for real-world inputs (exported PDF text, slide-export JSON, etc.).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Optional, Union

from .models import Deck, Metric, SlideContent, SlideKind

_SLIDE_KIND_VALUES = {k.value for k in SlideKind}


def _coerce_kind(value: Any) -> Optional[SlideKind]:
    if value is None:
        return None
    if isinstance(value, SlideKind):
        return value
    key = str(value).strip().lower()
    if key in _SLIDE_KIND_VALUES:
        return SlideKind(key)
    return None


def build_slide(data: Mapping[str, Any]) -> SlideContent:
    metrics = [Metric(**m) if isinstance(m, Mapping) else Metric(name=str(m)) for m in (data.get("metrics") or [])]
    kind = _coerce_kind(data.get("kind"))
    return SlideContent(
        kind=kind,  # may be None; canonical.canonical_slides maps by title
        title=str(data.get("title") or ""),
        headline=str(data.get("headline") or ""),
        bullets=[str(b) for b in (data.get("bullets") or [])],
        metrics=metrics,
        notes=str(data.get("notes") or ""),
        raw=str(data.get("raw") or ""),
    )


def build_deck(data: Mapping[str, Any]) -> Deck:
    slides = [build_slide(s) for s in (data.get("slides") or [])]
    return Deck(
        company=str(data.get("company") or "Untitled"),
        slides=slides,
        source=str(data.get("source") or ""),
    )


def load_deck(source: Union[str, Path, Mapping[str, Any]]) -> Deck:
    if isinstance(source, Mapping):
        return build_deck(source)
    path = Path(source)
    data = json.loads(path.read_text(encoding="utf-8"))
    return build_deck(data)


def load_context_raw(source: Optional[Union[str, Path, Mapping[str, Any]]] = None) -> dict:
    if source is None:
        return {}
    if isinstance(source, Mapping):
        return dict(source)
    path = Path(source)
    return json.loads(path.read_text(encoding="utf-8"))
