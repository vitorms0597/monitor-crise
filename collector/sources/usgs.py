"""Terremotos M4.5+ do USGS (feed GeoJSON, atualizado a cada minuto)."""
import re
from datetime import UTC, datetime

from .. import geo, http
from ..model import Event

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
ALERT_BOOST = {"yellow": 1, "orange": 2, "red": 3}
PLACE_RX = re.compile(r"^(\d+) km [NSEW]{1,3} of (.+)$")
REGION_RX = re.compile(r"^(north|south|east|west)(?:ern)? of (?:the )?(.+)$", re.I)
PONTOS = {"north": "norte", "south": "sul", "east": "leste", "west": "oeste"}


def _country_pt(where):
    head, _, tail = where.rpartition(", ")
    iso = geo.from_name(tail)
    if head and iso and iso != "USA":
        return f"{head}, {geo.countries()[iso]['nome']}"
    return where


def place_pt(place):
    """'90 km SSE of Tateyama, Japan' -> 'a 90 km de Tateyama, Japão'"""
    if m := PLACE_RX.match(place or ""):
        return f"a {m.group(1)} km de {_country_pt(m.group(2))}"
    if m := REGION_RX.match(place or ""):
        return f"ao {PONTOS[m.group(1).lower()]} de {m.group(2)}"
    return f"— {_country_pt(place)}"


def _iso(ms):
    return datetime.fromtimestamp(ms / 1000, UTC).isoformat(timespec="seconds")


def severity(mag, alert=None):
    base = 1 if mag < 5.5 else 2 if mag < 6.5 else 3 if mag < 7.5 else 4
    return min(5, base + ALERT_BOOST.get(alert or "", 0))


def _country(place, lon, lat):
    iso = geo.country_at(lon, lat)
    if iso or not place:
        return iso
    tail = place.split(",")[-1].strip()
    return geo.from_name(tail.removesuffix(" region").removeprefix("off the coast of ").strip())


def parse(data):
    out = []
    for f in data.get("features", []):
        p = f["properties"]
        if p.get("type") != "earthquake" or p.get("mag") is None:
            continue
        lon, lat = f["geometry"]["coordinates"][:2]
        mag = round(p["mag"], 1)
        place = p.get("place") or ""
        mag_pt = f"{mag:.1f}".replace(".", ",")
        out.append(Event(
            id=f"usgs:{f['id']}",
            tipo="evento",
            tema="desastre",
            subtema="terremoto",
            titulo=f"Terremoto de magnitude {mag_pt} {place_pt(place)}" if place else f"Terremoto de magnitude {mag_pt}",
            fonte="USGS",
            fonte_url=p["url"],
            publicado_em=_iso(p["time"]),
            atualizado_em=_iso(p["updated"]),
            severidade=severity(mag, p.get("alert")),
            pais_iso=_country(place, lon, lat),
            lat=lat,
            lon=lon,
        ))
    return out


def fetch():
    return parse(http.get_json(URL))
