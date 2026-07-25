---
name: sub-improvement-roadmap
description: Produce slide-level rewrites and missing-slide additions to raise the deck's score and answer investor objections.
---

## Purpose
Convert scores + objections into concrete, slide-specific deck edits.

## Inputs
Per-slide scores, gaps, investor objections, context.

## Process
1. Prioritize lowest-scoring and highest-objection slides.
2. For each weak slide, give a before → after rewrite (headline + key content) tied to the framework, using detector-specific guidance (top-down TAM → bottom-up rewrite; vanity metrics → revenue/retention rewrite; hockey-stick → bottom-up build; no moat → add defensibility).
3. Add any missing canonical slide with a content outline.
4. Tag each item effort (S/M/L) and impact (Low/Med/High).
5. Ensure **every raised objection is addressed** somewhere in the roadmap (link an existing item or backfill a dedicated one).

## Outputs
Slide-level roadmap: slide → before/after, effort, impact, objection addressed.

## Quality Gate
- Each item is slide-specific with before/after + effort/impact.
- Every investor objection is addressed.

## Implementation
`pitchdeck_scorer.improvement_roadmap.ImprovementRoadmap.build(per_slide, gaps, objections, ctx)`
→ `list[RoadmapItem]`.