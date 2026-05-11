"""Proposal Engine — Web UI (Streamlit)."""
import os
import re
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Load Streamlit secrets → env vars before any agent imports
import streamlit as st

def _load_secrets():
    for key in ("GROQ_API_KEY", "COMPANY_NAME"):
        if key in st.secrets:
            os.environ.setdefault(key, st.secrets[key])
    # Also honour .env for local dev
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

_load_secrets()

# Now safe to import agents
sys.path.insert(0, str(Path(__file__).parent))
import yaml
from agents.questionnaire_agent import QuestionnaireAgent
from agents.discovery_agent import DiscoveryAgent
from agents.scoping_agent import ScopingAgent
from agents.pricing_agent import PricingAgent
from agents.proposal_agent import ProposalAgent
from agents.gam_agent import GAMAgent

COMPANY_NAME = os.environ.get("COMPANY_NAME", "Proposal Engine")
REGIONS = ["India-South", "India-North", "MEE", "SEA", "NA"]

# ── CSS Injection — Dark Web3 / GenZ Aesthetic ─────────────────────────────
DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Background */
.stApp {
    background: #0D1117;
    background-image: radial-gradient(ellipse at 20% 50%, rgba(0,255,136,0.03) 0%, transparent 50%),
                      radial-gradient(ellipse at 80% 20%, rgba(88,166,255,0.03) 0%, transparent 50%);
}

/* Hide default header */
#MainMenu, footer, header { visibility: hidden; }

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #0D1117 0%, #161B22 50%, #0D1117 100%);
    border: 1px solid #21262D;
    border-radius: 16px;
    padding: 2.5rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00FF88, #58A6FF, transparent);
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00FF88 0%, #58A6FF 50%, #A78BFA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.2;
}
.hero-sub {
    color: #8B949E;
    font-size: 0.95rem;
    margin-top: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
}
.hero-badges {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
    flex-wrap: wrap;
}
.badge {
    background: rgba(0,255,136,0.08);
    border: 1px solid rgba(0,255,136,0.2);
    color: #00FF88;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
}
.badge.blue {
    background: rgba(88,166,255,0.08);
    border-color: rgba(88,166,255,0.2);
    color: #58A6FF;
}
.badge.purple {
    background: rgba(167,139,250,0.08);
    border-color: rgba(167,139,250,0.2);
    color: #A78BFA;
}

