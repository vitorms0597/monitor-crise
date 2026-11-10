# Monitor de Crises

Site em PT-BR que agrega ciberataques, guerras/conflitos, apagões e desastres no mundo, com mapa de calor
e "sismograma" dos temas mais falados por país. Atualiza a cada 30 minutos, com custo de infraestrutura zero.

- `collector/`: coletor Python (USGS, GDACS, NASA EONET, CISA KEV, GDELT) que grava em `data/*.json`
- `site/`: site estático (Astro) que lê `data/` no build
- `tools/build_geo.py`: regenera as tabelas de países a partir do Natural Earth
- `PRODUCT.md`: público, tom e princípios do produto

## Rodar localmente

```bash
python3 -m venv .venv && .venv/bin/pip install httpx pytest
.venv/bin/python -m collector                      # coleta e grava em data/
.venv/bin/python -m collector --backfill-horas 48  # primeira vez: preenche 48h de notícias
.venv/bin/python -m pytest

cd site && npm install && npm run dev               # http://localhost:4321
```

## Publicação (GitHub Pages)

O workflow **Coleta e deploy** roda a cada 30 minutos: coleta, grava os dados no branch `data`
(sempre um único commit, então o repositório não cresce), gera o site e publica no GitHub Pages em
`https://<usuário>.github.io/monitor-crises/`.

- Pages precisa estar ativado com origem **GitHub Actions** (*Settings → Pages*).
- Primeira publicação: rode o workflow manualmente com `backfill_horas = 48`.
- Domínio próprio: configure em *Settings → Pages → Custom domain* e crie as variáveis de repositório
  `SITE_URL=https://seudominio.com.br` e `BASE_PATH=/`.

## Anúncios

Variáveis de build (opcionais): `PUBLIC_ADSENSE_CLIENT` (ex.: `ca-pub-123…`), `PUBLIC_AADS_UNIT`, `PUBLIC_CONTACT_EMAIL`.
Sem elas, os espaços de anúncio aparecem reservados e vazios.
