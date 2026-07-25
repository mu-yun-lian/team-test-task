"""pitchdeck_scorer — Startup Pitch Deck Builder & Scorer (Idea 57).

A harness that scores a startup pitch deck slide-by-slide on persuasion,
logic, and clarity against named VC frameworks, stress-tests it with
investor objections, and emits a slide-level fix roadmap.

Public API:
    from pitchdeck_scorer import (
        Context, Deck, SlideContent, Pipeline, ScoreReport,
        RequirementsGatherer, ScoringEngine, QualityReviewer,
        ImprovementRoadmap, run,
    )
"""

from __future__ import annotations

from .models import (
    AxisScore,
    Context,
    Deck,
    Effort,
    FundabilityBand,
    Gap,
    Impact,
    Objection,
    Report,
    RoadmapItem,
    ScoreReport,
    SlideContent,
    SlideKind,
    SlideScore,
    Stage,
    TargetAudience,
)
from .pipeline import Pipeline, run

__all__ = [
    "AxisScore",
    "Context",
    "Deck",
    "Effort",
    "FundabilityBand",
    "Gap",
    "Impact",
    "Objection",
    "Pipeline",
    "Report",
    "RequirementsGatherer",
    "RoadmapItem",
    "ScoreReport",
    "ScoringEngine",
    "QualityReviewer",
    "ImprovementRoadmap",
    "SlideContent",
    "SlideKind",
    "SlideScore",
    "Stage",
    "TargetAudience",
    "run",
    "__version__",
]


# Lazily import the sub-skill classes so the top-level import stays light.
def __getattr__(name: str):  # PEP 562
    if name == "RequirementsGatherer":
        from .requirements_gatherer import RequirementsGatherer

        return RequirementsGatherer
    if name == "ScoringEngine":
        from .scoring_engine import ScoringEngine

        return ScoringEngine
    if name == "QualityReviewer":
        from .quality_reviewer import QualityReviewer

        return QualityReviewer
    if name == "ImprovementRoadmap":
        from .improvement_roadmap import ImprovementRoadmap

        return ImprovementRoadmap
    raise AttributeError(f"module 'pitchdeck_scorer' has no attribute {name!r}")


__version__ = "1.0.0"
