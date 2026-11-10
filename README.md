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

## Publicar (uma vez)

1. Crie um repositório **público** no GitHub (minutos de Actions ilimitados) e faça push deste projeto.
2. No Cloudflare (plano grátis), crie o projeto Pages: `npx wrangler pages project create monitor-crises --production-branch=main`.
3. Gere um API token no Cloudflare com permissão *Cloudflare Pages: Edit*.
4. No GitHub, em *Settings → Secrets and variables → Actions*:
   - secrets `CLOUDFLARE_API_TOKEN` e `CLOUDFLARE_ACCOUNT_ID`
   - variável `SITE_URL` (ex.: `https://monitordecrises.com.br`)
5. Rode o workflow **Coleta e deploy** manualmente uma vez com `backfill_horas = 48`.
6. Aponte o domínio para o projeto em *Cloudflare Pages → Custom domains*.

Os dados ficam no branch `data`, regravado a cada coleta como um único commit (o repositório não cresce).

## Anúncios

Variáveis de build (opcionais): `PUBLIC_ADSENSE_CLIENT` (ex.: `ca-pub-123…`), `PUBLIC_AADS_UNIT`, `PUBLIC_CONTACT_EMAIL`.
Sem elas, os espaços de anúncio aparecem reservados e vazios.
