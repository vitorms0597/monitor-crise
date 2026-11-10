"""Países: códigos, nomes e descoberta do país de uma coordenada (sem geocoder externo)."""
import json
from functools import cache
from pathlib import Path

HERE = Path(__file__).parent


@cache
def countries():
    return {c["iso3"]: c for c in json.loads((HERE / "countries.json").read_text())}


@cache
def _by_fips():
    return {f: c["iso3"] for c in reversed(list(countries().values())) for f in c["fips"]}


@cache
def _by_name():
    out = {}
    for c in countries().values():
        for n in (c["nome_en"], c["nome"]):
            out[n.lower()] = c["iso3"]
    out.update({"usa": "USA", "united states": "USA", "russia": "RUS", "south korea": "KOR",
                "north korea": "PRK", "dr congo": "COD", "congo": "COG", "czech republic": "CZE",
                "the bahamas": "BHS", "taiwan": "TWN", "laos": "LAO", "vietnam": "VNM",
                "iran": "IRN", "syria": "SYR", "bolivia": "BOL", "venezuela": "VEN",
                "tanzania": "TZA", "solomon islands": "SLB", "papua new guinea": "PNG",
                "fiji": "FJI", "tonga": "TON", "vanuatu": "VUT", "philippines": "PHL",
                "northern mariana islands": "MNP", "puerto rico": "PRI", "guam": "GUM"})
    return out


# Estados americanos aparecem sozinhos nas descrições do USGS ("10 km N of X, Alaska").
US_STATES = {"alaska", "california", "hawaii", "nevada", "washington", "oregon", "idaho", "montana",
             "wyoming", "utah", "texas", "oklahoma", "new mexico", "arizona", "colorado", "kansas",
             "tennessee", "arkansas", "missouri", "kentucky", "ca", "ak", "hi", "nv", "wa", "or",
             "id", "mt", "wy", "ut", "tx", "ok", "nm", "az", "co", "ks", "tn"}


def from_fips(code):
    return _by_fips().get(code)


def from_name(name):
    if not name:
        return None
    n = name.strip().lower()
    if n in US_STATES:
        return "USA"
    return _by_name().get(n)


@cache
def _polygons():
    data = json.loads((HERE / "countries-50m.geojson").read_text())
    polys = []
    for f in data["features"]:
        g = f["geometry"]
        parts = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for rings in parts:
            xs = [p[0] for p in rings[0]]
            ys = [p[1] for p in rings[0]]
            polys.append((f["properties"]["iso3"], (min(xs), min(ys), max(xs), max(ys)), rings))
    return polys


def _in_ring(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def country_at(lon, lat):
    """ISO3 do país que contém o ponto, ou None (mar aberto)."""
    if lon is None or lat is None:
        return None
    for iso3, (x0, y0, x1, y1), rings in _polygons():
        if x0 <= lon <= x1 and y0 <= lat <= y1 and _in_ring(lon, lat, rings[0]):
            if not any(_in_ring(lon, lat, hole) for hole in rings[1:]):
                return iso3
    return None
