"""GAM Agent — Global Account Manager resolution, stale-check, and billing block generation."""
import os
from pathlib import Path
from datetime import datetime, timedelta
import yaml
from .base_agent import BaseAgent

os.environ.setdefault("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")

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
        """Satisfy abstract method — delegates to resolve()."""
        region = kwargs.get("region") or (args[0] if args else "India-South")
        gam = self.resolve(region)
        return {
            "data": gam,
            "markdown": self.format_billing_block(gam),
        }

    def resolve(self, region: str) -> dict:
        """Return the most recently reviewed active GAM for the given region.
        Falls back to any active GAM if no regional match found."""
        data = self._load_gam_data()
        gams = data.get("gam_list", [])

        # Filter active GAMs for region
        regional = [g for g in gams if g.get("region") == region and g.get("active", True)]

        if not regional:
            # Fallback: any active GAM
            regional = [g for g in gams if g.get("active", True)]

        if not regional:
            return {
                "id": "GAM-FALLBACK",
                "name": "SISA Accounts Team",
                "email": "accounts@sisainfosec.com",
                "phone": "+91-80-4040-5000",
                "region": region,
                "title": "Accounts Team",
            }

        # Sort by last_reviewed descending (most recent first)
        def parse_date(g):
            try:
                return datetime.strptime(g.get("last_reviewed", "2020-01-01"), "%Y-%m-%d")
            except (ValueError, TypeError):
                return datetime(2020, 1, 1)

        regional_sorted = sorted(regional, key=parse_date, reverse=True)
        return regional_sorted[0]

    def resolve_by_name(self, name: str) -> dict:
        """Resolve a GAM by exact or partial name match."""
        data = self._load_gam_data()
        gams = data.get("gam_list", [])
        name_lower = name.lower()
        for gam in gams:
            if name_lower in gam.get("name", "").lower():
                return gam
        # Fallback to default
        return self.resolve("India-South")

    def check_stale(self) -> list:
        """Return list of GAMs where last_reviewed is older than stale_threshold_days."""
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
        """Return a formatted billing contact string for template injection."""
        if not gam:
            return "billing@sisainfosec.com | +91-80-4040-5000"
        lines = [
            f"**Billing Contact:** {gam.get('name', 'SISA Accounts')}",
            f"**Title:** {gam.get('title', 'Global Account Manager')}",
            f"**Email:** {gam.get('email', 'accounts@sisainfosec.com')}",
            f"**Phone:** {gam.get('phone', '+91-80-4040-5000')}",
            f"**Region:** {gam.get('region', 'India')}",
        ]
        return "\n".join(lines)

    def list_all(self) -> list:
        """Return full GAM list."""
        data = self._load_gam_data()
        return data.get("gam_list", [])
