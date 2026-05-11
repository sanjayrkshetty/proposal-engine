"""Critic Agent — adversarial reviewer that challenges agent output to improve quality."""
from .base_agent import BaseAgent, MODEL_FAST

CRITIQUE_PROMPT = """You are a sceptical senior consultant reviewing a pre-sales document.
Your job is to find weaknesses — not to be positive.

Document type: {doc_type}
Content to review:
---
{content}
---

Find exactly 3 weaknesses from this list of failure modes:
- Vague claim with no evidence or metric (e.g. "industry-leading" without proof)
- Missing specificity (scope too broad, no concrete deliverable named)
- Logical gap (conclusion doesn't follow from stated facts)
- Unsupported timeline or effort estimate
- Missing risk acknowledgement (assumes everything goes smoothly)
- Regulatory claim without citation

Return JSON only:
{{
  "critiques": [
    {{"issue": "one-line label", "quote": "exact phrase from content", "fix": "specific rewrite suggestion"}},
    {{"issue": "...", "quote": "...", "fix": "..."}},
    {{"issue": "...", "quote": "...", "fix": "..."}}
  ],
  "overall_score": <integer 1-10>,
  "strongest_section": "<one phrase>"
}}"""

INCORPORATE_PROMPT = """You wrote this executive summary:
---
{original}
---

A critic flagged these two issues:
1. {critique_1}
   Fix: {fix_1}
2. {critique_2}
   Fix: {fix_2}

Rewrite the executive summary incorporating both fixes. Keep it 3-4 sentences.
Output ONLY the rewritten text."""


class CriticAgent(BaseAgent):
    def __init__(self, service_config: dict):
        super().__init__(service_config)
        self.model = MODEL_FAST

    def run(self, content: str, doc_type: str = "discovery brief") -> dict:
        prompt = CRITIQUE_PROMPT.format(doc_type=doc_type, content=content[:3000])
        try:
            result = self.call_llm_json(prompt, max_tokens=600, temperature=0.1)
        except Exception:
            result = {"critiques": [], "overall_score": 5, "strongest_section": ""}
        return result

    def improve_exec_summary(self, original: str, critiques: list) -> str:
        if not critiques or len(critiques) < 2:
            return original
        prompt = INCORPORATE_PROMPT.format(
            original=original,
            critique_1=critiques[0].get("issue", ""),
            fix_1=critiques[0].get("fix", ""),
            critique_2=critiques[1].get("issue", ""),
            fix_2=critiques[1].get("fix", ""),
        )
        try:
            return self.call_llm(prompt, max_tokens=300, temperature=0.3)
        except Exception:
            return original
