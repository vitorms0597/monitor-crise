# Monitor de Crises

Site em PT-BR que agrega eventos de ciberataques, guerras/conflitos, apagões e desastres no mundo,
com mapa de calor dos temas mais falados por país.

- `collector/`: coletor Python (USGS, GDACS, NASA EONET, CISA KEV, GDELT) → `data/*.json`
- `site/`: site estático (Astro + MapLibre) que lê `data/` no build
- `tools/build_geo.py`: regenera as tabelas de países a partir do Natural Earth

```bash
python3 -m venv .venv && .venv/bin/pip install httpx pytest
.venv/bin/python -m collector          # coleta e grava em data/
.venv/bin/python -m pytest             # testes
```
