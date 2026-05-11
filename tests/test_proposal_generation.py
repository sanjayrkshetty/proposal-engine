"""Tests for proposal template rendering — no API calls needed."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("GROQ_API_KEY", "test-key")

import re
import pytest
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

ALL_TEMPLATES = list(TEMPLATE_DIR.rglob("*.md"))

REQUIRED_PLACEHOLDERS = [
    "{{CLIENT_NAME}}",
    "{{PROPOSAL_NO}}",
    "{{DATE}}",
    "{{BILLING_CONTACT}}",
    "{{PRICING_TABLE}}",
    "{{SERVICE_NAME}}",
]

PROPOSAL_NO_PATTERNS = {
    "dfir": r"PROP-[A-Z]+-\d{4}-\d{4}",
    "default": r"PROP-[A-Z]+-\d{4}-\d{4}",
}

FULL_PLACEHOLDER_SET = {
    "{{CLIENT_NAME}}": "Acme Corp",
    "{{EXEC_SUMMARY}}": "Test executive summary for unit testing.",
    "{{PROPOSAL_NO}}": "PROP-2026-INDIAS-0001",
    "{{DATE}}": "11 May 2026",
    "{{VALID_UNTIL}}": "10 June 2026",
    "{{BILLING_CONTACT}}": "Test GAM | test.gam@sisainfosec.com",
    "{{SCOPE_CONTEXT}}": "Test scope context.",
    "{{PRICING_TABLE}}": "| Item | Price |\n|------|-------|\n| Test | ₹100 |",
    "{{SERVICE_NAME}}": "Test Service",
    "{{SLA_TIER}}": "Enterprise",
    "{{ASSUMPTIONS}}": "- Standard assumptions apply",
    "{{REGION}}": "India-South",
    "{{COMPANY_NAME}}": "Proposal Engine",
}


def render_template(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    for ph, val in FULL_PLACEHOLDER_SET.items():
        content = content.replace(ph, val)
    return content


@pytest.mark.parametrize("template_path", ALL_TEMPLATES)
def test_template_renders_without_error(template_path):
    rendered = render_template(template_path)
    assert rendered  # non-empty


@pytest.mark.parametrize("template_path", ALL_TEMPLATES)
def test_template_contains_client_name_after_render(template_path):
    rendered = render_template(template_path)
    assert "Acme Corp" in rendered


@pytest.mark.parametrize("template_path", ALL_TEMPLATES)
def test_template_contains_proposal_no_after_render(template_path):
    rendered = render_template(template_path)
    assert "PROP-2026-INDIAS-0001" in rendered


@pytest.mark.parametrize("template_path", ALL_TEMPLATES)
def test_template_contains_billing_contact_after_render(template_path):
    rendered = render_template(template_path)
    assert "test.gam@sisainfosec.com" in rendered


@pytest.mark.parametrize("template_path", ALL_TEMPLATES)
def test_no_unrendered_placeholders_remain(template_path):
    rendered = render_template(template_path)
    remaining = re.findall(r"\{\{[A-Z_]+\}\}", rendered)
    assert remaining == [], f"Unrendered placeholders in {template_path.name}: {remaining}"


def test_template_count_matches_expected():
    assert len(ALL_TEMPLATES) >= 14, f"Expected ≥14 templates, found {len(ALL_TEMPLATES)}"
