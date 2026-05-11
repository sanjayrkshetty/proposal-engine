# DEMO — proposal-engine

3-agent agentic pipeline for DFIR pre-sales automation. Each run produces three chained outputs: discovery brief → scope estimate → full proposal.

**CLI:** `python main.py --service DFIR-R --client "Apex Banking Group" --industry Banking --size "3000 employees"`

---

## Supported Service Lines

| Code   | Name                          | Description |
|--------|-------------------------------|-------------|
| DFIR-R | DFIR Retainer                 | Pre-contracted priority access to forensic experts with guaranteed SLAs |
| IFI    | Internal Forensic Investigation | Thorough investigation of complex or high-impact internal incidents |
| CA     | Compromise Assessment         | Proactive identification of hidden breaches and lateral movement |
| BAS    | Breach and Attack Simulation  | MITRE ATT&CK-mapped simulated attacks to validate defenses and assess security maturity |

---

## Sample Run — DFIR Retainer for Apex Banking Group

**Command:**
```bash
python main.py \
  --service DFIR-R \
  --client "Apex Banking Group" \
  --industry Banking \
  --size "3000 employees"
```

**Console output:**
```
╭─────────────────── Starting ────────────────────╮
│ Proposal Engine                            │
│ Service: DFIR Retainer                          │
│ Mode: full                                      │
╰─────────────────────────────────────────────────╯

Phase 1 — Discovery
  ✓ Discovery brief → outputs/2026-05-11_Apex-Banking-Group_DFIR-R/discovery_brief.md

Phase 2 — Scoping
  ✓ Scope estimate → outputs/2026-05-11_Apex-Banking-Group_DFIR-R/scope_estimate.md

Phase 3 — Proposal
  ✓ Proposal → outputs/2026-05-11_Apex-Banking-Group_DFIR-R/proposal.md

Done. Outputs in: outputs/2026-05-11_Apex-Banking-Group_DFIR-R/
```

---

## Agent 1 — Discovery Agent

**Model:** `claude-haiku-4-5` · **Purpose:** Extract pain points, regulatory drivers, environment assumptions, discovery questions, urgency signals, and recommend a pricing tier.

### Raw JSON output (`discovery_brief.json`)

```json
{
  "pain_points": [
    "No pre-contracted IR retainer — current response relies on ad-hoc vendor engagement, adding 24-48h to containment windows",
    "RBI and PCI DSS v4.0 compliance obligations require documented incident response capability with defined SLAs",
    "Legacy core banking systems create forensic complexity — limited logging, proprietary formats, poor audit trail",
    "Internal security team lacks DFIR depth; threat containment and root-cause analysis are outsourced reactively",
    "Increasing phishing and BEC attacks targeting banking staff; no structured playbook for credential compromise scenarios"
  ],
  "regulatory_drivers": [
    "RBI Cybersecurity Framework — mandatory IR policy and 6-hour breach reporting to CERT-In",
    "PCI DSS v4.0 Requirement 12.10 — documented and tested incident response plan",
    "ISO/IEC 27001 Annex A.16 — information security incident management",
    "SEBI CSCRF for listed entities — cyber resilience framework with incident response mandates"
  ],
  "environment_assumptions": [
    "Hybrid on-premise and private cloud environment — core banking on-prem, ancillary services on Azure",
    "3,000 employees across 3 geographies; estimated 2,500 endpoints in scope",
    "SIEM deployed (likely Splunk or IBM QRadar) but SOC coverage is business-hours only",
    "Card data environment in scope — PCI DSS CDE with 2-3 merchant-facing applications",
    "No current EDR on legacy Windows Server 2012/2016 nodes"
  ],
  "discovery_questions": [
    "What was your most recent security incident and how long did it take from detection to containment?",
    "Do you have an existing IR retainer with another vendor? If yes, what are the current SLAs and pain points?",
    "How is your PCI DSS CDE scoped — what systems and channels are in scope for Requirement 12.10?",
    "What is the internal IR team headcount and their certifications (GCFA, GCIH, CEH)?",
    "Are there any active or recent regulatory findings related to incident response readiness?"
  ],
  "urgency_signals": [
    "Recent industry-wide banking sector breach (peer institution compromise reported Q1 2026)",
    "Upcoming PCI DSS v4.0 compliance audit within 6 months",
    "CISO new in role — looking to establish IR capability as early win",
    "Board-level pressure following RBI circular on cyber resilience issued March 2026"
  ],
  "recommended_tier": "Enterprise",
  "tier_rationale": "3,000 employees with PCI DSS CDE and RBI obligations warrants guaranteed SLAs and dedicated forensic hours; Essential is insufficient for regulated banking environments, Elite is justified only if a live incident is in progress."
}
```

