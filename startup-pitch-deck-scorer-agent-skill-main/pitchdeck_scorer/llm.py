"""Optional LLM adapter for narrative augmentation.

This adapter is **production-ready but opt-in**. The deterministic pipeline
runs fully without it; when ``OPENAI_API_KEY`` is present and the ``openai``
package is installed, callers can request narrative polish on top of the
deterministic scores. The adapter never mutates the scored numbers — it only
rewrites prose. It is lazily imported so the core package stays dependency
light and tests never hit the network.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from .models import ScoreReport


@dataclass
class LLMConfig:
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "gpt-4o-mini"

    @classmethod
    def from_env(cls) -> LLMConfig:
        return cls(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE"),
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        )

    def is_configured(self) -> bool:
        return bool(self.api_key)


class LLMAdapter:
    """Augment a deterministic report's prose via an OpenAI-compatible API."""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig.from_env()

    def is_available(self) -> bool:
        if not self.config.is_configured():
            return False
        try:
            import openai  # noqa: F401
        except Exception:
            return False
        return True

    def polish_summary(self, report: ScoreReport, *, max_tokens: int = 350) -> str:
        """Return an investor-tone executive summary paragraph.

        Falls back to a deterministic template if the LLM is unavailable so
        this method is always safe to call in the pipeline.
        """
        if not self.is_available():
            return self._fallback_summary(report)

        try:
            from openai import OpenAI
        except Exception:
            return self._fallback_summary(report)

        prompt = self._build_prompt(report)
        try:
            client = (
                OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
                if self.config.base_url
                else OpenAI(api_key=self.config.api_key)
            )
            resp = client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a seasoned seed/Series-A investor writing a tight executive summary.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            text = (resp.choices[0].message.content or "").strip()
            return text or self._fallback_summary(report)
        except Exception:
            return self._fallback_summary(report)

    # ------------------------------------------------------------------
    def _build_prompt(self, report: ScoreReport) -> str:
        lines = [
            f"Company: {report.company}",
            f"Stage: {report.stage}",
            f"Overall score: {report.overall_score}/100 — {report.fundability}",
            f"Gaps: {', '.join(g.kind.value for g in report.gaps) or 'none'}",
            f"Objections: {len(report.objections)}",
        ]
        return "Write a 3-sentence investor executive summary for this pitch-deck scorecard.\n" + "\n".join(lines)

    def _fallback_summary(self, report: ScoreReport) -> str:
        gap_word = f" with {len(report.gaps)} missing canonical slide(s)" if report.gaps else ""
        return (
            f"{report.company} ({report.stage}) scores {report.overall_score}/100 "
            f"overall — {report.fundability}{gap_word}. "
            f"The deck faces {len(report.objections)} substantive investor objections; "
            f"address the roadmap items in priority order before partner review."
        )
