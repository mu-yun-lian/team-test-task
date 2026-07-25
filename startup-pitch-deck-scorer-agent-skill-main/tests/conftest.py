"""pytest configuration: expose deck builders as fixtures and ensure UTF-8."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import pytest
from decks import (
    inflated_financials_deck,
    missing_business_model_deck,
    pre_seed_angel_deck,
    strong_deck,
    vanity_traction_deck,
    weak_topdown_tam_deck,
)

# Make stdout/stderr UTF-8 so assertions printing non-ASCII never fail on Windows.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass


@pytest.fixture
def strong_deck_fixture():
    return strong_deck()


@pytest.fixture
def weak_topdown_tam_deck_fixture():
    return weak_topdown_tam_deck()


@pytest.fixture
def vanity_traction_deck_fixture():
    return vanity_traction_deck()


@pytest.fixture
def missing_business_model_deck_fixture():
    return missing_business_model_deck()


@pytest.fixture
def inflated_financials_deck_fixture():
    return inflated_financials_deck()


@pytest.fixture
def pre_seed_angel_deck_fixture():
    return pre_seed_angel_deck()
