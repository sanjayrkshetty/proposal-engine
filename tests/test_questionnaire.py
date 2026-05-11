"""Tests for QuestionnaireAgent — mock mode only (no API calls)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("GROQ_API_KEY", "test-key")

import pytest
from agents.questionnaire_agent import QuestionnaireAgent

DUMMY_CONFIG = {"name": "Test Service", "bu": "dfir", "code": "TEST"}

def make_agent():
    return QuestionnaireAgent(DUMMY_CONFIG)


def test_dfir_returns_dict_with_min_keys():
    agent = make_agent()
    result = agent.run(bu="dfir", sub_bu="", client_info={"name": "Test Bank"}, mode="mock")
    assert isinstance(result, dict)
    assert "answers" in result
    assert "scope_context" in result
    assert len(result["answers"]) >= 5


def test_mxdr_returns_valid_structure():
    agent = make_agent()
    result = agent.run(bu="mxdr", client_info={"name": "Corp A"}, mode="mock")
    assert isinstance(result["answers"], dict)
    assert len(result["answers"]) >= 5


def test_dpg_returns_valid_structure():
    agent = make_agent()
    result = agent.run(bu="dpg", client_info={"name": "HealthCo"}, mode="mock")
    assert len(result["answers"]) >= 5


def test_cts_appsec_contains_required_keys():
    agent = make_agent()
    result = agent.run(bu="cts", sub_bu="AppSec",
                       client_info={"name": "FinTech Ltd"}, mode="mock")
    assert isinstance(result["answers"], dict)
    assert len(result["answers"]) >= 5


def test_quantum_returns_valid_structure():
    agent = make_agent()
    result = agent.run(bu="quantum", client_info={"name": "InsureCorp"}, mode="mock")
    assert len(result["answers"]) >= 5


def test_institute_returns_valid_structure():
    agent = make_agent()
    result = agent.run(bu="institute", client_info={"name": "Training Org"}, mode="mock")
    assert len(result["answers"]) >= 5


def test_scope_context_is_string():
    agent = make_agent()
    result = agent.run(bu="dfir", client_info={"name": "Bank X"}, mode="mock")
    assert isinstance(result["scope_context"], str)
