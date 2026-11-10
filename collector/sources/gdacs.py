"""Alertas do GDACS (ONU/Comissão Europeia): ciclones, enchentes, vulcões, secas, incêndios.

Terremotos ficam com o USGS, que é mais rápido e detalhado.
"""
from .. import geo, http
from ..model import Event

URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/EVENTS4APP"
SUBTEMA = {"TC": "ciclone", "FL": "enchente", "VO": "vulcao", "DR": "seca", "WF": "incendio"}
NOME = {"TC": "Ciclone tropical", "FL": "Enchente", "VO": "Erupção vulcânica", "DR": "Seca",
        "WF": "Incêndio florestal"}
SEVERIDADE = {"green": 1, "orange": 3, "red": 5}
# Alertas verdes de queimada e seca são dezenas por dia e quase nunca viram notícia.
SKIP_GREEN = {"WF", "DR"}


def _utc(s):
    return s if s.endswith("Z") or "+" in s else s + "+00:00"


def parse(data):
    out = []
    for f in data.get("features", []):
        p = f["properties"]
        kind = p.get("eventtype")
        level = (p.get("alertlevel") or "").lower()
        if kind not in SUBTEMA or (level == "green" and kind in SKIP_GREEN):
            continue
        lon, lat = f["geometry"]["coordinates"][:2]
        iso = (p.get("iso3") or "").upper() or None
        if iso not in geo.countries():
            iso = geo.country_at(lon, lat)
        where = geo.countries()[iso]["nome"] if iso else (p.get("country") or "")
        nome = p.get("eventname") or ""
        titulo = NOME[kind] + (f" {nome}" if kind == "TC" and nome else "") + (f" — {where}" if where else "")
        out.append(Event(
            id=f"gdacs:{kind}:{p['eventid']}",
            tipo="evento",
            tema="desastre",
            subtema=SUBTEMA[kind],
            titulo=titulo,
            fonte="GDACS",
            fonte_url=p["url"]["report"],
            publicado_em=_utc(p["fromdate"]),
            atualizado_em=_utc(p.get("datemodified") or p.get("todate") or p["fromdate"]),
            severidade=SEVERIDADE.get(level, 1),
            pais_iso=iso,
            lat=lat,
            lon=lon,
        ))
    return out


def fetch():
    return parse(http.get_json(URL))
