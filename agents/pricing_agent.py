"""Pricing Agent — codebook-driven pricing table, discount gate, inflation alert."""
import os
from pathlib import Path
import yaml
from .base_agent import BaseAgent

os.environ.setdefault("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")

PRICING_BASELINE_PATH = Path("config/pricing_baseline.yaml")


class PricingAgent(BaseAgent):
    def __init__(self, service_config: dict):
        super().__init__(service_config)
        self._baseline_data = None

    def _load_codebook(self, codebook_path: str) -> dict:
        path = Path(codebook_path)
        if not path.exists():
            return {}
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_baseline(self) -> dict:
        if self._baseline_data is None:
            with open(PRICING_BASELINE_PATH, encoding="utf-8") as f:
                self._baseline_data = yaml.safe_load(f)
        return self._baseline_data

    def run(self, *args, **kwargs) -> dict:
        """Satisfy abstract method — delegates to build_pricing_table()."""
        service_code = kwargs.get("service_code") or self.config.get("code", "")
        qty = kwargs.get("qty", 1)
        region = kwargs.get("region", "India-South")
        discount_pct = kwargs.get("discount_pct", 0)
        result = self.build_pricing_table(service_code, qty, region, discount_pct)
        return {"data": result, "markdown": result.get("pricing_table_md", "")}

    def build_pricing_table(self, service_code: str, qty: int = 1,
                             region: str = "India-South", discount_pct: float = 0) -> dict:
        """Build a pricing table for the given service/qty/region/discount.

        Returns dict with:
          - unit_price_inr: base INR price
          - unit_price_regional: price after regional multiplier
          - qty: quantity
          - subtotal_inr: subtotal before discount
          - discount_pct: applied discount
          - discount_approval_required: bool
          - discount_threshold: threshold for this service
          - total_inr: final total
          - currency: display currency label
          - pricing_table_md: formatted Markdown table
          - unit: unit description
          - notes: codebook notes
        """
        codebook_path = self.config.get("codebook_path", f"bu/{self.config.get('bu', 'dfir')}/codebook.yaml")
        codebook = self._load_codebook(codebook_path)
        services_data = codebook.get("services", {})
        regional_multipliers = codebook.get("regional_multipliers", {})

        service_entry = services_data.get(service_code, {})

        # Fallback: use unit price from first matching service if not found directly
        if not service_entry and services_data:
            service_entry = next(iter(services_data.values()), {})

        unit_price_inr = float(service_entry.get("unit_price_inr", 500000))
        unit = service_entry.get("unit", "engagement")
        notes = service_entry.get("notes", "")
        discount_threshold = float(service_entry.get("discount_threshold_pct", 10))
        min_qty = int(service_entry.get("min_qty", 1))
        max_qty = int(service_entry.get("max_qty", 99))

        # Apply min/max qty
        qty = max(min_qty, min(qty, max_qty))

        # Regional multiplier
        multiplier = float(regional_multipliers.get(region, 1.0))

        # Currency label based on region
        if region in ("MEE",):
            currency = "USD"
            # Rough USD conversion: 1 USD ≈ 83 INR
            unit_price_display = unit_price_inr * multiplier / 83
        elif region == "NA":
            currency = "USD"
            unit_price_display = unit_price_inr * multiplier / 83
        elif region == "SEA":
            currency = "SGD"
            # 1 SGD ≈ 61 INR
            unit_price_display = unit_price_inr * multiplier / 61
        else:
            currency = "INR"
            unit_price_display = unit_price_inr * multiplier

        unit_price_regional = unit_price_inr * multiplier
        subtotal_inr = unit_price_regional * qty
        subtotal_display = unit_price_display * qty

        # Discount calculation
        discount_amount_inr = subtotal_inr * (discount_pct / 100)
        discount_amount_display = subtotal_display * (discount_pct / 100)
        total_inr = subtotal_inr - discount_amount_inr
        total_display = subtotal_display - discount_amount_display

        discount_approval_required = discount_pct > discount_threshold

        # Format currency symbol
        sym = {"INR": "₹", "USD": "$", "SGD": "S$"}.get(currency, "")

        # Build Markdown table
        md_lines = [
            f"| Item | Unit Price ({currency}) | Qty | Subtotal ({currency}) |",
            "|------|----------------------|-----|----------------------|",
            f"| {self.config.get('name', service_code)} | {sym}{unit_price_display:,.0f}/{unit} "
            f"| {qty} | {sym}{subtotal_display:,.0f} |",
        ]
        if discount_pct > 0:
            md_lines.append(
                f"| Discount ({discount_pct:.0f}%) | — | — | -{sym}{discount_amount_display:,.0f} |"
            )
        md_lines.append(
            f"| **Total** | — | — | **{sym}{total_display:,.0f}** |"
        )
        if notes:
            md_lines.append(f"\n*{notes}*")
        md_lines.append(f"\n*All prices exclusive of applicable taxes.*")

        pricing_table_md = "\n".join(md_lines)

        return {
            "service_code": service_code,
            "unit_price_inr": unit_price_inr,
            "unit_price_regional_inr": unit_price_regional,
            "unit_price_display": unit_price_display,
            "currency": currency,
            "qty": qty,
            "unit": unit,
            "subtotal_inr": subtotal_inr,
            "discount_pct": discount_pct,
            "discount_threshold": discount_threshold,
            "discount_approval_required": discount_approval_required,
            "discount_amount_inr": discount_amount_inr,
            "total_inr": total_inr,
            "total_display": total_display,
            "region": region,
            "multiplier": multiplier,
            "notes": notes,
            "pricing_table_md": pricing_table_md,
        }

    def check_inflation(self, acv_inr: float, region: str, bu: str) -> dict:
        """Check if ACV deviates significantly from baseline. Returns alert dict."""
        try:
            baseline_data = self._load_baseline()
        except FileNotFoundError:
            return {"alert": False}

        threshold_pct = float(baseline_data.get("inflation_alert_threshold_pct", 20))
        baselines = baseline_data.get("baselines", {})
        bu_baselines = baselines.get(bu.lower(), {})
        expected_acv = float(bu_baselines.get(region, 0))

        if expected_acv <= 0:
            return {"alert": False}

        deviation_pct = ((acv_inr - expected_acv) / expected_acv) * 100

        alert = deviation_pct > threshold_pct

        return {
            "alert": alert,
            "acv_inr": acv_inr,
            "expected_acv_inr": expected_acv,
            "deviation_pct": deviation_pct,
            "threshold_pct": threshold_pct,
            "region": region,
            "bu": bu,
        }

    def format_pricing_table(self, pricing_dict: dict) -> str:
        """Return the Markdown pricing table from a pricing dict."""
        return pricing_dict.get("pricing_table_md", "")
