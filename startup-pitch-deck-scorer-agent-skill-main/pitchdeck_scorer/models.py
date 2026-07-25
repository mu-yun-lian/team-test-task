"""Core data models for the pitch-deck scorer.

These Pydantic v2 models define the contracts that flow between the
sub-skills (requirements gatherer, scoring engine, quality reviewer,
improvement roadmap) and the report renderer. They are intentionally
framework-agnostic: the canonical slide set and the VC rubrics live in
``canonical`` and ``frameworks`` respectively.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class StrEnum(str, Enum):
    """A string enum that serializes to its value (3.11 backport)."""

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value


class Stage(StrEnum):
    PRE_SEED = "pre-seed"
    SEED = "seed"
    SERIES_A = "series-a"
    SERIES_B_PLUS = "series-b-plus"


class TargetAudience(StrEnum):
    ANGEL = "angel"
    PRE_SEED_FUND = "pre-seed-fund"
    SEED_FUND = "seed-fund"
    SERIES_A_FUND = "series-a-fund"
    GROWTH = "growth-equity"


class SlideKind(StrEnum):
    PROBLEM = "problem"
    SOLUTION = "solution"
    MARKET_TAM = "market-tam"
    PRODUCT = "product"
    BUSINESS_MODEL = "business-model"
    TRACTION = "traction"
    GTM = "gtm"
    COMPETITION = "competition"
    TEAM = "team"
    FINANCIALS = "financials"
    ASK = "ask"


class Effort(StrEnum):
    S = "S"
    M = "M"
    L = "L"


class Impact(StrEnum):
    LOW = "Low"
    MED = "Med"
    HIGH = "High"


class FundabilityBand(StrEnum):
    PASS = "Fundable as-is"
    REFINE = "Fundable with refinement"
    REWORK = "Needs material rework"
    NOT_FUNDABLE = "Not fundable in current state"


class AxisScore(BaseModel):
    """A 0-100 score on a single scoring axis."""

    persuasion: float = Field(ge=0.0, le=100.0)
    logic: float = Field(ge=0.0, le=100.0)
    clarity: float = Field(ge=0.0, le=100.0)

    @property
    def weighted(self) -> float:
        weights = ScoringWeights.default()
        return self.persuasion * weights.persuasion + self.logic * weights.logic + self.clarity * weights.clarity


class ScoringWeights(BaseModel):
    persuasion: float = 0.40
    logic: float = 0.35
    clarity: float = 0.25

    @classmethod
    def default(cls) -> ScoringWeights:
        return cls()

    @model_validator(mode="after")
    def _check(self) -> ScoringWeights:
        total = self.persuasion + self.logic + self.clarity
        if not 0.99 <= total <= 1.01:
            raise ValueError(f"scoring weights must sum to 1.0, got {total:.3f}")
        return self


class Metric(BaseModel):
    """A single quantitative metric captured on a slide (e.g. MRR, CAC)."""

    name: str
    raw: str
    value: Optional[float] = None
    unit: Optional[str] = None


class SlideContent(BaseModel):
    """A parsed pitch-deck slide mapped to a canonical slide kind.

    `kind` may be None for a raw, unmapped slide; `canonical.canonical_slides`
    resolves it from the title and returns resolved slides with `kind` set.
    """

    kind: Optional[SlideKind] = None
    title: str = ""
    headline: str = ""
    bullets: list[str] = Field(default_factory=list)
    metrics: list[Metric] = Field(default_factory=list)
    notes: str = ""
    raw: str = ""

    @property
    def text(self) -> str:
        parts = [self.title, self.headline, *self.bullets, self.notes, self.raw]
        return "\n".join(p for p in parts if p).strip()

    def has_text(self) -> bool:
        return bool(self.text.strip())


class Deck(BaseModel):
    """A parsed pitch deck: company metadata + ordered canonical slides."""

    company: str = "Untitled"
    slides: list[SlideContent] = Field(default_factory=list)
    extras: list[SlideContent] = Field(default_factory=list)  # non-canonical slides
    source: str = ""

    @property
    def present_kinds(self) -> set[SlideKind]:
        return {s.kind for s in self.slides}

    def slide(self, kind: SlideKind) -> Optional[SlideContent]:
        for s in self.slides:
            if s.kind == kind:
                return s
        return None


class Context(BaseModel):
    """Output of the requirements gatherer. Calibrates benchmarks."""

    stage: Stage
    sector: str = "general"
    raise_amount_usd: Optional[float] = None
    use_of_funds: str = ""
    audience: TargetAudience
    company: str = "Untitled"

    @property
    def raise_label(self) -> str:
        if self.raise_amount_usd is None:
            return "undisclosed"
        if self.raise_amount_usd >= 1_000_000:
            return f"${self.raise_amount_usd / 1_000_000:.1f}M"
        return f"${self.raise_amount_usd / 1_000:.0f}k"


class Finding(BaseModel):
    """A single rubric finding attached to a slide score."""

    code: str
    severity: str = "info"  # info | minor | major | blocker
    message: str
    deduction: float = 0.0  # points deducted from an axis (0-100 scale)


class SlideScore(BaseModel):
    kind: SlideKind
    label: str
    present: bool
    axes: AxisScore
    findings: list[Finding] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)

    @property
    def weighted(self) -> float:
        return round(self.axes.weighted, 1)


class Gap(BaseModel):
    kind: SlideKind
    reason: str


class Objection(BaseModel):
    """A tough investor question the deck must be able to answer."""

    question: str
    slide_kind: Optional[SlideKind] = None
    resolving_evidence: str
    severity: str = "major"  # minor | major | blocker


class RoadmapItem(BaseModel):
    """A concrete slide-level edit (before -> after) addressing objections."""

    slide_kind: SlideKind
    before: str
    after: str
    effort: Effort = Effort.M
    impact: Impact = Impact.MED
    objection_addressed: Optional[str] = None


class ScoreReport(BaseModel):
    """The complete synthesized output of the harness."""

    company: str
    stage: Stage
    audience: TargetAudience
    overall_score: float
    fundability: FundabilityBand
    per_slide: list[SlideScore]
    gaps: list[Gap]
    objections: list[Objection]
    roadmap: list[RoadmapItem]
    sources: list[str] = Field(default_factory=list)
    offline: bool = False
    notes: list[str] = Field(default_factory=list)

    model_config = {"use_enum_values": False}

    @model_validator(mode="after")
    def _overall_range(self) -> ScoreReport:
        if not 0.0 <= self.overall_score <= 100.0:
            raise ValueError("overall_score must be in [0, 100]")
        return self


# Backwards/forward-compat alias so older code referencing ``Report`` keeps working.
Report = ScoreReport
