#!/usr/bin/env python3
"""Proposal Engine Proposal Engine — Multi-BU CLI entry point."""

import os
import sys
import click
import yaml
import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Inject GROQ API key before any agent imports
os.environ["GROQ_API_KEY"] = "os.environ.get("GROQ_API_KEY", "")"

from agents.questionnaire_agent import QuestionnaireAgent
from agents.discovery_agent import DiscoveryAgent
from agents.scoping_agent import ScopingAgent
from agents.pricing_agent import PricingAgent
from agents.proposal_agent import ProposalAgent
from agents.gam_agent import GAMAgent

console = Console()

REGIONS = ["India-North", "India-South", "MEE", "SEA", "NA"]


def load_all_services() -> dict:
    config_path = Path("config/services.yaml")
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config["services"]


def load_service_config(service_code: str) -> dict:
    services = load_all_services()
    if service_code not in services:
        available = list(services.keys())
        raise ValueError(f"Unknown service: {service_code}. Available: {available}")
    return services[service_code]


def get_next_proposal_number(service_config: dict, region: str) -> str:
    seq_path = Path("config/proposal_sequences.json")
    if seq_path.exists():
        with open(seq_path, encoding="utf-8") as f:
            sequences = json.load(f)
    else:
        sequences = {}

    fmt = service_config.get("proposal_number_format", "Proposal Engine-{BU}-{YEAR}-{SEQ:04d}")
    bu = service_config.get("bu", "Proposal Engine").upper()
    year = datetime.now().strftime("%Y")
    region_code = region.replace("-", "").upper()[:6] if region else "IN"

    # Key for this format type
    seq_key = f"{bu}_{year}_{region_code}"
    current_seq = sequences.get(seq_key, 0) + 1
    sequences[seq_key] = current_seq

    # Persist
    with open(seq_path, "w", encoding="utf-8") as f:
        json.dump(sequences, f, indent=2)

    # Format the proposal number
    proposal_num = fmt.format(
        YEAR=year,
        REGION=region_code,
        BU=bu,
        SEQ=current_seq,
    )
    return proposal_num


def service_autocomplete(ctx, param, incomplete):
    services = load_all_services()
    return [k for k in services.keys() if k.startswith(incomplete.upper())]


@click.command()
@click.option("--service", required=True, help="Service code (e.g. DFIR-R-ENT, CTS-APP-WAPT)")
@click.option("--client", default="Unknown Client", help="Client name")
@click.option("--industry", default="Financial Services", help="Client industry")
@click.option("--size", default="Mid-market (500-5000 employees)", help="Client size")
@click.option("--bu", default=None, help="Business unit filter (dfir, mxdr, dpg, cts, institute, quantum)")
@click.option("--tier", default=None, help="Override tier (Essential, Enterprise, Elite)")
@click.option("--gam", default=None, help="Override GAM name for billing contact")
@click.option("--region", default="India-South",
              type=click.Choice(REGIONS, case_sensitive=False),
              help="Client region")
@click.option("--exec-summary", "exec_summary", default=None,
              help="Executive summary context (1-2 sentences for proposal personalisation)")
@click.option("--mode", default="full",
              type=click.Choice(["full", "discovery", "scope", "proposal"], case_sensitive=False),
              help="Pipeline mode")
@click.option("--input", "input_file", default=None,
              help="Path to existing discovery brief JSON (for scope/proposal modes)")
@click.option("--discount", default=0.0, type=float,
              help="Discount percentage to apply (0-100)")