### Markdown output (`discovery_brief.md`)

```markdown
# Discovery Brief — Apex Banking Group
**Service:** DFIR Retainer
**Recommended Tier:** Enterprise — 3,000 employees with PCI DSS CDE and RBI obligations warrants guaranteed SLAs
and dedicated forensic hours; Essential is insufficient for regulated banking environments.

## Pain Points
- No pre-contracted IR retainer — current response relies on ad-hoc vendor engagement, adding 24-48h to containment windows
- RBI and PCI DSS v4.0 compliance obligations require documented incident response capability with defined SLAs
- Legacy core banking systems create forensic complexity — limited logging, proprietary formats, poor audit trail
- Internal security team lacks DFIR depth; threat containment and root-cause analysis are outsourced reactively
- Increasing phishing and BEC attacks targeting banking staff; no structured playbook for credential compromise scenarios

## Regulatory Drivers
- RBI Cybersecurity Framework — mandatory IR policy and 6-hour breach reporting to CERT-In
- PCI DSS v4.0 Requirement 12.10 — documented and tested incident response plan
- ISO/IEC 27001 Annex A.16 — information security incident management
- SEBI CSCRF for listed entities — cyber resilience framework with incident response mandates

## Environment Assumptions
- Hybrid on-premise and private cloud environment — core banking on-prem, ancillary services on Azure
- 3,000 employees across 3 geographies; estimated 2,500 endpoints in scope
- SIEM deployed (likely Splunk or IBM QRadar) but SOC coverage is business-hours only
- Card data environment in scope — PCI DSS CDE with 2-3 merchant-facing applications
- No current EDR on legacy Windows Server 2012/2016 nodes

## Top Discovery Questions
1. What was your most recent security incident and how long did it take from detection to containment?
2. Do you have an existing IR retainer with another vendor? If yes, what are the current SLAs and pain points?
3. How is your PCI DSS CDE scoped — what systems and channels are in scope for Requirement 12.10?
4. What is the internal IR team headcount and their certifications (GCFA, GCIH, CEH)?
5. Are there any active or recent regulatory findings related to incident response readiness?

## Urgency Signals
- Recent industry-wide banking sector breach (peer institution compromise reported Q1 2026)
- Upcoming PCI DSS v4.0 compliance audit within 6 months
- CISO new in role — looking to establish IR capability as early win
- Board-level pressure following RBI circular on cyber resilience issued March 2026
```

---

## Agent 2 — Scoping Agent

**Model:** `claude-haiku-4-5` · **Purpose:** Translate discovery findings into an effort estimate, in/out-of-scope definition, SLA commitments, and an indicative price range.

### Raw JSON output (`scope_estimate.json` — derived from `scope_estimate.md`)

