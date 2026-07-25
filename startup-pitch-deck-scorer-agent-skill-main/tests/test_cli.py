import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DECK = {
    "company": "CliCo",
    "slides": [
        {
            "title": "The Problem",
            "headline": "SMBs lose 10hrs/week reconciling invoices",
            "bullets": ["Finance teams waste hours", "Cost of manual error: $X", "Why now: AI can read invoices"],
        },
        {
            "kind": "ask",
            "title": "Ask",
            "headline": "Raising $1.5M seed",
            "bullets": [
                "$1.5M seed round",
                "Use of funds: engineering, sales",
                "Reaches $500k MRR milestone",
                "18 months runway",
            ],
        },
    ],
}
CONTEXT = {"stage": "seed", "sector": "saas", "raise_amount": "$1.5M", "audience": "seed-fund"}


def _run_cli(args, stdin=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    env["PYTHONUTF8"] = "1"
    env.setdefault("NO_COLOR", "1")
    return subprocess.run(
        [sys.executable, "-m", "pitchdeck_scorer", *args],
        cwd=str(ROOT),
        env=env,
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_cli_requires_deck(monkeypatch, tmp_path):
    res = _run_cli(["--deck", "nonexistent.json", "--context", str(tmp_path / "c.json")])
    # Either argparse error or our file-not-found handling.
    assert res.returncode != 0


def test_cli_markdown_output(tmp_path):
    deck_path = tmp_path / "deck.json"
    ctx_path = tmp_path / "ctx.json"
    deck_path.write_text(json.dumps(DECK), encoding="utf-8")
    ctx_path.write_text(json.dumps(CONTEXT), encoding="utf-8")
    res = _run_cli(["--deck", str(deck_path), "--context", str(ctx_path), "--format", "markdown"])
    assert res.returncode == 0, res.stderr
    assert "Pitch Deck Score Report" in res.stdout
    assert "CliCo" in res.stdout


def test_cli_json_output_to_file(tmp_path):
    deck_path = tmp_path / "deck.json"
    ctx_path = tmp_path / "ctx.json"
    out_path = tmp_path / "out.json"
    deck_path.write_text(json.dumps(DECK), encoding="utf-8")
    ctx_path.write_text(json.dumps(CONTEXT), encoding="utf-8")
    res = _run_cli(
        ["--deck", str(deck_path), "--context", str(ctx_path), "--format", "json", "--output", str(out_path)]
    )
    assert res.returncode == 0, res.stderr
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["company"] == "CliCo"
    assert data["stage"] == "seed"


def test_cli_stdin_deck(tmp_path):
    ctx_path = tmp_path / "ctx.json"
    ctx_path.write_text(json.dumps(CONTEXT), encoding="utf-8")
    res = _run_cli(["--deck", "-", "--context", str(ctx_path)], stdin=json.dumps(DECK))
    assert res.returncode == 0, res.stderr
    assert "CliCo" in res.stdout
