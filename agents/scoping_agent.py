"""Scoping Agent — estimates effort, defines in/out scope, flags commercial risks."""
import os
import json
import anthropic

SCOPING_PROMPT = """You are a DFIR scoping specialist at Proposal Engine.
Given a discovery brief and client context, produce a detailed scope estimate for a {service_name} engagement.

Client: {client_name} | Industry: {industry} | Size: {size}
Tier: {tier}

Discovery brief summary:
{brief_summary}

Output a JSON object with exactly these keys:
{{
  "effort_days": {{
    "onsite": number,
    "remote": number,
    "reporting": number,
    "total": number
  }},
  "in_scope": ["list of 5-8 in-scope items"],
  "out_of_scope": ["list of 3-5 explicit exclusions"],
  "deliverables": ["list of deliverables"],
  "commercial_risks": ["list of 2-4 scope creep / commercial risks to flag"],
  "sla_commitments": {{
    "initial_response": "e.g. 4 hours",
    "containment": "e.g. 24 hours",
    "report_delivery": "e.g. 5 business days"
  }},
  "indicative_price_range": {{"low": number, "high": number, "currency": "USD"}}
}}

Output ONLY the JSON, no other text."""


class ScopingAgent:
    def __init__(self, service_config: dict):
        self.config = service_config
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def run(self, brief_data: dict, client_info: dict) -> dict:
        tier = brief_data.get("recommended_tier", "Enterprise")
        brief_summary = "\n".join([
            f"Pain points: {', '.join(brief_data.get('pain_points', [])[:3])}",
            f"Regulations: {', '.join(brief_data.get('regulatory_drivers', [])[:3])}",
            f"Urgency: {', '.join(brief_data.get('urgency_signals', [])[:2])}",
        ])

        prompt = SCOPING_PROMPT.format(
            service_name=self.config["name"],
            client_name=client_info.get("name") or "Unknown",
            industry=client_info.get("industry") or "Financial Services",
            size=client_info.get("size") or "Mid-market",
            tier=tier,
            brief_summary=brief_summary,
        )

        msg = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        data = json.loads(msg.content[0].text.strip())
        markdown = self._to_markdown(data, client_info, tier)
        return {"data": data, "markdown": markdown}

    def _to_markdown(self, data: dict, client_info: dict, tier: str) -> str:
        e = data.get("effort_days", {})
        p = data.get("indicative_price_range", {})
        sla = data.get("sla_commitments", {})
        lines = [
            f"# Scope Estimate — {client_info.get('name', 'Client')}",
            f"**Service:** {self.config['name']} — {tier} Tier",
            "",
            "## Effort Estimate",
            f"| Phase | Days |",
            f"|-------|------|",
            f"| On-site | {e.get('onsite', 0)} |",
            f"| Remote | {e.get('remote', 0)} |",
            f"| Reporting | {e.get('reporting', 0)} |",
            f"| **Total** | **{e.get('total', 0)}** |",
            "",
            f"**Indicative Price:** ${p.get('low', 0):,} – ${p.get('high', 0):,} {p.get('currency', 'USD')}",
            "",
            "## In Scope",
            *[f"- {i}" for i in data.get("in_scope", [])],
            "",
            "## Out of Scope",
            *[f"- {o}" for o in data.get("out_of_scope", [])],
            "",
            "## Deliverables",
            *[f"- {d}" for d in data.get("deliverables", [])],
            "",
            "## SLA Commitments",
            f"- Initial response: {sla.get('initial_response', 'TBD')}",
            f"- Containment: {sla.get('containment', 'TBD')}",
            f"- Report delivery: {sla.get('report_delivery', 'TBD')}",
            "",
            "## Commercial Risks",
            *[f"⚠ {r}" for r in data.get("commercial_risks", [])],
        ]
        return "\n".join(lines)
