"""Discovery Agent — extracts pain points, regulatory drivers, and environment details."""
import os
from .base_agent import BaseAgent

os.environ.setdefault("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")

DISCOVERY_PROMPT = """You are a Proposal Engine pre-sales discovery specialist.
Given client information for a {service_name} engagement, generate a structured discovery brief.

Client: {client_name}
Industry: {industry}
Size: {size}
Region: {region}
Exec Summary Context: {exec_summary}

Service: {service_name} — {service_description}

Output a JSON object with exactly these keys:
{{
  "pain_points": ["list of 3-5 likely pain points for this client/industry"],
  "regulatory_drivers": ["list of applicable regulations/standards"],
  "environment_assumptions": ["list of environment assumptions"],
  "discovery_questions": ["top 5 discovery questions to ask"],
  "urgency_signals": ["signals that indicate urgency or buying trigger"],
  "recommended_tier": "Essential|Enterprise|Elite",
  "tier_rationale": "one sentence explaining the tier recommendation"
}}

Output ONLY the JSON, no other text."""


class DiscoveryAgent(BaseAgent):
    def run(self, client_info: dict) -> dict:
        prompt = DISCOVERY_PROMPT.format(
            service_name=self.config["name"],
            service_description=self.config.get("description", ""),
            client_name=client_info.get("name") or "Unknown",
            industry=client_info.get("industry") or "Financial Services",
            size=client_info.get("size") or "Mid-market (500-5000 employees)",
            region=client_info.get("region") or "India",
            exec_summary=client_info.get("exec_summary") or "Not provided",
        )

        data = self.call_llm_json(prompt, max_tokens=1024)
        markdown = self._to_markdown(data, client_info)
        return {"data": data, "markdown": markdown}

    def _to_markdown(self, data: dict, client_info: dict) -> str:
        c = client_info.get("name") or "Client"
        lines = [
            f"# Discovery Brief — {c}",
            f"**Service:** {self.config['name']}  ",
            f"**Recommended Tier:** {data.get('recommended_tier', 'Enterprise')} — {data.get('tier_rationale', '')}",
            "",
            "## Pain Points",
            *[f"- {p}" for p in data.get("pain_points", [])],
            "",
            "## Regulatory Drivers",
            *[f"- {r}" for r in data.get("regulatory_drivers", [])],
            "",
            "## Environment Assumptions",
            *[f"- {e}" for e in data.get("environment_assumptions", [])],
            "",
            "## Top Discovery Questions",
            *[f"{i+1}. {q}" for i, q in enumerate(data.get("discovery_questions", []))],
            "",
            "## Urgency Signals",
            *[f"- {u}" for u in data.get("urgency_signals", [])],
        ]
        return "\n".join(lines)