/* Cards */
.card {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.card:hover { border-color: #30363D; }
.card-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8B949E;
    margin-bottom: 0.4rem;
    font-family: 'JetBrains Mono', monospace;
}
.card-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #E6EDF3;
}
.card-value.green { color: #3FB950; }
.card-value.cyan { color: #00FF88; }
.card-value.blue { color: #58A6FF; }

/* Section headers */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 1.5rem 0 0.8rem;
}
.section-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #00FF88;
    box-shadow: 0 0 8px rgba(0,255,136,0.6);
}
.section-title {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #8B949E;
    font-family: 'JetBrains Mono', monospace;
}

/* Alert boxes */
.alert-warn {
    background: rgba(210,153,34,0.08);
    border: 1px solid rgba(210,153,34,0.3);
    border-left: 3px solid #D29922;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    color: #D29922;
    font-size: 0.88rem;
}
.alert-danger {
    background: rgba(248,81,73,0.08);
    border: 1px solid rgba(248,81,73,0.3);
    border-left: 3px solid #F85149;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    color: #F85149;
    font-size: 0.88rem;
}
.alert-success {
    background: rgba(63,185,80,0.08);
    border: 1px solid rgba(63,185,80,0.3);
    border-left: 3px solid #3FB950;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    color: #3FB950;
    font-size: 0.88rem;
}

/* Progress steps */
.step-bar {
    display: flex;
    gap: 0.4rem;
    margin: 1rem 0;
}
.step {
    flex: 1;
    height: 4px;
    border-radius: 2px;
    background: #21262D;
}
.step.done { background: #00FF88; }
.step.active {
    background: linear-gradient(90deg, #00FF88, #58A6FF);
    animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* Proposal output */
.proposal-container {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 12px;
    padding: 1.5rem;
    font-family: 'Space Grotesk', sans-serif;
    line-height: 1.7;
    max-height: 600px;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: #30363D #161B22;
}
.proposal-container::-webkit-scrollbar { width: 6px; }
.proposal-container::-webkit-scrollbar-track { background: #161B22; }
.proposal-container::-webkit-scrollbar-thumb { background: #30363D; border-radius: 3px; }

/* Sidebar tweaks */
[data-testid="stSidebar"] {
    background: #0D1117 !important;
    border-right: 1px solid #21262D !important;
}

/* Input styling */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: #161B22 !important;
    border: 1px solid #30363D !important;
    color: #E6EDF3 !important;
    border-radius: 8px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #00FF88 !important;
    box-shadow: 0 0 0 2px rgba(0,255,136,0.1) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00FF88, #00CC6A) !important;
    color: #0D1117 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.5rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0,255,136,0.3) !important;
}

/* Download button */
.stDownloadButton > button {
    background: #161B22 !important;
    color: #00FF88 !important;
    border: 1px solid #00FF88 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover {
    background: rgba(0,255,136,0.1) !important;
}

/* Tabs */
[data-baseweb="tab-list"] {
    background: #161B22 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid #21262D !important;
}
[data-baseweb="tab"] {
    color: #8B949E !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}
[aria-selected="true"] {
    background: #21262D !important;
    color: #00FF88 !important;
    border-radius: 8px !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 10px;
    padding: 0.75rem 1rem;
}
[data-testid="stMetricValue"] {
    color: #00FF88 !important;
    font-weight: 700 !important;
}
</style>
"""


# ── Helpers ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_services():
    with open("config/services.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg["services"]


def get_proposal_number(service_config: dict, region: str) -> str:
    seq_path = Path("config/proposal_sequences.json")
    sequences = json.loads(seq_path.read_text(encoding="utf-8")) if seq_path.exists() else {}
    fmt = service_config.get("proposal_number_format", "PROP-{BU}-{YEAR}-{SEQ:04d}")
    bu = service_config.get("bu", "PE").upper()
    year = datetime.now().strftime("%Y")
    region_code = region.replace("-", "").upper()[:6]
    seq_key = f"{bu}_{year}_{region_code}"
    current_seq = sequences.get(seq_key, 0) + 1
    sequences[seq_key] = current_seq
    seq_path.write_text(json.dumps(sequences, indent=2), encoding="utf-8")
    return fmt.format(YEAR=year, REGION=region_code, BU=bu, SEQ=current_seq)


def sanitize_for_path(s: str) -> str:
    return re.sub(r"[^\w\s-]", "", s).replace(" ", "-")[:40]


def check_api_key() -> bool:
    key = os.environ.get("GROQ_API_KEY", "")
    return bool(key and key != "your_groq_api_key_here" and len(key) > 20)


def progress_bar_html(current: int, total: int = 5) -> str:
    steps = []
    for i in range(total):
        if i < current:
            steps.append('<div class="step done"></div>')
        elif i == current:
            steps.append('<div class="step active"></div>')
        else:
            steps.append('<div class="step"></div>')
    return f'<div class="step-bar">{"".join(steps)}</div>'


# ── Page Config ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title=f"{COMPANY_NAME}",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(DARK_CSS, unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div style="padding:1rem 0.5rem">
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#8B949E;text-transform:uppercase;letter-spacing:0.1em">System</div>
        <div style="font-size:1.1rem;font-weight:700;color:#E6EDF3;margin-top:0.3rem">{COMPANY_NAME}</div>
        <div style="font-size:0.75rem;color:#8B949E;font-family:'JetBrains Mono',monospace">Agentic Proposal Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    api_ok = check_api_key()
    if api_ok:
        st.markdown('<div class="alert-success">⚡ LLM Connected — Groq API active</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-danger">⚠ GROQ_API_KEY not set</div>', unsafe_allow_html=True)
        with st.expander("How to set up"):
            st.markdown("""
            **Local:** Create `.env` file:
            ```
            GROQ_API_KEY=your_key_here
            ```
            **Streamlit Cloud:** App Settings → Secrets
            ```toml
            GROQ_API_KEY = "your_key"
            ```
            Get a free key at [console.groq.com](https://console.groq.com/keys)
            """)

    st.divider()

    st.markdown('<div class="section-title">Pipeline Mode</div>', unsafe_allow_html=True)
    mode = st.selectbox(
        "mode",
        options=["full", "discovery", "scope"],
        format_func=lambda x: {"full": "⚡ Full Pipeline", "discovery": "🔍 Discovery Only", "scope": "📐 Scope Only"}[x],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown('<div class="section-title">About</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.78rem;color:#8B949E;line-height:1.6">
    5-agent pipeline:<br>
    <span style="color:#00FF88;font-family:monospace">Questionnaire</span> →
    <span style="color:#58A6FF;font-family:monospace">Discovery</span> →
    <span style="color:#A78BFA;font-family:monospace">Scoping</span> →
    <span style="color:#D29922;font-family:monospace">Pricing</span> →
    <span style="color:#3FB950;font-family:monospace">Proposal</span><br><br>
    Powered by <span style="color:#E6EDF3">Groq</span> — zero token waste.
    </div>
    """, unsafe_allow_html=True)


# ── Hero ───────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">Proposal Engine</div>
    <div class="hero-sub">// agentic pre-sales automation · 6 BUs · 22 services · zero manual effort</div>
    <div class="hero-badges">
        <span class="badge">⚡ Groq-Powered</span>
        <span class="badge blue">6 Business Units</span>
        <span class="badge blue">22 Services</span>
        <span class="badge purple">AI-Native Pipeline</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Service Selection ──────────────────────────────────────────────────────

services = load_services()
bu_map = {}
for code, cfg in services.items():
    bu = cfg.get("bu", "other").upper()
    if bu not in bu_map:
        bu_map[bu] = []
    bu_map[bu].append((code, cfg.get("name", code)))

col_bu, col_svc = st.columns([1, 2])

with col_bu:
    st.markdown('<div class="section-header"><div class="section-dot"></div><div class="section-title">Business Unit</div></div>', unsafe_allow_html=True)
    selected_bu = st.selectbox("bu", options=list(bu_map.keys()), label_visibility="collapsed")

with col_svc:
    st.markdown('<div class="section-header"><div class="section-dot" style="background:#58A6FF;box-shadow:0 0 8px rgba(88,166,255,0.6)"></div><div class="section-title">Service</div></div>', unsafe_allow_html=True)
    svc_options = bu_map.get(selected_bu, [])
    selected_svc = st.selectbox(
        "service",
        options=[code for code, _ in svc_options],
        format_func=lambda x: next((n for c, n in svc_options if c == x), x),
        label_visibility="collapsed",
    )

service_config = services[selected_svc]

# Show service description
if service_config.get("description"):
    st.markdown(f"""
    <div class="card" style="margin-top:0.5rem">
        <div class="card-title">Service Description</div>
        <div style="color:#C9D1D9;font-size:0.88rem">{service_config['description']}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Client Information ─────────────────────────────────────────────────────

st.markdown('<div class="section-header"><div class="section-dot" style="background:#A78BFA;box-shadow:0 0 8px rgba(167,139,250,0.6)"></div><div class="section-title">Client Information</div></div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    client_name = st.text_input("Client Name *", placeholder="e.g. Acme Bank Ltd", key="client_name")
with c2:
    industry = st.text_input("Industry", value="Financial Services", key="industry")
with c3:
    region = st.selectbox("Region", options=REGIONS, key="region")

c4, c5 = st.columns(2)
with c4:
    size = st.text_input("Organisation Size", value="Mid-market (500-5000 employees)", key="size")
with c5:
    gam_name = st.text_input("GAM / Account Manager (optional)", placeholder="Leave blank to auto-resolve", key="gam")

exec_summary = st.text_area(
    "Executive Context (optional)",
    placeholder="1-2 sentences about the client's situation, incident, or compliance driver...",
    height=80,
    key="exec_summary",
)

with st.expander("Advanced Options"):
    adv1, adv2 = st.columns(2)
    with adv1:
        tier_override = st.selectbox("Tier Override", options=["Auto (AI-recommended)", "Essential", "Enterprise", "Elite"], key="tier")
    with adv2:
        discount_pct = st.number_input("Discount %", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="discount")

st.divider()

# ── Generate Button ────────────────────────────────────────────────────────

generate = st.button("⚡  Generate Proposal", use_container_width=True, disabled=not (client_name and api_ok))

if not client_name:
    st.markdown('<div class="alert-warn">Enter a client name to generate a proposal.</div>', unsafe_allow_html=True)

if generate and client_name and api_ok:
    # Session state for results
    results = {}
    errors = []
    phase = 0

    progress_ph = st.empty()
    status_ph = st.empty()

    client_info = {
        "name": client_name,
        "industry": industry or "Financial Services",
        "size": size or "Mid-market",
        "region": region,
        "exec_summary": exec_summary or "",
        "scope_context": "",
    }

    tier_val = None if tier_override == "Auto (AI-recommended)" else tier_override

    # Proposal number
    proposal_number = get_proposal_number(service_config, region)

    # Output dir
    ts = datetime.now().strftime("%Y-%m-%d")
    slug = sanitize_for_path(client_name)
    run_id = f"{ts}_{slug}_{service_config['bu'].upper()}_{selected_svc}"
    out_path = Path("outputs") / run_id
    out_path.mkdir(parents=True, exist_ok=True)

    # ── Phase 0: Questionnaire
    progress_ph.markdown(progress_bar_html(0), unsafe_allow_html=True)
    status_ph.markdown('<div class="alert-success">⚡ Phase 0 — Running questionnaire...</div>', unsafe_allow_html=True)

    try:
        q_agent = QuestionnaireAgent(service_config)
        q_result = q_agent.run(
            bu=service_config["bu"],
            sub_bu=service_config.get("sub_bu", ""),
            client_info=client_info,
        )
        if q_result.get("scope_context"):
            client_info["scope_context"] = q_result["scope_context"]
        (out_path / "questionnaire.json").write_text(json.dumps(q_result, indent=2), encoding="utf-8")
        results["questionnaire"] = q_result
    except Exception as e:
        errors.append(f"Questionnaire: {e}")
        results["questionnaire"] = {"answers": {}, "scope_context": ""}

    # ── Phase 1: Discovery
    progress_ph.markdown(progress_bar_html(1), unsafe_allow_html=True)
    status_ph.markdown('<div class="alert-success">🔍 Phase 1 — Running discovery...</div>', unsafe_allow_html=True)

    brief = None
    try:
        d_agent = DiscoveryAgent(service_config)
        brief = d_agent.run(client_info)
        if tier_val:
            brief["data"]["recommended_tier"] = tier_val
        (out_path / "discovery_brief.json").write_text(json.dumps(brief["data"], indent=2), encoding="utf-8")
        (out_path / "discovery_brief.md").write_text(brief["markdown"], encoding="utf-8")
        results["discovery"] = brief
    except Exception as e:
        errors.append(f"Discovery: {e}")
        brief = {"data": {"recommended_tier": tier_val or "Enterprise", "pain_points": [], "regulatory_drivers": [], "urgency_signals": []}, "markdown": ""}

    if mode == "discovery":
        progress_ph.markdown(progress_bar_html(5), unsafe_allow_html=True)
        status_ph.markdown('<div class="alert-success">✓ Discovery complete.</div>', unsafe_allow_html=True)

    # ── Phase 2: Scoping
    scope = None
    if mode in ("full", "scope") and brief:
        progress_ph.markdown(progress_bar_html(2), unsafe_allow_html=True)
        status_ph.markdown('<div class="alert-success">📐 Phase 2 — Scoping...</div>', unsafe_allow_html=True)
        try:
            s_agent = ScopingAgent(service_config)
            scope = s_agent.run(brief["data"], client_info)
            (out_path / "scope_estimate.json").write_text(json.dumps(scope["data"], indent=2), encoding="utf-8")
            (out_path / "scope_estimate.md").write_text(scope["markdown"], encoding="utf-8")
            results["scope"] = scope
        except Exception as e:
            errors.append(f"Scoping: {e}")
            scope = {"data": {"effort_days": {"total": 5}, "in_scope": [], "out_of_scope": [], "assumptions": [], "commercial_risks": [], "deliverables": [], "indicative_price_range": {}}, "markdown": ""}

    if mode == "scope":
        progress_ph.markdown(progress_bar_html(5), unsafe_allow_html=True)
        status_ph.markdown('<div class="alert-success">✓ Scoping complete.</div>', unsafe_allow_html=True)

    # ── Phase 3: Pricing
    pricing_result = None
    if mode == "full" and scope:
        progress_ph.markdown(progress_bar_html(3), unsafe_allow_html=True)
        status_ph.markdown('<div class="alert-success">💰 Phase 3 — Pricing...</div>', unsafe_allow_html=True)
        try:
            p_agent = PricingAgent(service_config)
            qty = scope["data"].get("effort_days", {}).get("total", 1) or 1
            pricing_result = p_agent.build_pricing_table(
                service_code=selected_svc,
                qty=qty,
                region=region,
                discount_pct=discount_pct,
            )
            inflation = p_agent.check_inflation(pricing_result.get("total_inr", 0), region, service_config["bu"])
            pricing_result["inflation"] = inflation
            (out_path / "pricing_table.json").write_text(json.dumps(pricing_result, indent=2), encoding="utf-8")
            results["pricing"] = pricing_result
        except Exception as e:
            errors.append(f"Pricing: {e}")

    # ── Phase 4: Proposal
    if mode == "full" and brief and scope:
        progress_ph.markdown(progress_bar_html(4), unsafe_allow_html=True)
        status_ph.markdown('<div class="alert-success">📄 Phase 4 — Generating proposal...</div>', unsafe_allow_html=True)
        try:
            gam_agent = GAMAgent({})
            gam_data_raw = gam_agent.resolve_by_name(gam_name) if gam_name else gam_agent.resolve(region)
            billing_block = gam_agent.format_billing_block(gam_data_raw)
            gam_result = {"billing_block": billing_block, "gam": gam_data_raw}

            prop_agent = ProposalAgent(service_config)
            proposal = prop_agent.run(
                brief_data=brief["data"],
                scope_data=scope["data"],
                client_info=client_info,
                pricing_data=pricing_result,
                gam_data=gam_result,
                proposal_number=proposal_number,
            )
            (out_path / "proposal.md").write_text(proposal["markdown"], encoding="utf-8")
            (out_path / "proposal_meta.json").write_text(
                json.dumps({k: v for k, v in proposal["data"].items() if k != "proposal_text"}, indent=2),
                encoding="utf-8"
            )
            results["proposal"] = proposal
        except Exception as e:
            errors.append(f"Proposal: {e}")

    progress_ph.markdown(progress_bar_html(5), unsafe_allow_html=True)
    status_ph.markdown(f'<div class="alert-success">✓ Pipeline complete — Proposal <strong>{proposal_number}</strong></div>', unsafe_allow_html=True)

    st.session_state["results"] = results
    st.session_state["proposal_number"] = proposal_number
    st.session_state["out_path"] = str(out_path)
    st.session_state["errors"] = errors
    st.session_state["_pipeline_mode"] = mode
    # NOTE: do NOT write st.session_state["client_name"] or any other widget key —
    # Streamlit 1.57+ raises StreamlitAPIException if a widget-bound key is set manually.

# ── Results Display ────────────────────────────────────────────────────────

if "results" in st.session_state and st.session_state["results"]:
    results = st.session_state["results"]
    proposal_number = st.session_state.get("proposal_number", "")
    errors = st.session_state.get("errors", [])
    mode_used = st.session_state.get("_pipeline_mode", "full")

    st.divider()

    # Summary metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Proposal No.", proposal_number)
    with m2:
        tier_display = results.get("discovery", {}).get("data", {}).get("recommended_tier", "—")
        st.metric("Recommended Tier", tier_display)
    with m3:
        effort = results.get("scope", {}).get("data", {}).get("effort_days", {}).get("total", "—")
        st.metric("Effort (days)", effort)
    with m4:
        pricing = results.get("pricing", {})
        total = pricing.get("total_inr", 0)
        currency = pricing.get("currency", "INR")
        st.metric("Total Value", f"{currency} {total:,.0f}" if total else "—")

    # Alerts
    if errors:
        for err in errors:
            st.markdown(f'<div class="alert-warn">⚠ {err}</div>', unsafe_allow_html=True)

    pricing = results.get("pricing", {})
    if pricing.get("discount_approval_required"):
        st.markdown(f'<div class="alert-danger">🔴 Discount approval required — {discount_pct}% exceeds the {pricing.get("discount_threshold", 10)}% threshold. Get Sales Director sign-off.</div>', unsafe_allow_html=True)
    if pricing.get("inflation", {}).get("alert"):
        dev = pricing["inflation"].get("deviation_pct", 0)
        st.markdown(f'<div class="alert-warn">⚠ Inflation alert — ACV is {dev:.1f}% above regional baseline. Review before sending.</div>', unsafe_allow_html=True)

    # Results tabs
    tab_labels = ["🔍 Discovery", "📐 Scope", "💰 Pricing", "📄 Proposal", "📥 Downloads"]
    t1, t2, t3, t4, t5 = st.tabs(tab_labels)

    with t1:
        disc = results.get("discovery", {}).get("data", {})
        if disc:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Pain Points**")
                for p in disc.get("pain_points", []):
                    st.markdown(f"- {p}")
                st.markdown("**Regulatory Drivers**")
                for r in disc.get("regulatory_drivers", []):
                    st.markdown(f"- {r}")
            with c2:
                st.markdown("**Discovery Questions**")
                for i, q in enumerate(disc.get("discovery_questions", []), 1):
                    st.markdown(f"{i}. {q}")
                st.markdown("**Urgency Signals**")
                for u in disc.get("urgency_signals", []):
                    st.markdown(f"- {u}")
            if disc.get("tier_rationale"):
                st.markdown(f'<div class="alert-success">🎯 Tier Recommendation: <strong>{disc.get("recommended_tier")}</strong> — {disc.get("tier_rationale")}</div>', unsafe_allow_html=True)
        else:
            st.info("Run in full or discovery mode to see results.")

    with t2:
        scope_data = results.get("scope", {}).get("data", {})
        if scope_data:
            effort = scope_data.get("effort_days", {})
            price = scope_data.get("indicative_price_range", {})
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.metric("On-site Days", effort.get("onsite", 0))
            with sc2:
                st.metric("Remote Days", effort.get("remote", 0))
            with sc3:
                st.metric("Total Days", effort.get("total", 0))

            if price.get("low"):
                st.markdown(f"**Indicative Range:** {price.get('currency', 'INR')} {price.get('low', 0):,} – {price.get('high', 0):,}")

            s1, s2 = st.columns(2)
            with s1:
                st.markdown("**In Scope**")
                for i in scope_data.get("in_scope", []):
                    st.markdown(f"- {i}")
                st.markdown("**Deliverables**")
                for d in scope_data.get("deliverables", []):
                    st.markdown(f"- {d}")
            with s2:
                st.markdown("**Out of Scope**")
                for o in scope_data.get("out_of_scope", []):
                    st.markdown(f"- {o}")
                st.markdown("**Assumptions**")
                for a in scope_data.get("assumptions", []):
                    st.markdown(f"- {a}")

            if scope_data.get("commercial_risks"):
                st.markdown("**Commercial Risks**")
                for r in scope_data["commercial_risks"]:
                    st.markdown(f'<div class="alert-warn">⚠ {r}</div>', unsafe_allow_html=True)
        else:
            st.info("Run in full or scope mode to see results.")

    with t3:
        p = results.get("pricing", {})
        if p:
            st.markdown(p.get("pricing_table_md", "*No pricing table generated.*"))
            pc1, pc2, pc3 = st.columns(3)
            with pc1:
                st.metric("Unit Price", f"{p.get('currency', 'INR')} {p.get('unit_price_inr', 0):,.0f}")
            with pc2:
                st.metric("Qty / Days", p.get("qty", 1))
            with pc3:
                st.metric("Total", f"{p.get('currency', 'INR')} {p.get('total_inr', 0):,.0f}")
        else:
            st.info("Run in full pipeline mode to see pricing.")

    with t4:
        proposal = results.get("proposal", {})
        if proposal and proposal.get("markdown"):
            md = proposal["markdown"]
            # Render in scrollable container
            st.markdown(f'<div class="proposal-container">', unsafe_allow_html=True)
            st.markdown(md)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Run in full pipeline mode to generate the proposal.")

    with t5:
        out_path = Path(st.session_state.get("out_path", "outputs"))
        files = list(out_path.glob("*")) if out_path.exists() else []
        if files:
            st.markdown(f"**Output directory:** `{out_path}`")
            for f in sorted(files):
                content = f.read_bytes()
                col_name, col_dl = st.columns([3, 1])
                with col_name:
                    st.markdown(f"`{f.name}` — {len(content)/1024:.1f} KB")
                with col_dl:
                    st.download_button(
                        "↓",
                        data=content,
                        file_name=f.name,
                        mime="text/plain" if f.suffix in (".md", ".json", ".txt") else "application/octet-stream",
                        key=f"dl_{f.name}",
                    )
        else:
            st.info("No output files yet.")

        # Bulk download: proposal.md if exists
        proposal_path = out_path / "proposal.md"
        if proposal_path.exists():
            st.divider()
            st.download_button(
                "⬇ Download Full Proposal (.md)",
                data=proposal_path.read_bytes(),
                file_name=f"{proposal_number}_proposal.md",
                mime="text/markdown",
                use_container_width=True,
            )

# ── Pipeline History ───────────────────────────────────────────────────────

st.divider()
st.markdown('<div class="section-header"><div class="section-dot" style="background:#A78BFA;box-shadow:0 0 8px rgba(167,139,250,0.6)"></div><div class="section-title">Pipeline History</div></div>', unsafe_allow_html=True)

history_root = Path("outputs")
if history_root.exists():
    runs = sorted([d for d in history_root.iterdir() if d.is_dir()], reverse=True)
    if runs:
        for run_dir in runs[:10]:
            meta_path = run_dir / "proposal_meta.json"
            if not meta_path.exists():
                continue
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                with st.expander(f"**{meta.get('proposal_number', run_dir.name)}** — {meta.get('client', '?')} · {meta.get('service', '?')}"):
                    hc1, hc2, hc3, hc4 = st.columns(4)
                    hc1.metric("Proposal No.", meta.get("proposal_number", "—"))
                    hc2.metric("Client", meta.get("client", "—"))
                    hc3.metric("Service", meta.get("service", "—"))
                    hc4.metric("Tier", meta.get("tier", "—"))
                    proposal_md = run_dir / "proposal.md"
                    if proposal_md.exists():
                        st.download_button(
                            "⬇ Download Proposal",
                            data=proposal_md.read_bytes(),
                            file_name=f"{meta.get('proposal_number', run_dir.name)}_proposal.md",
                            mime="text/markdown",
                            key=f"hist_{run_dir.name}",
                        )
            except Exception:
                pass
    else:
        st.markdown('<div style="color:#484F58;font-size:0.85rem;font-family:monospace">No runs yet — generate a proposal above.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="color:#484F58;font-size:0.85rem;font-family:monospace">outputs/ directory will appear after first run.</div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────

st.markdown("""
<div style="margin-top:3rem;padding:1.5rem;border-top:1px solid #21262D;text-align:center">
    <div style="font-size:0.75rem;color:#484F58;font-family:'JetBrains Mono',monospace;line-height:1.8">
        Proposal Engine · Agentic Pre-Sales Automation · Powered by Groq + Llama 3
    </div>
    <div style="margin-top:6px;font-size:0.7rem;color:#30363D;font-family:'JetBrains Mono',monospace">
        Built by <a href="https://sanjayrkshetty.vercel.app" target="_blank"
            style="color:#58A6FF;text-decoration:none">Sanjay R K Shetty</a>
        &nbsp;·&nbsp;
        <a href="https://github.com/sanjayrkshetty/proposal-engine" target="_blank"
            style="color:#58A6FF;text-decoration:none">github.com/sanjayrkshetty/proposal-engine</a>
        &nbsp;·&nbsp; © 2026 Sanjay R K Shetty · All rights reserved
    </div>
</div>
""", unsafe_allow_html=True)
