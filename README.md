Proposal Engine

Agentic pre-sales automation for DFIR service line.

Automates the full pre-sales workflow — discovery → scoping → proposal generation — for:
- **DFIR Retainer** — pre-contracted priority access to forensic experts
- **IFI** — Internal Forensic Investigation for complex/high-impact incidents  
- **CA** — Compromise Assessment for hidden breach detection
- **BAS** — Breach and Attack Simulation mapped to MITRE ATT&CK

Built with Claude API multi-agent orchestration. Runs on GitHub Actions with daily workflow execution.

---

## Architecture

```
Client Input (CLI or JSON)
        ↓
  Discovery Agent          ← extracts pain points, regulatory drivers, environment
        ↓
  Scoping Agent            ← estimates effort, defines in/out scope, flags risks
        ↓
  Proposal Agent           ← generates full proposal: exec summary → pricing
        ↓
  Output (Markdown/PDF)    ← saved to outputs/ with timestamp
```

## Services covered

| Service | Code | Description |
|---------|------|-------------|
| DFIR Retainer | `DFIR-R` | Pre-contracted IR access, 24/7 priority SLAs |
| Internal Forensic Investigation | `IFI` | Deep system/log forensics, attack chain reconstruction |
| Compromise Assessment | `CA` | Proactive hidden breach & lateral movement detection |
| Breach & Attack Simulation | `BAS` | MITRE ATT&CK simulated attacks, maturity assessment |

## Usage

```bash
# Install
pip install -r requirements.txt

# Run full pipeline for a service
python main.py --service DFIR-R --client "Acme Bank" --industry "Banking" --size "5000 employees"

# Run discovery only
python main.py --service CA --mode discovery

# Run scoping from existing discovery brief
python main.py --service IFI --mode scope --input outputs/discovery_brief.json
```

## Setup

```bash
export ANTHROPIC_API_KEY=your_key
```

## Output structure

```
outputs/
└── YYYY-MM-DD_ClientName_ServiceCode/
    ├── discovery_brief.md
    ├── scope_estimate.md
    └── proposal.md
```

## Workflow updates

Add new service flows by editing `config/services.yaml` and the relevant template in `templates/`.
The GitHub Action runs daily, validates all templates, and commits any regenerated samples.
