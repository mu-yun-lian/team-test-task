"""Report rendering: Markdown + JSON for the final synthesized scorecard.

The Markdown renderer uses a small Jinja2 template so the output format is
easy to audit and override. JSON rendering is just ``ScoreReport``'s pydantic
``model_dump_json`` with enums-as-values for portability.
"""

from __future__ import annotations

from typing import Optional

from .models import ScoreReport

_MARKDOWN_TEMPLATE = r"""# Pitch Deck Score Report — {{ company }} ({{ stage }})

## 1. Summary
- **Overall score:** {{ overall_score }}/100
- **Fundability verdict:** {{ fundability }}
- **Audience:** {{ audience }}
- **Mode:** {{ "Offline (SECOND-KNOWLEDGE-BRAIN only)" if offline else "Online research used" }}
- **Gaps:** {{ gaps_count }} missing canonical slide(s)
- **Objections raised:** {{ objections_count }}
{% if executive_summary %}

> {{ executive_summary }}
{% endif %}

## 2. Per-Slide Scores
| Slide | Persuasion | Logic | Clarity | Weighted | Status |
|-------|-----------:|------:|--------:|---------:|--------|
{% for s in per_slide -%}
| {{ s.label }} | {{ s.axes.persuasion }} | {{ s.axes.logic }} | {{ s.axes.clarity }} | {{ s.weighted }} | {{ "present" if s.present else "missing" }} |
{% endfor %}

### Findings detail
{% for s in per_slide -%}
{% if s.findings -%}
- **{{ s.label }} ({{ s.weighted }}/100):**
{% for f in s.findings -%}
  - [{{ f.severity }}] {{ f.message }}
{% endfor -%}
{% endif -%}
{% else -%}
_(no findings)_
{% endfor %}

## 3. Gaps
{% if gaps -%}
{% for g in gaps -%}
- **{{ g.kind.value }}:** {{ g.reason }}
{% endfor -%}
{% else -%}
_None — all canonical slides present._
{% endif %}

## 4. Investor Objections ({{ objections_count }})
{% for o in objections -%}
{{ loop.index }}. **[{{ o.severity }}]** {{ o.question }}
   - _Slide:_ {{ o.slide_kind.value if o.slide_kind else "general" }}
   - _Resolving evidence:_ {{ o.resolving_evidence }}
{% endfor %}

## 5. Fix Roadmap
{% for r in roadmap -%}
{{ loop.index }}. **{{ r.slide_kind.value }}** — effort: {{ r.effort }} · impact: {{ r.impact }}{% if r.objection_addressed %} · addresses: "{{ r.objection_addressed }}"{% endif %}
   - _Before:_ {{ r.before }}
   - _After:_ {{ r.after }}
{% endfor %}

## 6. Sources & Currency
{% if offline -%}
- ⚠️ Offline limitation: live web research was unavailable; benchmarks are drawn from SECOND-KNOWLEDGE-BRAIN.md and dated normative anchors.
{% endif -%}
{% for src in sources -%}
- {{ src }}
{% endfor %}

{% if notes -%}
### Notes
{% for n in notes -%}
- {{ n }}
{% endfor -%}
{% endif -%}
"""


def render_markdown(report: ScoreReport, executive_summary: Optional[str] = None) -> str:
    from jinja2 import Template

    env = {
        "company": report.company,
        "stage": report.stage.value,
        "audience": report.audience.value,
        "overall_score": report.overall_score,
        "fundability": report.fundability.value,
        "offline": report.offline,
        "gaps_count": len(report.gaps),
        "objections_count": len(report.objections),
        "per_slide": report.per_slide,
        "gaps": report.gaps,
        "objections": report.objections,
        "roadmap": report.roadmap,
        "sources": report.sources,
        "notes": report.notes,
        "executive_summary": executive_summary,
    }
    return Template(_MARKDOWN_TEMPLATE).render(**env)


def render_json(report: ScoreReport) -> str:
    """JSON with enums serialized as their string values."""
    return report.model_dump_json(indent=2, by_alias=False)
