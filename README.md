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

## Publicação

Hoje o repositório é privado e o site **não está publicado**. O workflow **Coleta e deploy** só roda
manualmente (*Actions → Coleta e deploy → Run workflow*): coleta, grava os dados no branch `data` e gera o site.

Para publicar no GitHub Pages (`https://vitorms0597.github.io/monitor-crise/`):
1. Torne o repositório público (Pages grátis) ou assine o GitHub Pro.
2. *Settings → Pages → Source: GitHub Actions*.
3. *Settings → Secrets and variables → Actions → Variables*: crie `PUBLICAR = sim`.
4. Descomente o `schedule` no workflow (coleta a cada 30 min) e rode uma vez com `backfill_horas = 48`.

Repositório privado no plano grátis tem 2.000 minutos de Actions por mês; a coleta a cada 30 min gasta
cerca de 5.000. Se ficar privado, use um intervalo de 2 horas (`0 */2 * * *`).

Domínio próprio: configure em *Settings → Pages → Custom domain* e crie as variáveis `SITE_URL=https://seudominio.com.br`
e `BASE_PATH=/`.

## Anúncios

Variáveis de build (opcionais): `PUBLIC_ADSENSE_CLIENT` (ex.: `ca-pub-123…`), `PUBLIC_AADS_UNIT`, `PUBLIC_CONTACT_EMAIL`.
Sem elas, os espaços de anúncio aparecem reservados e vazios.