@click.option("--output-dir", default="outputs", help="Output directory root")
def main(service, client, industry, size, bu, tier, gam, region,
         exec_summary, mode, input_file, discount, output_dir):
    """Proposal Engine Proposal Engine — agentic multi-BU pre-sales automation."""

    # Load and validate service config
    try:
        service_config = load_service_config(service)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    # Startup banner
    console.print(Panel(
        f"[bold cyan]Proposal Engine Proposal Engine[/bold cyan]\n"
        f"Service: [yellow]{service_config['name']}[/yellow] ({service})\n"
        f"BU: [blue]{service_config['bu'].upper()}[/blue] | "
        f"Tier: [green]{service_config.get('tier', 'Standard')}[/green] | "
        f"Region: [magenta]{region}[/magenta]\n"
        f"Client: [white]{client}[/white] | Mode: [cyan]{mode}[/cyan]",
        title="[bold]Proposal Engine Proposal Engine — Starting[/bold]",
        border_style="cyan"
    ))

    # Output path
    timestamp = datetime.now().strftime("%Y-%m-%d")
    client_slug = client.replace(" ", "-").replace("/", "-")[:30]
    run_id = f"{timestamp}_{client_slug}_{service_config['bu'].upper()}_{service}"
    out_path = Path(output_dir) / run_id
    out_path.mkdir(parents=True, exist_ok=True)

    # GAM resolution
    console.print("\n[bold]GAM Check[/bold]")
    gam_agent = GAMAgent({})
    stale = gam_agent.check_stale()
    if stale:
        console.print(f"  [yellow]⚠ Stale GAM accounts ({len(stale)}):[/yellow] "
                      f"{', '.join([g['name'] for g in stale])}")
    if gam:
        gam_data_raw = gam_agent.resolve_by_name(gam)
    else:
        gam_data_raw = gam_agent.resolve(region)
    billing_block = gam_agent.format_billing_block(gam_data_raw)
    gam_result = {"billing_block": billing_block, "gam": gam_data_raw}
    console.print(f"  [green]✓[/green] GAM resolved: {gam_data_raw.get('name', 'Unknown')} "
                  f"({gam_data_raw.get('email', '')})")

    # Client info dict
    client_info = {
        "name": client,
        "industry": industry,
        "size": size,
        "region": region,
        "exec_summary": exec_summary or "",
        "scope_context": "",
    }

    # Generate proposal number early (persists regardless of mode)
    proposal_number = get_next_proposal_number(service_config, region)
    console.print(f"\n  [dim]Proposal Number:[/dim] [bold]{proposal_number}[/bold]")

    brief = None
    scope = None
    questionnaire_result = None

    # ── Phase 0: Questionnaire ─────────────────────────────────────────────
    if mode in ("full",):
        console.print("\n[bold]Phase 0 — Questionnaire[/bold]")
        q_agent = QuestionnaireAgent(service_config)
        questionnaire_result = q_agent.run(
            bu=service_config["bu"],
            sub_bu=service_config.get("sub_bu", ""),
            client_info=client_info,
        )
        (out_path / "questionnaire.json").write_text(
            json.dumps(questionnaire_result, indent=2), encoding="utf-8"
        )
        # Inject scope context into client_info
        if questionnaire_result.get("scope_context"):
            client_info["scope_context"] = questionnaire_result["scope_context"]
        console.print(f"  [green]✓[/green] Questionnaire complete → {out_path}/questionnaire.json")

    # ── Phase 1: Discovery ─────────────────────────────────────────────────
    if mode in ("full", "discovery"):
        console.print("\n[bold]Phase 1 — Discovery[/bold]")
        d_agent = DiscoveryAgent(service_config)
        brief = d_agent.run(client_info)
        # Apply tier override
        if tier:
            brief["data"]["recommended_tier"] = tier
        (out_path / "discovery_brief.md").write_text(brief["markdown"], encoding="utf-8")
        (out_path / "discovery_brief.json").write_text(
            json.dumps(brief["data"], indent=2), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Discovery brief → {out_path}/discovery_brief.md")

    # Load brief from file if provided
    if input_file and not brief:
        with open(input_file, encoding="utf-8") as f:
            brief = {"data": json.load(f)}

    # ── Phase 2: Scoping ───────────────────────────────────────────────────
    if mode in ("full", "scope") and brief:
        console.print("\n[bold]Phase 2 — Scoping[/bold]")
        s_agent = ScopingAgent(service_config)
        scope = s_agent.run(brief["data"], client_info)
        (out_path / "scope_estimate.md").write_text(scope["markdown"], encoding="utf-8")
        (out_path / "scope_estimate.json").write_text(
            json.dumps(scope["data"], indent=2), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Scope estimate → {out_path}/scope_estimate.md")

    # ── Phase 3: Pricing ───────────────────────────────────────────────────
    pricing_result = None
    if mode in ("full",) and scope:
        console.print("\n[bold]Phase 3 — Pricing[/bold]")
        p_agent = PricingAgent(service_config)
        # Determine quantity from scope
        effort = scope["data"].get("effort_days", {})
        qty = effort.get("total", 1) or 1
        pricing_result = p_agent.build_pricing_table(
            service_code=service,
            qty=qty,
            region=region,
            discount_pct=discount,
        )
        # Check inflation
        acv = pricing_result.get("total_inr", 0)
        inflation = p_agent.check_inflation(acv, region, service_config["bu"])
        if inflation.get("alert"):
            console.print(
                Panel(
                    f"[yellow]⚠ INFLATION ALERT[/yellow]\n"
                    f"ACV {pricing_result.get('currency', 'INR')} {acv:,.0f} exceeds baseline "
                    f"by {inflation.get('deviation_pct', 0):.1f}%\n"
                    f"Threshold: {inflation.get('threshold_pct', 20)}%",
                    border_style="yellow",
                    title="Pricing Alert"
                )
            )
        # Discount gate
        if discount > 0 and pricing_result.get("discount_approval_required"):
            approval_msg = (
                f"Discount of {discount}% exceeds the approval threshold "
                f"({pricing_result.get('discount_threshold', 10)}%) for {service}.\n"
                f"Please obtain approval from Sales Director before sending proposal."
            )
            (out_path / "discount_approval_required.txt").write_text(
                approval_msg, encoding="utf-8"
            )
            console.print(
                Panel(
                    f"[red]⚠ DISCOUNT APPROVAL REQUIRED[/red]\n{approval_msg}",
                    border_style="red",
                    title="Discount Gate"
                )
            )
        (out_path / "pricing_table.json").write_text(
            json.dumps(pricing_result, indent=2), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Pricing table → {out_path}/pricing_table.json")
        if pricing_result.get("pricing_table_md"):
            console.print(pricing_result["pricing_table_md"])

    # ── Phase 4: Proposal ──────────────────────────────────────────────────
    if mode in ("full", "proposal") and brief and scope:
        console.print("\n[bold]Phase 4 — Proposal[/bold]")
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
            json.dumps({k: v for k, v in proposal["data"].items()
                        if k != "proposal_text"}, indent=2),
            encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Proposal → {out_path}/proposal.md")

    # Summary
    console.print(Panel(
        f"[bold green]Pipeline Complete[/bold green]\n"
        f"Proposal No: [bold]{proposal_number}[/bold]\n"
        f"Output: {out_path}/",
        title="Done",
        border_style="green"
    ))

    return str(out_path)


if __name__ == "__main__":
    main()