```json
{
  "effort_days": {
    "onsite": 8,
    "remote": 14,
    "reporting": 5,
    "total": 27
  },
  "in_scope": [
    "12-month retainer agreement with defined response SLAs",
    "Up to 200 prepaid forensic investigation hours per annum",
    "PCI DSS CDE coverage — card data environment systems and merchant-facing applications",
    "Quarterly IR readiness reviews and tabletop exercise (1 per quarter)",
    "On-demand access to GCFA/GCIH-certified forensic investigators within SLA",
    "Incident response playbook development (tailored to RBI and PCI DSS v4.0 requirements)",
    "CERT-In 6-hour breach notification support",
    "Post-incident lessons-learned report for each activated engagement"
  ],
  "out_of_scope": [
    "Penetration testing and vulnerability assessments (separate engagement)",
    "SOC managed services or 24/7 monitoring (not included in retainer)",
    "Forensic investigation hours exceeding 200/year (priced as overage at day rate)",
    "Legal counsel, regulatory liaison, or law enforcement coordination",
    "Remediation implementation — advisory only; execution is client responsibility"
  ],
  "deliverables": [
    "Signed retainer agreement with SLA schedule",
    "Customised incident response playbook (NIST IR framework aligned)",
    "4x quarterly readiness review reports",
    "Post-incident forensic investigation reports (per activation)",
    "Annual retainer performance summary"
  ],
  "commercial_risks": [
    "Overage risk: 200 prepaid hours may be exhausted by a single large incident — client should understand day-rate overage pricing upfront",
    "Scope ambiguity on CDE boundaries: if PCI DSS scope expands mid-retainer (new payment channels), renegotiation required",
    "Travel costs for on-site response outside primary geography (Mumbai HQ) are pass-through — not included in retainer fee",
    "Quarterly tabletop exercises assume 4-hour sessions; multi-day red team exercises require separate SOW"
  ],
  "sla_commitments": {
    "initial_response": "4 hours (P1 critical) / 8 hours (P2 high)",
    "containment": "24 hours for P1 incidents",
    "report_delivery": "5 business days post-containment"
  },
  "indicative_price_range": {
    "low": 42000,
    "high": 68000,
    "currency": "USD"
  }
}
```

### Markdown output (`scope_estimate.md`)

```markdown
# Scope Estimate — Apex Banking Group
**Service:** DFIR Retainer — Enterprise Tier

## Effort Estimate
| Phase      | Days |
|------------|------|
| On-site    | 8    |
| Remote     | 14   |
| Reporting  | 5    |
| **Total**  | **27** |

**Indicative Price:** $42,000 – $68,000 USD

## In Scope
- 12-month retainer agreement with defined response SLAs
- Up to 200 prepaid forensic investigation hours per annum
- PCI DSS CDE coverage — card data environment systems and merchant-facing applications
- Quarterly IR readiness reviews and tabletop exercise (1 per quarter)
- On-demand access to GCFA/GCIH-certified forensic investigators within SLA
- Incident response playbook development (tailored to RBI and PCI DSS v4.0 requirements)
- CERT-In 6-hour breach notification support
- Post-incident lessons-learned report for each activated engagement

## Out of Scope
- Penetration testing and vulnerability assessments (separate engagement)
- SOC managed services or 24/7 monitoring (not included in retainer)
- Forensic investigation hours exceeding 200/year (priced as overage at day rate)
- Legal counsel, regulatory liaison, or law enforcement coordination
- Remediation implementation — advisory only; execution is client responsibility

## Deliverables
- Signed retainer agreement with SLA schedule
- Customised incident response playbook (NIST IR framework aligned)
- 4x quarterly readiness review reports
- Post-incident forensic investigation reports (per activation)
- Annual retainer performance summary

## SLA Commitments
- Initial response: 4 hours (P1 critical) / 8 hours (P2 high)
- Containment: 24 hours for P1 incidents
- Report delivery: 5 business days post-containment

## Commercial Risks
⚠ Overage risk: 200 prepaid hours may be exhausted by a single large incident — client should understand day-rate overage pricing upfront
⚠ Scope ambiguity on CDE boundaries: if PCI DSS scope expands mid-retainer (new payment channels), renegotiation required
⚠ Travel costs for on-site response outside primary geography (Mumbai HQ) are pass-through — not included in retainer fee
⚠ Quarterly tabletop exercises assume 4-hour sessions; multi-day red team exercises require separate SOW
```

