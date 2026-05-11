# Proposal Engine — Audit (Pre-Expansion)

**Date:** 2026-05-11  
**Auditor:** Automated Pre-Expansion Audit

---

## 1. Directory Structure

```
proposal-engine/
├── main.py                   (CLI entry point)
├── requirements.txt          (anthropic>=0.25.0 — MUST replace with groq)
├── README.md
├── DEMO.md
├── config/
│   └── services.yaml         (4 services: DFIR-R, IFI, CA, BAS)
├── agents/
│   ├── __init__.py
│   ├── discovery_agent.py    (uses anthropic.Anthropic)
│   ├── scoping_agent.py      (uses anthropic.Anthropic)
│   └── proposal_agent.py     (uses anthropic.Anthropic)
└── outputs/
    └── .gitkeep
```

---

## 2. Current Services Registered

| Code   | Name                          | BU   | Type    |
|--------|-------------------------------|------|---------|
| DFIR-R | DFIR Retainer                 | DFIR | Retainer |
| IFI    | Internal Forensic Investigation | DFIR | Project |
| CA     | Compromise Assessment         | DFIR | Project |
| BAS    | Breach and Attack Simulation  | DFIR | Project |

**Coverage:** 1 BU only (DFIR). Missing: MXDR, DPG, CTS, Institute, Quantum.

---

## 3. Agent Assessment

### discovery_agent.py
- **Status:** Functional
- **Issue:** Uses `anthropic.Anthropic` — must migrate to `groq.Groq`
- **Issue:** Hardcoded model `claude-haiku-4-5-20251001` — must replace with `llama-3.3-70b-versatile`
- **Pattern:** `__init__` creates client, `.run()` builds prompt → calls API → parses JSON
- **Returns:** `{"data": dict, "markdown": str}`

### scoping_agent.py
- **Status:** Functional
- **Issue:** Uses `anthropic.Anthropic` — must migrate to `groq.Groq`
- **Issue:** Hardcoded model — must replace
- **Returns:** `{"data": dict, "markdown": str}`

### proposal_agent.py
- **Status:** Functional
- **Issue:** Uses `anthropic.Anthropic` — must migrate to `groq.Groq`
- **Issue:** Uses `claude-sonnet-4-6` model — must replace
- **Returns:** `{"markdown": str, "data": dict}`

---

## 4. main.py Assessment

- **CLI Framework:** Click
- **Service choices:** Hardcoded `type=click.Choice(["DFIR-R", "IFI", "CA", "BAS"])` — must make dynamic from YAML
- **Pipeline:** DiscoveryAgent → ScopingAgent → ProposalAgent (3 phases)
- **Output:** `outputs/YYYY-MM-DD_ClientName_ServiceCode/`
- **Missing:** No `--bu`, `--tier`, `--gam`, `--region`, `--exec-summary` flags
- **Missing:** No QuestionnaireAgent or PricingAgent in pipeline
- **Missing:** No proposal sequence number tracking

---

## 5. requirements.txt Assessment

```
anthropic>=0.25.0    # MUST replace with groq>=0.4.0
pyyaml>=6.0
jinja2>=3.1
click>=8.1
rich>=13.0
python-dateutil>=2.9
```

**Missing:** `groq>=0.4.0`, `openpyxl>=3.1`, `pytest>=7.0`

---

## 6. Missing Components

| Component | Status | Required |
|-----------|--------|----------|
| base_agent.py | MISSING | All agents must inherit |
| questionnaire_agent.py | MISSING | Phase 0 of pipeline |
| pricing_agent.py | MISSING | Phase 3 of pipeline |
| gam_agent.py | MISSING | Billing contact injection |
| bu/ directory (6 BUs) | MISSING | Per-BU config + questionnaire |
| templates/ (14 files) | MISSING | Proposal rendering |
| config/gam_list.yaml | MISSING | GAM contacts by region |
| config/pricing_baseline.yaml | MISSING | Regional ACV baselines |
| config/proposal_sequences.json | MISSING | Sequence tracking |
| reports/pipeline_report.py | MISSING | Markdown + Excel reports |
| tests/ (3 files) | MISSING | pytest suite |

---

## 7. Expansion Scope

- **BUs to add:** MXDR, DPG, CTS, Institute, Quantum (5 new BUs beyond existing DFIR)
- **New services:** 18 additional service codes across 6 BUs
- **New agents:** 3 (QuestionnaireAgent, PricingAgent, GAMAgent)
- **Templates:** 14 total
- **Tests:** 3 test files, all must pass pytest
- **API migration:** anthropic → groq (full swap)

---

## 8. Risk Flags

1. **API swap:** All 3 existing agents use Anthropic SDK — full migration required
2. **Service expansion:** CLI service choice validation must be made dynamic
3. **Sequence numbers:** proposal_sequences.json must persist across runs (file I/O, not in-memory)
4. **Pricing:** No pricing engine exists — must build from codebook.yaml files
5. **Discount gate:** Must write file + print warning (non-blocking)
6. **Template placeholders:** Exact names required — `{{CLIENT_NAME}}`, `{{EXEC_SUMMARY}}`, etc.
