"""Command-line interface for pitchdeck-scorer.

Examples
    # Score a deck (context inline as JSON)
    pitchdeck-scorer --deck deck.json \
        --context '{"stage":"seed","sector":"saas","raise_amount":"$1.5M","audience":"seed-fund"}'

    # Same, JSON output to a file
    pitchdeck-scorer --deck deck.json --context context.json --format json --output report.md

    # Pipe a deck over stdin (context via env or inline)
    cat deck.json | pitchdeck-scorer --deck - --context context.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Optional

from . import __version__
from .deck_loader import load_context_raw, load_deck
from .pipeline import Pipeline


def _read_deck_arg(path: str) -> Mapping[str, Any]:
    if path == "-":
        return json.loads(sys.stdin.read())
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _read_context_arg(arg: Optional[str]) -> dict:
    if not arg:
        return {}
    if arg.startswith("{"):
        return json.loads(arg)
    return load_context_raw(arg)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pitchdeck-scorer",
        description="Score a startup pitch deck slide-by-slide against VC frameworks, with a fix roadmap.",
    )
    p.add_argument("--deck", required=True, help='Path to a deck JSON file, or "-" to read from stdin.')
    p.add_argument(
        "--context",
        default=None,
        help="Context JSON file or inline JSON object with stage/sector/audience/raise_amount/use_of_funds.",
    )
    p.add_argument(
        "--online", action="store_true", default=None, help="Enable live web research (opt-in; offline by default)."
    )
    p.add_argument("--offline", dest="online", action="store_false", help="Force offline mode (default).")
    p.add_argument(
        "--format", choices=("markdown", "json"), default="markdown", help="Output format. Default: markdown."
    )
    p.add_argument("--output", "-o", default=None, help="Write output to a file instead of stdout.")
    p.add_argument(
        "--polish",
        action="store_true",
        help="Use the optional LLM adapter to polish the executive summary (requires OPENAI_API_KEY).",
    )
    p.add_argument("--version", action="version", version=f"pitchdeck-scorer {__version__}")
    return p


def _ensure_utf8_stdio() -> None:
    """Force UTF-8 stdout/stderr so non-ASCII report text (em-dash, etc.)
    never crashes on Windows codepages like cp1252/cp1258."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:
            pass


def main(argv: Optional[list[str]] = None) -> int:
    _ensure_utf8_stdio()
    args = build_parser().parse_args(argv)
    try:
        deck_data = _read_deck_arg(args.deck)
    except FileNotFoundError:
        print(f"error: deck file not found: {args.deck}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON for deck: {exc}", file=sys.stderr)
        return 2

    deck = load_deck(deck_data)
    try:
        ctx_raw = _read_context_arg(args.context)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"error: invalid context: {exc}", file=sys.stderr)
        return 2

    pipeline = Pipeline()
    try:
        report = pipeline.run(deck, context_raw=ctx_raw, online=args.online)
    except Exception as exc:  # requirements gate or other
        print(f"error: {exc}", file=sys.stderr)
        return 1

    output = pipeline.render(report, fmt=args.format, polish=args.polish)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Wrote {args.output} ({args.format}). Score {report.overall_score}/100 — {report.fundability.value}.")
    else:
        sys.stdout.write(output)
        if not output.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