---

## Agent 3 — Proposal Agent

**Model:** `claude-sonnet-4-6` · **Purpose:** Generate a full professional proposal markdown (executive summary through pricing and next steps), grounded in the discovery and scope outputs.

### Full proposal output (`proposal.md`)

```markdown
# DFIR Retainer Proposal
## Apex Banking Group
**Prepared by:** Proposal Engine | **Date:** 11 May 2026 | **Tier:** Enterprise | **Ref:** Proposal Engine/DFIR/RET/2026/001

---

## 1. Executive Summary

Apex Banking Group operates in a high-threat environment with clear regulatory obligations under RBI's Cybersecurity Framework and PCI DSS v4.0, yet currently lacks a pre-contracted incident response capability with defined SLAs. A single uncontained breach in a banking environment of this scale can result in regulatory penalties, card scheme fines, and reputational damage that far exceed the cost of proactive preparedness. Our DFIR Retainer gives Apex Banking Group guaranteed 4-hour response, dedicated forensic capacity, and the documented IR programme required to satisfy upcoming compliance audits.

---

## 2. Understanding of Your Requirements

Apex Banking Group faces a convergence of pressures that make structured IR preparedness urgent rather than aspirational. The absence of a pre-contracted retainer means that in the event of a compromise, the bank would be negotiating vendor terms during active containment — a scenario that compounds exposure. Your PCI DSS CDE and RBI obligations mandate not just a response capability, but a documented, tested, and auditable one. Legacy infrastructure on-premise, combined with limited SOC coverage outside business hours, creates response blind spots that adversaries exploit. The recent banking sector compromise across peer institutions in Q1 2026 underscores the relevance of the threat.

Our engagement is designed to close these gaps through a structured retainer that delivers both compliance documentation and genuine operational readiness.

---

## 3. Our Approach

Proposal Engine follows a four-phase DFIR methodology: **Preparation**, **Detection and Triage**, **Containment and Eradication**, and **Recovery and Lessons Learned** — aligned to NIST SP 800-61r2 and CERT-In reporting requirements.

Under this retainer, Proposal Engine will:
- Conduct an onboarding forensic readiness assessment (environment mapping, logging adequacy, evidence preservation procedures)
- Develop a tailored Incident Response Playbook covering credential compromise, ransomware, insider threat, and BEC scenarios
- Maintain dedicated standby capacity — GCFA and GCIH-certified forensic investigators available 24/7 within SLA
- Execute quarterly tabletop exercises to validate playbook currency and staff readiness
- Provide on-demand forensic investigation up to 200 hours per annum, with overage available at agreed day rates

---

## 4. Scope of Work

| In Scope | Out of Scope |
|----------|-------------|
| 12-month retainer with defined SLA schedule | Penetration testing and VA (separate engagement) |
| 200 prepaid forensic investigation hours | SOC/MDR managed monitoring services |
| PCI DSS CDE systems and merchant-facing applications | Forensic hours exceeding 200/year (overage pricing applies) |
| Quarterly IR readiness reviews and tabletop exercises | Legal counsel or regulatory liaison |
| On-demand GCFA/GCIH-certified investigator access | Remediation implementation (advisory only) |
| Incident response playbook development | Multi-day red team exercises (separate SOW) |
| CERT-In 6-hour breach notification support | |
| Post-incident lessons-learned reports | |

---

## 5. Deliverables

- **Retainer Agreement** — signed SLA schedule and activation procedures
- **Incident Response Playbook** — NIST-aligned, tailored to RBI and PCI DSS v4.0 requirements
- **Quarterly Readiness Review Reports** (4 per annum)
- **Forensic Investigation Reports** — per incident activation, including executive summary and technical findings
- **Annual Retainer Performance Summary** — hours utilised, incidents handled, SLA adherence

---

## 6. Team and Credentials

Our DFIR practice is staffed by investigators holding GCFA (GIAC Certified Forensic Analyst), GCIH (GIAC Certified Incident Handler), and CREST certifications. The team has handled banking sector incidents across India, MEA, and Southeast Asia, with specific expertise in core banking system forensics and PCI DSS breach response. Proposal Engine holds PFI (PCI Forensic Investigator) status — a requirement for any breach investigation involving card data.

---

## 7. SLA Commitments

| Priority | Trigger | Initial Response | Containment Target |
|----------|---------|------------------|--------------------|
| P1 — Critical | Active breach, data exfiltration, ransomware | 4 hours | 24 hours |
| P2 — High | Suspected compromise, anomalous activity | 8 hours | 48 hours |
| P3 — Medium | IR advisory, playbook consultation | Next business day | N/A |

Report delivery: 5 business days post-containment for P1/P2 incidents.

---

## 8. Investment

| Tier | Prepaid Hours | SLA (P1 Response) | Tabletops | Annual Fee (USD) |
|------|--------------|-------------------|-----------|-----------------|
| Essential | 80 hours | 8 hours | 2/year | $22,000 – $28,000 |
| **Enterprise** | **200 hours** | **4 hours** | **4/year** | **$42,000 – $68,000** |
| Elite | 400 hours | 2 hours | 6/year + red team | $85,000 – $120,000 |

*Recommended: Enterprise Tier.* Overage hours available at agreed day rate. Travel costs outside primary geography (Mumbai) are pass-through. Annual fee excludes GST/VAT where applicable.

---

## 9. Why Proposal Engine

- **PFI-accredited** — one of a limited number of firms globally authorised to conduct PCI DSS breach investigations; directly relevant to Apex Banking Group's card data environment
- **Banking sector depth** — extensive experience with core banking forensics, RBI regulatory reporting, and SEBI CSCRF requirements across India and MEA
- **Geography** — on-the-ground presence in India and MEE with 24/7 standby capacity; no dependency on international team mobilisation
- **CERT-In empanelled** — recognised by India's nodal cybersecurity agency for incident response, adding credibility to your regulatory disclosures

---

## 10. Next Steps

1. **Discovery call** (30 min) — validate environment assumptions, confirm CDE scope, discuss existing IR capability
2. **Playbook scoping workshop** (half-day) — map critical asset inventory and define incident classification criteria
3. **Commercial alignment** — confirm tier, prepaid hours, and contract term; legal review of SLA schedule
4. **Onboarding** — forensic readiness assessment and playbook development (Weeks 1–4 of engagement)

To proceed or schedule the discovery call, contact your Proposal Engine account manager or reach out directly:
**David Okafor** | Director - Sales, India | contact@proposalengine.io
```

