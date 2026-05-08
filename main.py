#!/usr/bin/env python3
"""Proposal Engine Proposal Engine — CLI entry point."""

import click
import yaml
import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agents.discovery_agent import DiscoveryAgent
from agents.scoping_agent import ScopingAgent
from agents.proposal_agent import ProposalAgent

console = Console()

def load_service_config(service_code: str) -> dict:
    config_path = Path("config/services.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    if service_code not in config["services"]:
        raise ValueError(f"Unknown service: {service_code}. Available: {list(config['services'].keys())}")
    return config["services"][service_code]

@click.command()
@click.option("--service", required=True, type=click.Choice(["DFIR-R", "IFI", "CA", "BAS"]), help="Service line")
@click.option("--client", default=None, help="Client name")
@click.option("--industry", default=None, help="Client industry")
@click.option("--size", default=None, help="Client size (e.g. 5000 employees)")
@click.option("--mode", default="full", type=click.Choice(["full", "discovery", "scope", "proposal"]))
@click.option("--input", "input_file", default=None, help="Path to existing brief JSON (for scope/proposal modes)")
@click.option("--output-dir", default="outputs", help="Output directory")
def main(service, client, industry, size, mode, input_file, output_dir):
    """Proposal Engine Proposal Engine — agentic pre-sales automation."""

    service_config = load_service_config(service)

    console.print(Panel(
        f"[bold cyan]Proposal Engine Proposal Engine[/bold cyan]\n"
        f"Service: [yellow]{service_config['name']}[/yellow]\n"
        f"Mode: [green]{mode}[/green]",
        title="Starting"
    ))

    client_info = {"name": client, "industry": industry, "size": size}
    timestamp = datetime.now().strftime("%Y-%m-%d")
    run_id = f"{timestamp}_{(client or 'unknown').replace(' ', '-')}_{service}"
    out_path = Path(output_dir) / run_id
    out_path.mkdir(parents=True, exist_ok=True)

    brief = None
    scope = None

    # Discovery
    if mode in ("full", "discovery"):
        console.print("\n[bold]Phase 1 — Discovery[/bold]")
        agent = DiscoveryAgent(service_config)
        brief = agent.run(client_info)
        (out_path / "discovery_brief.md").write_text(brief["markdown"])
        (out_path / "discovery_brief.json").write_text(json.dumps(brief["data"], indent=2))
        console.print(f"  [green]✓[/green] Discovery brief → {out_path}/discovery_brief.md")

    # Load brief from file if provided
    if input_file and not brief:
        with open(input_file) as f:
            brief = {"data": json.load(f)}

    # Scoping
    if mode in ("full", "scope") and brief:
        console.print("\n[bold]Phase 2 — Scoping[/bold]")
        agent = ScopingAgent(service_config)
        scope = agent.run(brief["data"], client_info)
        (out_path / "scope_estimate.md").write_text(scope["markdown"])
        console.print(f"  [green]✓[/green] Scope estimate → {out_path}/scope_estimate.md")

    # Proposal
    if mode in ("full", "proposal") and brief and scope:
        console.print("\n[bold]Phase 3 — Proposal[/bold]")
        agent = ProposalAgent(service_config)
        proposal = agent.run(brief["data"], scope["data"], client_info)
        (out_path / "proposal.md").write_text(proposal["markdown"])
        console.print(f"  [green]✓[/green] Proposal → {out_path}/proposal.md")

    console.print(f"\n[bold green]Done.[/bold green] Outputs in: {out_path}/")

if __name__ == "__main__":
    main()