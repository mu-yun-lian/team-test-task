"""Harness pipeline: orchestrate the five sub-skills end-to-end.

Flow:
    1. requirements_gatherer -> Context        (gate: stage + audience set)
    2. research              -> dated sources  (gate: cited + dated; offline-safe)
    3. scoring_engine        -> per-slide scores + gaps
    4. quality_reviewer      -> >= 5 objections
    5. improvement_roadmap   -> slide-level rewrites (every objection addressed)
    6. synthesize            -> ScoreReport (markdown/json renderable)
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Optional, Union

from .deck_loader import load_context_raw, load_deck
from .improvement_roadmap import ImprovementRoadmap
from .knowledge import Brain
from .llm import LLMAdapter
from .models import Context, Deck, ScoreReport
from .quality_reviewer import QualityReviewer
from .report import render_json, render_markdown
from .requirements_gatherer import RequirementsGatherer
from .research import ResearchAdapter
from .scoring_engine import ScoringEngine


class Pipeline:
    """End-to-end pitch-deck scoring harness."""

    def __init__(
        self,
        *,
        gatherer: Optional[RequirementsGatherer] = None,
        researcher: Optional[ResearchAdapter] = None,
        scorer: Optional[ScoringEngine] = None,
        reviewer: Optional[QualityReviewer] = None,
        roadmap: Optional[ImprovementRoadmap] = None,
        brain: Optional[Brain] = None,
        llm: Optional[LLMAdapter] = None,
    ):
        self.gatherer = gatherer or RequirementsGatherer()
        self.researcher = researcher or ResearchAdapter()
        self.scorer = scorer or ScoringEngine()
        self.reviewer = reviewer or QualityReviewer()
        self.roadmap = roadmap or ImprovementRoadmap()
        self.brain = brain or Brain.load()
        self.llm = llm or LLMAdapter()

    def run(
        self,
        deck: Deck,
        *,
        context: Optional[Union[Context, Mapping[str, Any]]] = None,
        context_raw: Optional[Mapping[str, Any]] = None,
        online: Optional[bool] = None,
    ) -> ScoreReport:
        """Run the full harness and return a synthesized ScoreReport."""

        # 1. Requirements (gate: stage + audience set).
        if isinstance(context, Context):
            ctx = context
        else:
            raw = dict(context or {})
            if context_raw:
                raw.update(context_raw)
            ctx = self.gatherer.gather(deck, raw=raw)

        # 2. Research (cited + dated; offline-safe).
        research = self.researcher.research(ctx.sector, online=online, brain=self.brain)

        # 3. Scoring (per-slide scores + gaps).
        per_slide, gaps = self.scorer.score(deck, ctx)
        overall, band = ScoringEngine.overall(per_slide, gaps, ctx)

        # 4. Challenge (>= 5 investor objections).
        objections = self.reviewer.review(per_slide, gaps, ctx)

        # 5. Roadmap (slide-level rewrites; every objection addressed).
        roadmap = self.roadmap.build(per_slide, gaps, objections, ctx)

        # 6. Synthesize.
        notes = list(research.notes)
        if research.offline:
            notes.insert(0, "Benchmark currency: research used offline knowledge only.")
        report = ScoreReport(
            company=ctx.company,
            stage=ctx.stage,
            audience=ctx.audience,
            overall_score=overall,
            fundability=band,
            per_slide=per_slide,
            gaps=gaps,
            objections=objections,
            roadmap=roadmap,
            sources=research.sources,
            offline=research.offline,
            notes=notes,
        )
        return report

    # Convenience: render helpers -------------------------------------------
    def render(self, report: ScoreReport, *, fmt: str = "markdown", polish: bool = False) -> str:
        if fmt.lower() == "json":
            return render_json(report)
        summary = self.llm.polish_summary(report) if polish else None
        return render_markdown(report, executive_summary=summary)


def run(
    deck: Union[Deck, Mapping[str, Any], str, Path],
    *,
    context: Optional[Union[Context, Mapping[str, Any], str, Path]] = None,
    online: Optional[bool] = None,
    fmt: str = "markdown",
    polish: bool = False,
) -> Union[ScoreReport, str]:
    """Functional entry point.

    Accepts a Deck, a dict, or a path to a JSON file describing the deck, plus
    optional context (dict, Context, or path). Returns the ScoreReport when
    ``fmt == 'report'``; otherwise returns the rendered string.

    Note: ``context`` must include ``stage`` and ``audience`` (or an ask slide
    from which they can be inferred) — otherwise the requirements gate raises
    ``RequirementsError``.
    """
    pipeline = Pipeline()
    deck_obj = deck if isinstance(deck, Deck) else load_deck(deck)
    ctx_raw: Optional[Mapping[str, Any]] = None
    ctx_obj: Optional[Context] = None
    if isinstance(context, Context):
        ctx_obj = context
    elif isinstance(context, Mapping):
        ctx_raw = context
    elif isinstance(context, (str, Path)):
        ctx_raw = load_context_raw(context)

    report = pipeline.run(deck_obj, context=ctx_obj, context_raw=ctx_raw, online=online)
    if fmt.lower() == "report":
        return report
    return pipeline.render(report, fmt=fmt, polish=polish)