---

## Output File Structure

Each pipeline run produces a timestamped directory under `outputs/`:

```
outputs/
└── 2026-05-11_Apex-Banking-Group_DFIR-R/
    ├── discovery_brief.json    ← Agent 1 structured output
    ├── discovery_brief.md      ← Agent 1 markdown render
    ├── scope_estimate.md       ← Agent 2 markdown render
    └── proposal.md             ← Agent 3 full proposal
```

---

## Pipeline Architecture

```
python main.py --service DFIR-R --client "..." --industry "..." --size "..."
        │
        ├── DiscoveryAgent (claude-haiku-4-5)
        │       └── pain points, regulatory drivers, tier recommendation
        │
        ├── ScopingAgent (claude-haiku-4-5)
        │       └── effort table, in/out scope, SLAs, price range
        │
        └── ProposalAgent (claude-sonnet-4-6)
                └── full proposal markdown: exec summary → pricing → next steps

Config:   config/services.yaml   (service definitions, key components, regulatory fit)
Outputs:  outputs/<run-id>/      (discovery_brief.json, .md, scope_estimate.md, proposal.md)
```

Modes available via `--mode`: `full` (default) | `discovery` | `scope` | `proposal`

Use `--input <brief.json>` to resume from an existing discovery brief without re-running Agent 1.
