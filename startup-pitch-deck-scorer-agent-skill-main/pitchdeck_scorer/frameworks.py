"""Named VC frameworks, scoring rubrics, and content detectors.

Frameworks (Phase 0 deliverable):
    * Sequoia deck template (Company purpose -> Problem -> Solution -> Why now
      -> Market size -> Competition -> Product -> Business model -> Team ->
      Financials).
    * Guy Kawasaki 10/20/30 (10 slides, 20 minutes, 30pt font — clarity & focus).
    * YC essentials (clear one-liner, real traction, big market, credible
      team, concrete ask).
    * TAM/SAM/SOM bottom-up market sizing.

The per-slide rubrics below are consumed by ``scoring_engine.ScoringEngine``.
Each canonical slide lists the rubric elements that should be present; the
engine checks presence via lightweight keyword/regex detectors and converts
missing or weak elements into scored Findings.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from .models import SlideKind

# ---------------------------------------------------------------------------
# Framework catalog
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Framework:
    name: str
    description: str
    slides: tuple[str, ...]
    notes: str = ""


FRAMEWORKS: tuple[Framework, ...] = (
    Framework(
        name="Sequoia deck template",
        description=(
            "The canonical Sequoia pitch structure: Company purpose, Problem, "
            "Solution, Why now, Market size, Competition, Product, Business "
            "model, Team, Financials."
        ),
        slides=(
            "Company purpose",
            "Problem",
            "Solution",
            "Why now",
            "Market size",
            "Competition",
            "Product",
            "Business model",
            "Team",
            "Financials",
        ),
        notes="Narrative arc first; numbers support the story.",
    ),
    Framework(
        name="Guy Kawasaki 10/20/30",
        description=("10 slides, delivered in 20 minutes, 30pt font. Clarity and focus over density."),
        slides=(
            "Title",
            "Problem",
            "Underlying magic",
            "Solution",
            "Business model",
            "Go-to-market",
            "Competitive landscape",
            "Team",
            "Projections/milestones",
            "Ask",
        ),
        notes="Less is more; every slide must survive a 20-second skim.",
    ),
    Framework(
        name="YC essentials",
        description=("A clear one-liner, real traction, a big market, a credible team, and a concrete ask."),
        slides=(
            "One-liner",
            "Problem",
            "Solution",
            "Traction",
            "Market",
            "Team",
            "Ask",
        ),
        notes="Traction is the strongest signal; explain it in plain numbers.",
    ),
    Framework(
        name="TAM/SAM/SOM (bottom-up)",
        description=(
            "Top-down 'X% of a huge market' is not credible. Size TAM bottom-up: "
            "addressable customers x realistic ACV, then SAM and SOM."
        ),
        slides=("Market size",),
        notes="Show the math; cite the customer count and price assumptions.",
    ),
)


# ---------------------------------------------------------------------------
# Rubric model
# ---------------------------------------------------------------------------

Axis = str  # "persuasion" | "logic" | "clarity"


@dataclass(frozen=True)
class RubricElement:
    code: str
    label: str
    axis: Axis
    weight: float  # importance within the slide (0-1); normalized later
    required: bool = True
    detector: str = "keyword"  # detector name handled in scoring_engine


@dataclass
class SlideRubric:
    kind: SlideKind
    label: str
    elements: tuple[RubricElement, ...]
    ideal_bullets: int = 4
    notes: str = ""


RUBRICS: dict[SlideKind, SlideRubric] = {
    SlideKind.PROBLEM: SlideRubric(
        kind=SlideKind.PROBLEM,
        label="Problem",
        ideal_bullets=3,
        notes="State who suffers, the pain, and urgency; avoid solution-speak here.",
        elements=(
            RubricElement("prob-who", "Names who has the problem", "persuasion", 0.30),
            RubricElement("prob-pain", "Describes the pain/cost of the status quo", "persuasion", 0.25),
            RubricElement("prob-urgency", "Explains why now (urgency)", "logic", 0.25),
            RubricElement("prob-specific", "Concrete examples / data, not vague claims", "clarity", 0.20),
        ),
    ),
    SlideKind.SOLUTION: SlideRubric(
        kind=SlideKind.SOLUTION,
        label="Solution",
        ideal_bullets=4,
        notes="One clear solution tied back to the problem; show how it works.",
        elements=(
            RubricElement("sol-clear", "One-sentence value proposition", "clarity", 0.30),
            RubricElement("sol-fit", "Maps solution to each named problem", "logic", 0.30),
            RubricElement("sol-how", "Describes how it works (mechanism)", "logic", 0.20),
            RubricElement("sol-diff", "States what is uniquely better", "persuasion", 0.20),
        ),
    ),
    SlideKind.MARKET_TAM: SlideRubric(
        kind=SlideKind.MARKET_TAM,
        label="Market / TAM",
        ideal_bullets=4,
        notes="Bottom-up TAM with the math; top-down 'X% of $YB' is penalized.",
        elements=(
            RubricElement("tam-bottom-up", "Bottom-up sizing (#customers x ACV)", "logic", 0.40),
            RubricElement("tam-math", "Shows the sizing math explicitly", "logic", 0.20),
            RubricElement("tam-segments", "Segments TAM/SAM/SOM or beachhead", "logic", 0.15),
            RubricElement("tam-credible", "Cites a source for the customer base", "persuasion", 0.15),
            RubricElement("tam-headline", "Headline TAM number stated up front", "clarity", 0.10),
        ),
    ),
    SlideKind.PRODUCT: SlideRubric(
        kind=SlideKind.PRODUCT,
        label="Product",
        ideal_bullets=4,
        notes="Show the product; avoid feature dumps without outcomes.",
        elements=(
            RubricElement("prod-evidence", "Screenshot/demo/proof of existence", "persuasion", 0.25),
            RubricElement("prod-outcomes", "Features tied to outcomes, not lists", "logic", 0.30),
            RubricElement("prod-tech", "Defensible / differentiated technology", "logic", 0.25),
            RubricElement("prod-clear", "Comprehensible to a non-technical investor", "clarity", 0.20),
        ),
    ),
    SlideKind.BUSINESS_MODEL: SlideRubric(
        kind=SlideKind.BUSINESS_MODEL,
        label="Business Model",
        ideal_bullets=3,
        notes="How you make money, with price and unit economics.",
        elements=(
            RubricElement("bm-revenue", "Revenue model named (SaaS/marketplace/...)", "logic", 0.30),
            RubricElement("bm-price", "Pricing / ACV stated", "logic", 0.25),
            RubricElement("bm-units", "Unit economics (CAC/LTV/payback/margin)", "logic", 0.30),
            RubricElement("bm-clear", "One-line business model", "clarity", 0.15),
        ),
    ),
    SlideKind.TRACTION: SlideRubric(
        kind=SlideKind.TRACTION,
        label="Traction",
        ideal_bullets=4,
        notes="Real, retention-aware metrics — not vanity signups alone.",
        elements=(
            RubricElement("trac-growth", "Growth trend with numbers", "persuasion", 0.25),
            RubricElement("trac-revenue", "Revenue/usage (not only signups)", "persuasion", 0.30),
            RubricElement("trac-retention", "Retention / churn / NRR", "logic", 0.25),
            RubricElement("trac-cadence", "Monthly/cadence + time period", "logic", 0.20),
        ),
    ),
    SlideKind.GTM: SlideRubric(
        kind=SlideKind.GTM,
        label="Go-to-Market",
        ideal_bullets=4,
        notes="Repeatable acquisition motion; CAC and channel.",
        elements=(
            RubricElement("gtm-channel", "Named acquisition channels", "logic", 0.30),
            RubricElement("gtm-cac", "CAC stated / payback period", "logic", 0.30),
            RubricElement("gtm-repeat", "Repeatable/scalable motion described", "persuasion", 0.25),
            RubricElement("gtm-clear", "One-line motion", "clarity", 0.15),
        ),
    ),
    SlideKind.COMPETITION: SlideRubric(
        kind=SlideKind.COMPETITION,
        label="Competition",
        ideal_bullets=4,
        notes="Honest landscape + defensible differentiation (moat).",
        elements=(
            RubricElement("comp-landscape", "Names real competitors", "logic", 0.30),
            RubricElement("comp-matrix", "Comparison matrix / axes", "clarity", 0.20),
            RubricElement("comp-diff", "States how you win", "persuasion", 0.25),
            RubricElement("comp-moat", "Defensibility / moat explained", "logic", 0.25),
        ),
    ),
    SlideKind.TEAM: SlideRubric(
        kind=SlideKind.TEAM,
        label="Team",
        ideal_bullets=4,
        notes="Relevant founder-market fit; fill obvious gaps.",
        elements=(
            RubricElement("team-founders", "Founders named with roles", "clarity", 0.20),
            RubricElement("team-fit", "Relevant domain/operating experience", "persuasion", 0.40),
            RubricElement("team-track", "Prior outcomes / credibility signals", "persuasion", 0.25),
            RubricElement("team-gaps", "Acknowledges & covers role gaps", "logic", 0.15),
        ),
    ),
    SlideKind.FINANCIALS: SlideRubric(
        kind=SlideKind.FINANCIALS,
        label="Financials",
        ideal_bullets=4,
        notes="Realistic, assumption-backed projections; flag hockey sticks.",
        elements=(
            RubricElement("fin-projection", "Revenue/ARR projection with horizon", "logic", 0.25),
            RubricElement("fin-assumptions", "Key assumptions stated", "logic", 0.35),
            RubricElement("fin-realistic", "Projection is realistic (not hockey-stick)", "logic", 0.25),
            RubricElement("fin-margin", "Margin / burn / runway shown", "persuasion", 0.15),
        ),
    ),
    SlideKind.ASK: SlideRubric(
        kind=SlideKind.ASK,
        label="Ask / Use of Funds",
        ideal_bullets=3,
        notes="Clear amount, use of funds, and milestones the round buys.",
        elements=(
            RubricElement("ask-amount", "Raise amount stated", "clarity", 0.30),
            RubricElement("ask-use", "Use of funds broken down", "logic", 0.30),
            RubricElement("ask-milestones", "Milestones the round reaches", "persuasion", 0.30),
            RubricElement("ask-runway", "Runway the round provides", "logic", 0.10),
        ),
    ),
}


# ---------------------------------------------------------------------------
# Content detectors
# ---------------------------------------------------------------------------

# Compiled regexes (kept module-level for reuse / performance).
_TOP_DOWN_TAM = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*%\s*(?:of|of the)\s+(?:a\s+|an\s+)?\$?\s*\d+(?:\.\d+)?\s*[bmt]",
    re.IGNORECASE,
)
_BOTTOM_UP_HINT = re.compile(r"bottom[\s-]?up|customers?\s*[x×]\s*(acv|arpu|price|#)", re.IGNORECASE)
_MONEY_NUMBER = re.compile(r"\$\s?\d+(?:\.\d+)?\s*[bmk]", re.IGNORECASE)
_PERCENT = re.compile(r"\b\d+(?:\.\d+)?\s*%")
_ARR_TARGET = re.compile(r"\$\s?\d+(?:\.\d+)?\s*[bm]\s*arr", re.IGNORECASE)
_SHORT_HORIZON = re.compile(r"\b(in|within|by)\s+(\d|two|three|four)\s*(yr|yrs|year|years)", re.IGNORECASE)
_VANITY_WORDS = re.compile(
    r"\b(signups?|registered\s+users?|downloads?|visitors?|page\s*views?|likes?|followers?)\b",
    re.IGNORECASE,
)
_REVENUE_WORDS = re.compile(r"\b(arr|mrr|revenue|gmv|paid\s+customers?|paying\s+users?|bookings?)\b", re.IGNORECASE)
_RETENTION_WORDS = re.compile(
    r"\b(retention|churn|nrr|net\s+revenue\s+retention|d7|d30|wau|mau|cohort)\b", re.IGNORECASE
)
_UNIT_ECON_WORDS = re.compile(r"\b(cac|ltv|lvc|payback|gross\s+margin|contribution\s+margin|roi)\b", re.IGNORECASE)
_MOAT_WORDS = re.compile(
    r"\b(moat|defensib|network\s+effect|switching\s+cost|patent|proprietary|lock-?in|data\s+moat)\b",
    re.IGNORECASE,
)
_HOCKEY_STICK = re.compile(r"hockey[\s-]?stick|j.?curve|10x\s+growth|exponential", re.IGNORECASE)


def _text(slide_text: str) -> str:
    return slide_text or ""


def is_top_down_tam(text: str) -> bool:
    return bool(_TOP_DOWN_TAM.search(_text(text)))


def has_bottom_up_tam(text: str) -> bool:
    return bool(_BOTTOM_UP_HINT.search(_text(text))) or (
        bool(_MONEY_NUMBER.search(_text(text)))
        and bool(re.search(r"customers?|accounts?|seats?|companies", _text(text), re.IGNORECASE))
    )


def has_vanity_metrics(text: str) -> bool:
    return bool(_VANITY_WORDS.search(_text(text))) and not _revenue_positive(text)


_NEGATED_REVENUE = re.compile(r"\b(no|without|zero|0|nil)\s+(arr|mrr|revenue|bookings?)\b", re.IGNORECASE)


def _revenue_positive(text: str) -> bool:
    """True if revenue is asserted in a positive (non-negated) form."""
    t = _text(text)
    if not _REVENUE_WORDS.search(t):
        return False
    # Drop negated mentions like 'no revenue', 'without arr' before deciding.
    stripped = _NEGATED_REVENUE.sub(" ", t)
    return bool(_REVENUE_WORDS.search(stripped))


def has_revenue_metric(text: str) -> bool:
    return _revenue_positive(text)


def has_retention_metric(text: str) -> bool:
    return bool(_RETENTION_WORDS.search(_text(text)))


def has_unit_economics(text: str) -> bool:
    return bool(_UNIT_ECON_WORDS.search(_text(text)))


def has_moat(text: str) -> bool:
    return bool(_MOAT_WORDS.search(_text(text)))


def has_named_competitors(text: str) -> bool:
    # At least two capitalized-looking tokens after a "vs"/"competitors" cue,
    # or simply 2+ tokens that look like product/company names (heuristic).
    return bool(re.search(r"(vs\.?|versus|competitors?|alternatives?)", _text(text), re.IGNORECASE)) or (
        len(re.findall(r"\b[A-Z][A-Za-z0-9]{2,}", _text(text))) >= 2
    )


def has_comparison_axes(text: str) -> bool:
    return bool(re.search(r"(matrix|axes?|comparison|features?\s*vs|capabilities?)", _text(text), re.IGNORECASE))


def looks_inflated_projection(text: str) -> bool:
    t = _text(text)
    if _HOCKEY_STICK.search(t):
        return True
    arr = _ARR_TARGET.search(t)
    horizon = _SHORT_HORIZON.search(t)
    # "$100M+ ARR in 2 years" with no stated assumption basis => inflated.
    if arr and horizon:
        big = re.search(r"\$\s?\s*(\d+(?:\.\d+)?)\s*([bm])", t, re.IGNORECASE)
        if big:
            num = float(big.group(1))
            unit = big.group(2).lower()
            value = num * (1_000 if unit == "b" else 1)
            if value >= 50:  # >= $50M ARR within a couple of years, flagged
                return True
    return False


def has_finite_horizon(text: str) -> bool:
    return bool(_SHORT_HORIZON.search(_text(text))) or bool(
        re.search(r"\b(18|24|36)\s*months?\b|\b3\s*year\b", _text(text), re.IGNORECASE)
    )


def has_assumptions(text: str) -> bool:
    return bool(re.search(r"(assumption|based on|assuming|driver|model|sensitivity)", _text(text), re.IGNORECASE))


def has_runway(text: str) -> bool:
    return bool(re.search(r"(runway|burn|months?\s*of\s*runway)", _text(text), re.IGNORECASE))


def has_pricing(text: str) -> bool:
    return bool(_MONEY_NUMBER.search(_text(text))) or bool(
        re.search(r"(per\s+(seat|user|month|year)|freemium|tier|\$/mo|\$x)", _text(text), re.IGNORECASE)
    )


def has_amount(text: str) -> bool:
    return bool(_MONEY_NUMBER.search(_text(text)))


def has_percentage(text: str) -> bool:
    return bool(_PERCENT.search(_text(text)))


def has_named_founders(text: str) -> bool:
    return len(re.findall(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+", _text(text))) >= 1


def has_domain_fit(text: str) -> bool:
    return bool(re.search(r"(years?|ex-|formerly|previously|background|domain|experience)", _text(text), re.IGNORECASE))


def has_evidence_words(text: str) -> bool:
    return bool(re.search(r"(screenshot|demo|live|video|prototype|launched|shipped)", _text(text), re.IGNORECASE))


def count_bullets(bullets: list[str]) -> int:
    return sum(1 for b in bullets if b.strip())


# A registry the scoring engine can introspect for tests / debugging.
DETECTORS: dict[str, Callable[..., bool]] = {
    "is_top_down_tam": is_top_down_tam,
    "has_bottom_up_tam": has_bottom_up_tam,
    "has_vanity_metrics": has_vanity_metrics,
    "has_revenue_metric": has_revenue_metric,
    "has_retention_metric": has_retention_metric,
    "has_unit_economics": has_unit_economics,
    "has_moat": has_moat,
    "has_named_competitors": has_named_competitors,
    "has_comparison_axes": has_comparison_axes,
    "looks_inflated_projection": looks_inflated_projection,
    "has_finite_horizon": has_finite_horizon,
    "has_assumptions": has_assumptions,
    "has_runway": has_runway,
    "has_pricing": has_pricing,
    "has_amount": has_amount,
    "has_named_founders": has_named_founders,
    "has_domain_fit": has_domain_fit,
    "has_evidence_words": has_evidence_words,
}
