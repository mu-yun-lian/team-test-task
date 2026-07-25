"""Shared fixtures for the pitchdeck-scorer test-suite."""

from __future__ import annotations

import json
import pathlib

from pitchdeck_scorer.models import Deck, SlideContent, SlideKind

FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"


def slide(kind: SlideKind, title: str, headline: str = "", bullets=None, notes: str = "") -> SlideContent:
    return SlideContent(kind=kind, title=title, headline=headline, bullets=list(bullets or []), notes=notes)


def strong_deck() -> Deck:
    """A well-rounded pre-seed SaaS deck that should score Fundable-ish."""
    return Deck(
        company="StrongCo",
        slides=[
            slide(
                SlideKind.PROBLEM,
                "The Problem",
                "SMBs lose 10 hours/week reconciling invoices",
                [
                    "Finance teams waste hours on manual reconciliation",
                    "Cost of errors: $50k/year per company",
                    "Why now: AI can read invoices accurately",
                    "For SMB finance teams",
                ],
            ),
            slide(
                SlideKind.SOLUTION,
                "Solution",
                "Automated invoice reconciliation for SMBs",
                [
                    "One-line value prop: close the books in minutes",
                    "How it works: AI model reads and matches invoices",
                    "Unlike QuickBooks, end-to-end and accurate",
                    "Maps to each problem above",
                ],
            ),
            slide(
                SlideKind.MARKET_TAM,
                "Market",
                "Bottom-up TAM = $1.2B",
                [
                    "1.2M SMBs x $1,000 ACV = $1.2B TAM (bottom-up)",
                    "SAM = $400M (US finance-heavy SMBs)",
                    "SOM (3yr) = $40M",
                    "Source: Statista SMB census",
                ],
            ),
            slide(
                SlideKind.PRODUCT,
                "Product",
                "AI reconciliation engine",
                [
                    "Live demo screenshot",
                    "Reduces reconciliation time by 80%",
                    "Proprietary ML matching model",
                    "Plain-language: it reads invoices",
                ],
            ),
            slide(
                SlideKind.BUSINESS_MODEL,
                "Business Model",
                "SaaS subscription",
                [
                    "SaaS subscription, $1,000/yr per company",
                    "Pricing: $1k/yr ACV",
                    "CAC $4k, LTV $24k, payback 9 months",
                    "Gross margin 80%",
                ],
            ),
            slide(
                SlideKind.TRACTION,
                "Traction",
                "$20k MRR, growing 20% MoM",
                [
                    "$20k MRR, growing 20% MoM over last 6 months",
                    "ARR $240k, 240 paying customers",
                    "NRR 115%, churn 3% monthly",
                    "Cadence: MoM, Q2 2026",
                ],
            ),
            slide(
                SlideKind.GTM,
                "Go-to-Market",
                "Outbound + content motion",
                [
                    "Outbound sales + SEO content as channels",
                    "CAC $4k, payback 9 months",
                    "Repeatable outbound playbook",
                    "One-line: outbound to SMB finance teams",
                ],
            ),
            slide(
                SlideKind.COMPETITION,
                "Competition",
                "vs QuickBooks, Xero, BILL",
                [
                    "Named competitors: QuickBooks, Xero, BILL",
                    "Comparison matrix on accuracy, automation, price",
                    "We win on end-to-end automation",
                    "Moat: proprietary invoice graph + data network effect",
                ],
            ),
            slide(
                SlideKind.TEAM,
                "Team",
                "Ex-Stripe + ex-Plaid founders",
                [
                    "Jane Doe - CEO, ex-Stripe, 10 years in fintech",
                    "John Smith - CTO, ex-Plaid, built prior SaaS to $5M ARR",
                    "Prior exit: acquired by Stripe",
                    "Hiring head of sales (role gap covered)",
                ],
            ),
            slide(
                SlideKind.FINANCIALS,
                "Financials",
                "Path to $5M ARR in 24 months",
                [
                    "$5M ARR target in 24 months",
                    "Assumptions: 20% MoM growth, 3% churn",
                    "Realistic ramp (no hockey-stick)",
                    "Gross margin 80%, 18 months runway",
                ],
            ),
            slide(
                SlideKind.ASK,
                "Ask",
                "Raising $1.5M seed",
                [
                    "$1.5M seed round",
                    "Use of funds: engineering, sales, product",
                    "Milestones: reach $500k MRR by Q4",
                    "18 months runway",
                ],
            ),
        ],
    )


def weak_topdown_tam_deck() -> Deck:
    """Scenario 2: top-down TAM deck."""
    return Deck(
        company="TamCo",
        slides=[
            slide(
                SlideKind.MARKET_TAM, "Market", "1% of a $50B market", ["1% of a $50B market", "Top-down market sizing"]
            ),
        ],
    )


def vanity_traction_deck() -> Deck:
    """Scenario 3: vanity-metrics traction."""
    return Deck(
        company="VanityCo",
        slides=[
            slide(
                SlideKind.TRACTION,
                "Traction",
                "10,000 signups",
                ["10,000 signups", "Registered users growing", "No revenue yet"],
            ),
        ],
    )


def missing_business_model_deck() -> Deck:
    """Scenario 4: deck with no monetization slide."""
    return Deck(
        company="NoBmCo",
        slides=[
            slide(SlideKind.PROBLEM, "Problem", "A real problem", ["Who: SMBs", "Pain: time", "Why now"]),
            slide(SlideKind.SOLUTION, "Solution", "A solution", ["Value prop", "How it works", "Unlike incumbents"]),
        ],
    )


def inflated_financials_deck() -> Deck:
    """Scenario 5: hockey-stick financials."""
    return Deck(
        company="InflateCo",
        slides=[
            slide(
                SlideKind.FINANCIALS,
                "Financials",
                "$100M ARR in 2 years",
                ["Hockey-stick projection to $100M ARR", "Within 2 years", "$100M ARR target"],
            ),
        ],
    )


def pre_seed_angel_deck() -> Deck:
    """Scenario 1: pre-seed deck for angels."""
    return Deck(
        company="AngelCo",
        slides=[
            slide(
                SlideKind.PROBLEM,
                "Problem",
                "Founders waste hours on compliance",
                [
                    "Who: early founders",
                    "Pain: legal compliance is slow and expensive",
                    "Why now: regulatory shift",
                    "Example: 10 hours/week",
                ],
            ),
            slide(
                SlideKind.SOLUTION,
                "Solution",
                "Compliance autopilot",
                ["One-line value prop", "How it works via AI", "Unlike lawyers, instant"],
            ),
            slide(
                SlideKind.TEAM,
                "Team",
                "Founder who lived the problem",
                ["Founder lived this problem for 3 years", "Ex-compliance officer"],
            ),
            slide(
                SlideKind.ASK,
                "Ask",
                "Raising $500k from angels",
                ["$500k from angels", "Use of funds: engineering", "Milestone: 10 paying pilots", "12 months runway"],
            ),
        ],
    )


def load_fixture_json(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))
