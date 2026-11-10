"""Gera as tabelas de países a partir do Natural Earth (rodar só quando quiser atualizar).

Uso: python tools/build_geo.py
Saídas:
  collector/geo/countries.json          códigos ISO3/FIPS/nomes por país
  collector/geo/countries-50m.geojson   fronteiras p/ descobrir o país de uma coordenada
  site/public/geo/countries-110m.geojson fronteiras leves p/ o mapa do site
"""
import json
import re
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_{}_admin_0_countries.geojson"

# Natural Earth não traz FIPS para alguns países; GDELT usa estes códigos.
FIPS_OVERRIDES = {"SSD": ["OD"], "NOR": ["NO"], "ISR": ["IS"], "PSE": ["WE", "GZ"], "KOS": ["KV"]}
SKIP = {"ALD", "IOA", "KAS"}  # Åland, Ter. australianos do Índico, Siachen

# Natural Earth traz os nomes em português de Portugal; o site é PT-BR.
PT_BR = {
    "Arménia": "Armênia", "Benim": "Benin", "Chéquia": "Tchéquia", "Eslovénia": "Eslovênia", "Estónia": "Estônia",
    "Ilhas Caimão": "Ilhas Cayman", "Ilhas Feroe": "Ilhas Faroé", "Irão": "Irã", "Iémen": "Iêmen", "Letónia": "Letônia",
    "Macedónia do Norte": "Macedônia do Norte", "Madagáscar": "Madagascar", "Malawi": "Malauí", "Maurícia": "Maurício",
    "Mónaco": "Mônaco", "Nova Caledónia": "Nova Caledônia", "Polónia": "Polônia", "Quénia": "Quênia",
    "Roménia": "Romênia", "Sara Ocidental": "Saara Ocidental", "Tajiquistão": "Tadjiquistão", "Vietname": "Vietnã",
    "República da Irlanda": "Irlanda", "Coletividade de São Bartolomeu": "São Bartolomeu", "Antártida": "Antártida",
}


def nome_pt(p):
    nome = p["NAME_PT"] or p["NAME"]
    return PT_BR.get(nome, nome)


def fetch(scale):
    with urllib.request.urlopen(NE.format(scale), timeout=120) as r:
        return json.load(r)


def iso3(p):
    return p["ISO_A3_EH"] if p["ISO_A3_EH"] != "-99" else p["ADM0_A3"]


def slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def round_coords(c):
    if isinstance(c[0], (int, float)):
        return [round(c[0], 3), round(c[1], 3)]
    return [round_coords(x) for x in c]


def main():
    ne50 = fetch("50m")
    countries, features = {}, []
    for f in ne50["features"]:
        p = f["properties"]
        if p["ADM0_A3"] in SKIP:
            continue
        code = iso3(p)
        fips = FIPS_OVERRIDES.get(code) or ([p["FIPS_10"]] if p["FIPS_10"] != "-99" else [])
        if code not in countries:
            countries[code] = {
                "iso3": code,
                "iso2": p["ISO_A2_EH"] if p["ISO_A2_EH"] != "-99" else None,
                "fips": fips,
                "nome": nome_pt(p),
                "nome_en": p["NAME_EN"] or p["NAME"],
                "slug": slug(nome_pt(p)),
                "continente": p["CONTINENT"],
                "centro": [round(p["LABEL_X"], 3), round(p["LABEL_Y"], 3)],
            }
        features.append({"type": "Feature", "properties": {"iso3": code},
                         "geometry": {"type": f["geometry"]["type"],
                                      "coordinates": round_coords(f["geometry"]["coordinates"])}})

    out = ROOT / "collector" / "geo"
    out.mkdir(parents=True, exist_ok=True)
    (out / "countries.json").write_text(json.dumps(sorted(countries.values(), key=lambda c: c["iso3"]),
                                                   ensure_ascii=False, indent=1))
    (out / "countries-50m.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": features},
                                                          separators=(",", ":")))

    ne110 = fetch("110m")
    small = []
    for f in ne110["features"]:
        p = f["properties"]
        code = iso3(p)
        small.append({"type": "Feature", "properties": {"iso3": code, "nome": nome_pt(p)},
                      "geometry": {"type": f["geometry"]["type"],
                                   "coordinates": round_coords(f["geometry"]["coordinates"])}})
    site = ROOT / "site" / "public" / "geo"
    site.mkdir(parents=True, exist_ok=True)
    (site / "countries-110m.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": small},
                                                            ensure_ascii=False, separators=(",", ":")))
    print(f"{len(countries)} países, {len(features)} polígonos 50m, {len(small)} polígonos 110m")


if __name__ == "__main__":
    main()
