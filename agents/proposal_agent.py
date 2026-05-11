"""Proposal Agent — renders full proposal from template with all placeholders filled."""
import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from .base_agent import BaseAgent

EXEC_SUMMARY_PROMPT = """You are a senior proposal writer for a professional cybersecurity services firm.
Write a compelling executive summary for the following engagement.

Service: {service_name}
Client: {client_name}
Industry: {industry}
Tier: {tier}
Region: {region}
Context provided: {exec_summary_context}

Pain points: {pain_points}
Regulatory drivers: {regulatory_drivers}

Write 3-4 sentences that are business-outcome focused, reference the client's specific context,
and position the firm as the trusted partner. Be professional and concise.
Output ONLY the executive summary text, no headers."""


class ProposalAgent(BaseAgent):
    def __init__(self, service_config: dict):
        super().__init__(service_config)
        from .base_agent import MODEL_PRO
        self.model = MODEL_PRO  # proposal quality needs the big model

    def run(self, brief_data: dict, scope_data: dict, client_info: dict,
            pricing_data: dict = None, gam_data: dict = None,
            proposal_number: str = "PROP-0001") -> dict:

        tier = brief_data.get("recommended_tier", "Enterprise")
        service_code = self.config.get("code", "UNKNOWN")
        bu = self.config.get("bu", "dfir")
        template_file = self.config.get("template", "")
        company_name = os.environ.get("COMPANY_NAME", "Proposal Engine")

        exec_summary_context = client_info.get("exec_summary") or ""
        exec_summary = self._generate_exec_summary(brief_data, scope_data, client_info, tier, exec_summary_context)

        pricing_table = ""
        if pricing_data:
            pricing_table = pricing_data.get("pricing_table_md", "")
        if not pricing_table:
            pricing_table = self._build_fallback_pricing(scope_data)

        billing_contact = ""
        if gam_data:
            billing_contact = gam_data.get("billing_block", "")
        if not billing_contact:
            billing_contact = "accounts@proposalengine.io | +1-800-000-0000"

        assumptions = "\n".join([f"- {a}" for a in scope_data.get("assumptions", [
            "Client provides access to relevant systems within 2 business days of engagement start",
            "All in-scope systems are within the agreed network perimeter",
            "Client point of contact available during engagement",
        ])])

        scope_context = client_info.get("scope_context") or self._build_scope_context(brief_data, scope_data)

        today = datetime.now()
        valid_until = today + timedelta(days=self.config.get("default_validity_days", 30))

        template_path = Path(f"templates/{bu}/{template_file}") if template_file else None
        if template_path and template_path.exists():
            template_content = template_path.read_text(encoding="utf-8")
        else:
            template_content = self._default_template()

        replacements = {
            "{{CLIENT_NAME}}": client_info.get("name") or "Client",
            "{{EXEC_SUMMARY}}": exec_summary,
            "{{PROPOSAL_NO}}": proposal_number,
            "{{DATE}}": today.strftime("%d %B %Y"),
            "{{VALID_UNTIL}}": valid_until.strftime("%d %B %Y"),
            "{{BILLING_CONTACT}}": billing_contact,
            "{{SCOPE_CONTEXT}}": scope_context,
            "{{PRICING_TABLE}}": pricing_table,
            "{{SERVICE_NAME}}": self.config.get("name", service_code),
            "{{SLA_TIER}}": self.config.get("sla_tier", tier),
            "{{ASSUMPTIONS}}": assumptions,
            "{{REGION}}": client_info.get("region") or "Global",
            "{{COMPANY_NAME}}": company_name,
        }

        rendered = template_content
        for placeholder, value in replacements.items():
            rendered = rendered.replace(placeholder, str(value))

        return {
            "markdown": rendered,
            "data": {
                "proposal_text": rendered,
                "proposal_number": proposal_number,
                "client": client_info.get("name"),
                "service": service_code,
                "tier": tier,
                "region": client_info.get("region"),
                "exec_summary": exec_summary,
            }
        }

    def _generate_exec_summary(self, brief_data: dict, scope_data: dict,
                                client_info: dict, tier: str, exec_summary_context: str) -> str:
        if exec_summary_context and len(exec_summary_context) > 50:
            prompt = EXEC_SUMMARY_PROMPT.format(
                service_name=self.config.get("name", ""),
                client_name=client_info.get("name") or "Client",
                industry=client_info.get("industry") or "Financial Services",
                tier=tier,
                region=client_info.get("region") or "Global",
                exec_summary_context=exec_summary_context,
                pain_points="; ".join(brief_data.get("pain_points", [])[:3]),
                regulatory_drivers="; ".join(brief_data.get("regulatory_drivers", [])[:2]),
            )
            return self.call_llm(prompt, max_tokens=512, temperature=0.3)
        else:
            pain_pts = "; ".join(brief_data.get("pain_points", [])[:2])
            regs = "; ".join(brief_data.get("regulatory_drivers", [])[:2])
            company_name = os.environ.get("COMPANY_NAME", "Proposal Engine")
            return (
                f"{client_info.get('name', 'Your organisation')} faces increasing cybersecurity challenges "
                f"in the {client_info.get('industry', 'Financial Services')} sector, including {pain_pts}. "
                f"Regulatory obligations under {regs} require a structured and expert-led response. "
                f"{company_name} proposes a {tier}-tier {self.config.get('name', 'security engagement')} "
                f"to address these imperatives and strengthen your security posture."
            )

    def _build_scope_context(self, brief_data: dict, scope_data: dict) -> str:
        lines = []
        in_scope = scope_data.get("in_scope", [])
        if in_scope:
            lines.append("**In Scope:**")
            for item in in_scope[:6]:
                lines.append(f"- {item}")
        out_scope = scope_data.get("out_of_scope", [])
        if out_scope:
            lines.append("\n**Out of Scope:**")
            for item in out_scope[:4]:
                lines.append(f"- {item}")
        return "\n".join(lines)

    def _build_fallback_pricing(self, scope_data: dict) -> str:
        p = scope_data.get("indicative_price_range", {})
        low = p.get("low", 0)
        high = p.get("high", 0)
        currency = p.get("currency", "INR")
        return (
            f"| Item | Amount |\n"
            f"|------|--------|\n"
            f"| Indicative Investment | {currency} {low:,} – {high:,} |\n"
            f"\n*Final pricing subject to scoping confirmation.*"
        )

    def _default_template(self) -> str:
        return """# {{COMPANY_NAME}}
## Proposal for {{SERVICE_NAME}}

**Prepared for:** {{CLIENT_NAME}}
**Proposal No:** {{PROPOSAL_NO}}
**Date:** {{DATE}}
**Valid Until:** {{VALID_UNTIL}}
**Region:** {{REGION}}

---

## Executive Summary

{{EXEC_SUMMARY}}

---

## About {{COMPANY_NAME}}

{{COMPANY_NAME}} is a professional cybersecurity services firm specialising in incident response, forensics, compliance, and managed security. Our team of certified security professionals holds GCFA, GCIH, CREST, CISSP, and CISM credentials, delivering world-class security outcomes for financial institutions, healthcare organisations, and critical infrastructure operators.

---

## Scope of Services

{{SCOPE_CONTEXT}}

---

## Pricing & Commercials

{{PRICING_TABLE}}

SLA Tier: {{SLA_TIER}}

---

## Assumptions

{{ASSUMPTIONS}}

---

## Terms & Conditions

1. This proposal is valid until **{{VALID_UNTIL}}** from the date of issue.
2. Pricing is exclusive of applicable taxes (GST/VAT) unless otherwise stated.
3. Any scope changes post-engagement commencement are subject to change-order procedures.
4. {{COMPANY_NAME}} retains the right to withdraw or amend this proposal if material information is found to be inaccurate.
5. Payment terms: 50% advance upon engagement confirmation; 50% on delivery of final report.
6. Confidentiality: Both parties agree to maintain the confidentiality of all information exchanged.
7. Data handling: All client data processed during the engagement is handled per ISO 27001-certified data handling procedures.
8. Governing law: This agreement is governed by the laws of the applicable jurisdiction unless otherwise agreed.

---

## Billing & Contact

{{BILLING_CONTACT}}
"""
