"""Eventos naturais em andamento detectados por satélite (NASA EONET v3)."""
from .. import geo, http
from ..model import Event

URL = "https://eonet.gsfc.nasa.gov/api/v3/events"
SUBTEMA = {"wildfires": ("incendio", "Incêndio florestal"), "severeStorms": ("tempestade", "Tempestade severa"),
           "volcanoes": ("vulcao", "Vulcão ativo"), "floods": ("enchente", "Enchente"),
           "landslides": ("deslizamento", "Deslizamento de terra")}
SEVERIDADE = {"incendio": 1, "tempestade": 2, "vulcao": 2, "enchente": 2, "deslizamento": 2}


def parse(data):
    out = []
    for e in data.get("events", []):
        cat = next((c["id"] for c in e.get("categories", []) if c["id"] in SUBTEMA), None)
        points = [g for g in e.get("geometry", []) if g.get("type") == "Point"]
        if not cat or not points:
            continue
        subtema, nome = SUBTEMA[cat]
        first, last = points[0], points[-1]
        lon, lat = last["coordinates"][:2]
        src = (e.get("sources") or [{}])[0]
        out.append(Event(
            id=f"eonet:{e['id']}",
            tipo="evento",
            tema="desastre",
            subtema=subtema,
            titulo=f"{nome} — {e['title']}",
            fonte="NASA EONET",
            fonte_url=src.get("url") or e["link"],
            publicado_em=first["date"].replace("Z", "+00:00"),
            atualizado_em=last["date"].replace("Z", "+00:00"),
            severidade=SEVERIDADE[subtema],
            pais_iso=geo.country_at(lon, lat),
            lat=lat,
            lon=lon,
        ))
    return out


def fetch():
    return parse(http.get_json(URL, status="open", days=14))
