"""Discovery Agent — extracts pain points, regulatory drivers, and environment details."""
import os
import json
import anthropic

DISCOVERY_PROMPT = """You are a DFIR pre-sales discovery specialist at Proposal Engine.
Given client information for a {service_name} engagement, generate a structured discovery brief.

Client: {client_name}
Industry: {industry}
Size: {size}

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


class DiscoveryAgent:
    def __init__(self, service_config: dict):
        self.config = service_config
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def run(self, client_info: dict) -> dict:
        prompt = DISCOVERY_PROMPT.format(
            service_name=self.config["name"],
            service_description=self.config["description"],
            client_name=client_info.get("name") or "Unknown",
            industry=client_info.get("industry") or "Financial Services",
            size=client_info.get("size") or "Mid-market (500-5000 employees)",
        )

        msg = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        data = json.loads(raw)

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
