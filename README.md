# Proposal Engine

> **Production multi-agent pipeline that automates the full pre-sales cycle — discovery → scoping → pricing → proposal — across 6 business units and 22 services.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=flat-square&logo=streamlit)](https://proposal-engine.streamlit.app)
[![Tests](https://img.shields.io/badge/Tests-90%2F90%20passing-00d97e?style=flat-square)](tests/)
[![Model](https://img.shields.io/badge/Groq-Llama%203.3--70b-f97316?style=flat-square)](https://groq.com)
[![Deploy](https://img.shields.io/badge/Deploy-Streamlit%20Cloud-FF4B4B?style=flat-square)](https://streamlit.io/cloud)

---

## What it does

A pre-sales consultant spends 3–6 hours per proposal: discovery call notes, scoping, pricing lookup, formatting. This pipeline does it in under 90 seconds.

Input: client name, industry, size, region, service code.
Output: a complete, client-ready proposal markdown — exec summary, scope, methodology, pricing table, assumptions, SLAs.

---

## Architecture

```
Client Input (Streamlit UI or CLI)
         │
         ▼
 QuestionnaireAgent        ← generates discovery questions tailored to BU + client context
         │
         ▼
   DiscoveryAgent          ← extracts pain points, regulatory drivers, environment details
         │
         ▼
   ScopingAgent            ← estimates effort, defines in/out scope, flags risks
         │
         ▼
   PricingAgent            ← codebook-driven pricing with tier + discount logic
         │
         ▼
   CriticAgent             ← adversarial reviewer: challenges weak claims, vague scope, unsupported estimates
         │
         ▼
   ProposalAgent           ← renders full proposal from template, incorporating critic fixes
         │
         ▼
   Output: proposal.md     ← saved to outputs/{date}_{client}_{service}/
```

**Model strategy:** `llama-3.1-8b-instant` (MODEL_FAST) for agents 1–4 and Critic. `llama-3.3-70b-versatile` (MODEL_PRO) for ProposalAgent only. Keeps cost near zero on Groq free tier.

---

## Services covered — 6 BUs, 22 codes

| BU | Services |
|----|---------|
| **DFIR** | IR Retainer (ENT/STD), Compromise Assessment, Internal Forensic Investigation, Breach & Attack Simulation, Digital Forensics |
| **CTS** (Pen Test) | Network PT, Web App PT, Mobile PT, API PT, Cloud PT, Red Team, Phishing Sim |
| **GRC** | ISO 27001, PCI DSS v4.0, SOC 2, HIPAA, DPDP Readiness |
| **MXDR** | Managed XDR Essential, Managed XDR Advanced |
| **Institute** (Training) | Security Awareness, DFIR Practitioner |
| **DPG** (Data Privacy) | DPIA, Data Mapping |

---

## Adversarial CriticAgent

Most multi-agent pipelines just chain outputs forward. This one includes a critic that runs **against** its own output:

```python
# After exec summary is generated, critic challenges it before rendering
critique = critic.run(exec_summary, doc_type="executive summary")
# Returns: 3 weaknesses with exact quote + rewrite suggestion
exec_summary = critic.improve_exec_summary(exec_summary, critiques[:2])
```

Failure modes it catches: vague claims without evidence, unsupported timelines, missing risk acknowledgement, regulatory claims without citation.

---

## Streamlit UI

```
Sidebar: API key status · pipeline mode (full/discovery/scope)
Main:    client info form → BU selector → service dropdown
         [Generate Proposal] → live phase progress
         Results tabs: Discovery · Scope · Pricing · Proposal · Downloads
         Pipeline history: last 10 runs, expandable, downloadable
```

Dark theme, real-time progress, download buttons for every output file.

---

## Setup

### Streamlit Community Cloud (recommended — free)

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → your fork → `streamlit_app.py`
3. Add secrets in the dashboard:
   ```toml
   GROQ_API_KEY = "gsk_..."
   COMPANY_NAME = "Your Company Name"
   ```
4. Deploy — auto-redeploys on every push to main

### Local

```bash
git clone https://github.com/sanjayrkshetty/proposal-engine
cd proposal-engine
pip install -r requirements.txt

cp .env.example .env
# Edit .env: add GROQ_API_KEY=gsk_...

# Streamlit UI
streamlit run streamlit_app.py

# CLI
python main.py --service DFIR-R-ENT --client "Acme Bank" \
  --industry "Banking" --size "Mid-market" --region "India-South"
```

### Environment variables

| Variable | Required | Default |
|----------|----------|---------|
| `GROQ_API_KEY` | Yes | — |
| `COMPANY_NAME` | No | `Proposal Engine` |

---

## CLI flags

```
--service    Service code (e.g. DFIR-R-ENT, CTS-NPT, GRC-ISO27001)
--client     Client name
--industry   Industry vertical
--size       Organisation size
--region     Region (India-South, SEA, MEA, North America...)
--mode       full (default) | discovery | scope
--tier       Standard | Enterprise (auto-detected if omitted)
--discount   Discount % (0–40)
--gam        GAM ID from config/gam_list.yaml
```

---

## Tests

```bash
pytest tests/ -v
# 90/90 passing — zero LLM calls in CI (all mocked)
```

Tests cover: template rendering for all 22 service codes, placeholder completeness, proposal number format, billing contact propagation.

---

## Output structure

```
outputs/
└── 2026-05-11_Acme-Bank_DFIR-R-ENT/
    ├── questionnaire.json
    ├── discovery_brief.md
    ├── scope_estimate.md
    ├── pricing.md
    └── proposal.md          ← the deliverable
```

---

## Extending

**Add a new service:** edit `config/services.yaml` + add a template to `templates/{bu}/`.

**Add a new BU:** create `bu/{name}/config.py` and `bu/{name}/questionnaire.py`, register in `bu/__init__.py`.

**Swap the LLM:** change `MODEL_FAST` / `MODEL_PRO` in `agents/base_agent.py`. Any OpenAI-compatible API works (OpenRouter, Together, local Ollama).

---

## Built by

[Sanjay R K Shetty](https://github.com/sanjayrkshetty) — AI Security Researcher, MIT Bengaluru '26.

© 2026 Sanjay R K Shetty · All rights reserved
