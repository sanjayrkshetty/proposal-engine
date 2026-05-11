"""Pipeline Report — scan outputs/ and generate markdown or Excel summary."""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    RICH = True
except ImportError:
    RICH = False

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    EXCEL = True
except ImportError:
    EXCEL = False

COMPANY_NAME = os.environ.get("COMPANY_NAME", "Proposal Engine")

DARK_BG     = "FF0D1117"
HEADER_BG   = "FF1C2333"
ROW_ALT_BG  = "FF161B22"
TEXT_COLOR  = "FFC9D1D9"
ACCENT      = "FF58A6FF"
GREEN       = "FF3FB950"
YELLOW      = "FFD29922"
RED         = "FFF85149"


def scan_outputs(output_dir: str = "outputs") -> list:
    root = Path(output_dir)
    if not root.exists():
        return []

    proposals = []
    for run_dir in sorted(root.iterdir()):
        if not run_dir.is_dir():
            continue
        meta_path = run_dir / "proposal_meta.json"
        if not meta_path.exists():
            continue
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        meta["run_dir"] = str(run_dir)
        meta["run_id"] = run_dir.name
        proposals.append(meta)

    return proposals


def render_markdown_report(proposals: list) -> str:
    if not proposals:
        return "# Proposal Pipeline Report\n\nNo proposals found in outputs/.\n"

    lines = [
        f"# {COMPANY_NAME} — Proposal Pipeline Report",
        f"*Generated: {datetime.now().strftime('%d %B %Y %H:%M')}*",
        f"*Total proposals: {len(proposals)}*",
        "",
        "| Proposal No | Client | Service | Tier | Region | Date |",
        "|-------------|--------|---------|------|--------|------|",
    ]
    for p in proposals:
        lines.append(
            f"| {p.get('proposal_number', '-')} "
            f"| {p.get('client', '-')} "
            f"| {p.get('service', '-')} "
            f"| {p.get('tier', '-')} "
            f"| {p.get('region', '-')} "
            f"| {p.get('run_id', '-')[:10]} |"
        )
    return "\n".join(lines)


def render_rich_table(proposals: list):
    if not RICH:
        print(render_markdown_report(proposals))
        return

    console = Console()
    table = Table(title=f"{COMPANY_NAME} Proposal Pipeline Report", show_lines=True)
    table.add_column("Proposal No", style="bold cyan")
    table.add_column("Client", style="white")
    table.add_column("Service", style="yellow")
    table.add_column("Tier", style="green")
    table.add_column("Region", style="magenta")
    table.add_column("Date", style="dim")

    for p in proposals:
        table.add_row(
            p.get("proposal_number", "-"),
            p.get("client", "-"),
            p.get("service", "-"),
            p.get("tier", "-"),
            p.get("region", "-"),
            p.get("run_id", "-")[:10],
        )

    console.print(table)


def write_excel_report(proposals: list, output_path: str = "reports/pipeline_report.xlsx"):
    if not EXCEL:
        print("openpyxl not installed — skipping Excel export")
        return

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "All Proposals"

    def make_fill(hex_color):
        return PatternFill(fill_type="solid", fgColor=hex_color)

    def make_font(bold=False, color=TEXT_COLOR, size=11):
        return Font(bold=bold, color=color, size=size, name="Calibri")

    def make_border():
        side = Side(style="thin", color="FF30363D")
        return Border(left=side, right=side, top=side, bottom=side)

    headers = ["Proposal No", "Client", "Service", "Tier", "Region", "Date"]
    ws.append(headers)

    for cell in ws[1]:
        cell.fill = make_fill(HEADER_BG)
        cell.font = make_font(bold=True, color=ACCENT, size=12)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = make_border()

    ws.row_dimensions[1].height = 24

    for i, p in enumerate(proposals, start=2):
        row = [
            p.get("proposal_number", "-"),
            p.get("client", "-"),
            p.get("service", "-"),
            p.get("tier", "-"),
            p.get("region", "-"),
            p.get("run_id", "-")[:10],
        ]
        ws.append(row)
        bg = DARK_BG if i % 2 == 0 else ROW_ALT_BG
        for cell in ws[i]:
            cell.fill = make_fill(bg)
            cell.font = make_font()
            cell.alignment = Alignment(vertical="center")
            cell.border = make_border()

    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 28
    ws.column_dimensions["C"].width = 22
    ws.column_dimensions["D"].width = 14
    ws.column_dimensions["E"].width = 16
    ws.column_dimensions["F"].width = 16

    bus = sorted(set(p.get("service", "")[:p.get("service", "").find("-")] for p in proposals if p.get("service")))
    for bu in bus:
        bu_proposals = [p for p in proposals if p.get("service", "").startswith(bu)]
        if not bu_proposals:
            continue
        ws_bu = wb.create_sheet(title=bu[:31])
        ws_bu.append(headers)
        for cell in ws_bu[1]:
            cell.fill = make_fill(HEADER_BG)
            cell.font = make_font(bold=True, color=ACCENT)
            cell.alignment = Alignment(horizontal="center")
        for p in bu_proposals:
            ws_bu.append([
                p.get("proposal_number", "-"), p.get("client", "-"),
                p.get("service", "-"), p.get("tier", "-"),
                p.get("region", "-"), p.get("run_id", "-")[:10],
            ])

    wb.save(output_path)
    print(f"Excel report saved: {output_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Proposal Pipeline Report")
    parser.add_argument("--format", choices=["table", "markdown", "excel"], default="table")
    parser.add_argument("--output", default="reports/pipeline_report.xlsx")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    proposals = scan_outputs(args.output_dir)

    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print(f"{COMPANY_NAME} Pipeline Report — format: {args.format}")

    if args.format == "table":
        render_rich_table(proposals)
    elif args.format == "markdown":
        print(render_markdown_report(proposals))
    elif args.format == "excel":
        write_excel_report(proposals, args.output)


if __name__ == "__main__":
    main()
