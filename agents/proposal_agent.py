"""Proposal Agent — generates full proposal markdown: exec summary → pricing."""
import os
import anthropic

PROPOSAL_PROMPT = """You are a senior DFIR proposal writer at SISA Information Security.
Write a complete, professional pre-sales proposal for the following engagement.

Service: {service_name}
Client: {client_name} | Industry: {industry} | Tier: {tier}

Discovery findings:
- Pain points: {pain_points}
- Regulatory drivers: {regulatory_drivers}

Scope:
- In scope: {in_scope}
- Total effort: {effort_days} days
- Price range: {price_range}
- SLAs: {slas}

Deliverables: {deliverables}

Write a complete proposal with these sections (use markdown headers):
1. Executive Summary (3-4 sentences, business-outcome focused)
2. Understanding of Your Requirements (reference the specific pain points and regulatory context)
3. Our Approach (methodology for this service)
4. Scope of Work (in-scope / out-of-scope table)
5. Deliverables
6. Team & Credentials (reference GCFA, GCIH, CREST certifications generically)
7. SLA Commitments
8. Investment (pricing table with tier options)
9. Why SISA (3-4 differentiators)
10. Next Steps

Be specific, professional, and concise. Total length 600-900 words."""


class ProposalAgent:
    def __init__(self, service_config: dict):
        self.config = service_config
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def run(self, brief_data: dict, scope_data: dict, client_info: dict) -> dict:
        e = scope_data.get("effort_days", {})
        p = scope_data.get("indicative_price_range", {})
        sla = scope_data.get("sla_commitments", {})

        prompt = PROPOSAL_PROMPT.format(
            service_name=self.config["name"],
            client_name=client_info.get("name") or "Client",
            industry=client_info.get("industry") or "Financial Services",
            tier=brief_data.get("recommended_tier", "Enterprise"),
            pain_points="; ".join(brief_data.get("pain_points", [])[:3]),
            regulatory_drivers="; ".join(brief_data.get("regulatory_drivers", [])[:3]),
            in_scope="; ".join(scope_data.get("in_scope", [])[:5]),
            effort_days=e.get("total", 0),
            price_range=f"${p.get('low', 0):,}–${p.get('high', 0):,} {p.get('currency', 'USD')}",
            slas=f"Response {sla.get('initial_response','TBD')}, Report {sla.get('report_delivery','TBD')}",
            deliverables="; ".join(scope_data.get("deliverables", [])[:4]),
        )

        msg = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        markdown = msg.content[0].text.strip()
        return {"markdown": markdown, "data": {"proposal_text": markdown}}
