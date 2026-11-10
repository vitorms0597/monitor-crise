"""Vulnerabilidades sendo exploradas por atacantes agora (catálogo KEV da CISA/EUA)."""
from datetime import UTC, datetime, timedelta

from .. import http
from ..model import Event

URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


def parse(data, *, now=None, days=30):
    now = now or datetime.now(UTC)
    cutoff = (now - timedelta(days=days)).date().isoformat()
    out = []
    for v in data.get("vulnerabilities", []):
        if v["dateAdded"] < cutoff:
            continue
        ransomware = v.get("knownRansomwareCampaignUse") == "Known"
        when = f"{v['dateAdded']}T00:00:00+00:00"
        out.append(Event(
            id=f"kev:{v['cveID']}",
            tipo="evento",
            tema="ciber",
            subtema="ransomware" if ransomware else "vulnerabilidade",
            titulo=f"Falha explorada por hackers: {v['vendorProject']} {v['product']} ({v['cveID']})",
            fonte="CISA KEV",
            fonte_url=f"https://nvd.nist.gov/vuln/detail/{v['cveID']}",
            publicado_em=when,
            atualizado_em=when,
            severidade=3 if ransomware else 2,
        ))
    return out


def fetch():
    return parse(http.get_json(URL))
