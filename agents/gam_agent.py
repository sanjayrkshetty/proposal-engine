"""GAM Agent — Global Account Manager resolution, stale-check, and billing block generation."""
from pathlib import Path
from datetime import datetime, timedelta
import yaml
from .base_agent import BaseAgent

GAM_LIST_PATH = Path("config/gam_list.yaml")


class GAMAgent(BaseAgent):
    def __init__(self, service_config: dict):
        super().__init__(service_config)
        self._gam_data = None

    def _load_gam_data(self) -> dict:
        if self._gam_data is None:
            with open(GAM_LIST_PATH, encoding="utf-8") as f:
                self._gam_data = yaml.safe_load(f)
        return self._gam_data

    def run(self, *args, **kwargs) -> dict:
        region = kwargs.get("region") or (args[0] if args else "India-South")
        gam = self.resolve(region)
        return {
            "data": gam,
            "markdown": self.format_billing_block(gam),
        }

    def resolve(self, region: str) -> dict:
        data = self._load_gam_data()
        gams = data.get("gam_list", [])

        regional = [g for g in gams if g.get("region") == region and g.get("active", True)]

        if not regional:
            regional = [g for g in gams if g.get("active", True)]

        if not regional:
            return {
                "id": "GAM-FALLBACK",
                "name": "Accounts Team",
                "email": "accounts@proposalengine.io",
                "phone": "+1-800-000-0000",
                "region": region,
                "title": "Accounts Team",
            }

        def parse_date(g):
            try:
                return datetime.strptime(g.get("last_reviewed", "2020-01-01"), "%Y-%m-%d")
            except (ValueError, TypeError):
                return datetime(2020, 1, 1)

        regional_sorted = sorted(regional, key=parse_date, reverse=True)
        return regional_sorted[0]

    def resolve_by_name(self, name: str) -> dict:
        data = self._load_gam_data()
        gams = data.get("gam_list", [])
        name_lower = name.lower()
        for gam in gams:
            if name_lower in gam.get("name", "").lower():
                return gam
        return self.resolve("India-South")

    def check_stale(self) -> list:
        data = self._load_gam_data()
        threshold_days = data.get("stale_threshold_days", 90)
        gams = data.get("gam_list", [])
        stale_cutoff = datetime.now() - timedelta(days=threshold_days)
        stale = []
        for gam in gams:
            if not gam.get("active", True):
                continue
            try:
                last_reviewed = datetime.strptime(gam.get("last_reviewed", "2020-01-01"), "%Y-%m-%d")
                if last_reviewed < stale_cutoff:
                    stale.append(gam)
            except (ValueError, TypeError):
                stale.append(gam)
        return stale

    def format_billing_block(self, gam: dict) -> str:
        if not gam:
            return "accounts@proposalengine.io | +1-800-000-0000"
        lines = [
            f"**Billing Contact:** {gam.get('name', 'Accounts Team')}",
            f"**Title:** {gam.get('title', 'Global Account Manager')}",
            f"**Email:** {gam.get('email', 'accounts@proposalengine.io')}",
            f"**Phone:** {gam.get('phone', '+1-800-000-0000')}",
            f"**Region:** {gam.get('region', 'Global')}",
        ]
        return "\n".join(lines)

    def list_all(self) -> list:
        data = self._load_gam_data()
        return data.get("gam_list", [])
