"""Tests for PricingAgent — no API calls needed (pure codebook math)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("GROQ_API_KEY", "test-key")

import pytest
from agents.pricing_agent import PricingAgent

DUMMY_CONFIG = {"name": "Test", "bu": "dfir", "code": "DFIR-R-ENT"}

def make_agent():
    return PricingAgent(DUMMY_CONFIG)


def test_dfir_ent_unit_price_calculation():
    agent = make_agent()
    result = agent.build_pricing_table("DFIR-R-ENT", qty=12, region="India-South", discount_pct=0)
    assert result["subtotal_inr"] == 900000 * 12
    assert result["total_inr"] == 900000 * 12


def test_dfir_ess_unit_price():
    agent = make_agent()
    result = agent.build_pricing_table("DFIR-R-ESS", qty=3, region="India-South", discount_pct=0)
    assert result["subtotal_inr"] == 450000 * 3


def test_discount_gate_fires_on_excess():
    agent = make_agent()
    import io
    from contextlib import redirect_stdout
    f = io.StringIO()
    result = agent.build_pricing_table("DFIR-R-ESS", qty=3, region="India-South", discount_pct=15)
    assert result.get("discount_approval_required") is True


def test_discount_within_threshold_no_flag():
    agent = make_agent()
    result = agent.build_pricing_table("DFIR-R-ESS", qty=3, region="India-South", discount_pct=5)
    assert result.get("discount_approval_required") is not True


def test_inflation_alert_fires_when_acv_exceeds_baseline():
    agent = make_agent()
    # Baseline for DFIR India-South ~5.4M — pass 7M (30% above) to trigger alert
    result = agent.check_inflation(acv_inr=7_000_000, region="India-South", bu="DFIR")
    assert result["alert"] is True
    assert result["deviation_pct"] > 20


def test_inflation_no_alert_within_threshold():
    agent = make_agent()
    # Below baseline — no alert
    result = agent.check_inflation(acv_inr=720_000, region="India-South", bu="DFIR")
    assert result["alert"] is False


def test_pricing_table_markdown_format():
    agent = make_agent()
    result = agent.build_pricing_table("DFIR-R-ENT", qty=6, region="India-South")
    table_md = agent.format_pricing_table(result)
    assert "|" in table_md
    assert "Total" in table_md
