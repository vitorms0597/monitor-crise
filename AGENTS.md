# AGENTS.md — Monitor de Crises

Contexto para agentes de código (Claude, Ollama, etc.). Leia inteiro antes de editar.
Documentos complementares: `PRODUCT.md` (público e princípios), `DESIGN.md` (sistema visual), `README.md` (como rodar).

## 1. O que é

Site estático em **português do Brasil** que agrega eventos de crise no mundo em 4 temas:
`conflito` (guerras, terrorismo), `ciber` (ciberataques), `energia` (apagões), `desastre` (terremotos, enchentes, etc.).
Mostra um "sismograma" (volume por hora de cada tema), um mapa de calor por país e páginas por país, tema e evento.
Objetivo do dono: audiência orgânica e receita com anúncios (AdSense / A-Ads).

## 2. Regras que não podem ser quebradas

1. **Só dados reais com fonte.** Todo item exibido tem link para a origem. Nunca inventar, inflar ou "completar" dados.
2. **Nada de conteúdo conspiratório ou alarmista.** O público desconfia da mídia tradicional, mas o tom é **frio e factual**: números e fatos, sem adjetivos como "chocante" e sem "o que a mídia esconde".
3. **Custo de infraestrutura R$ 0.** Sem APIs pagas, servidores ou bancos de dados. Só GitHub Actions + GitHub Pages.
4. **Textos do site em PT-BR** (Irã, Quênia, Vietnã; nunca a forma de Portugal: Irão, Quénia, Vietname).
5. **Blockchain (IPFS, OpenTimestamps, domínio .eth) é fase futura.** Não implementar e não prometer no site.
6. **Nunca publicar e-mail pessoal** do dono no site. O contato aponta para as issues do repositório.
7. Não fazer commit da pasta `data/` no `main` (ela vive no branch `data`).

## 3. Arquitetura

```
GitHub Actions (cron) ─► collector/ (Python) ─► data/*.json ─► site/ (Astro, build estático) ─► GitHub Pages
                              │
     fontes: USGS, GDACS, NASA EONET, CISA KEV, GDELT
```

| Pasta | Conteúdo |
|---|---|
| `collector/` | Coletor Python 3.12; única dependência externa: `httpx` |
| `collector/sources/` | Um módulo por fonte; cada um tem `parse(data)` (puro, testável) e `fetch()` |
| `collector/classify.py` | Classifica manchetes nos 4 temas |
| `collector/store.py` | Lê/grava `data/`, deduplica, arquiva |
| `collector/aggregate.py` | Calcula o "calor" por país e tema |
| `collector/geo/` | Tabela de países (ISO3, FIPS, nome PT-BR, slug) e polígonos para achar o país de uma coordenada |
| `collector/tests/` | pytest com fixtures reais em `fixtures/` |
| `tools/build_geo.py` | Regera `collector/geo/*` e `site/public/geo/*` a partir do Natural Earth (inclui tabela `PT_BR` de nomes) |
| `site/` | Astro 6 (não usar Astro 7: o Node local é 22.20 e não é suportado) |
| `site/src/lib/data.ts` | Lê `../data` no build (ou `DATA_DIR`) |
| `site/src/lib/map.ts` | Mapa SVG gerado no build com d3-geo (não usa MapLibre) |
| `.github/workflows/` | `coleta-e-deploy.yml` (coleta + build + Pages) e `testes.yml` |

## 4. Como os dados são buscados

**Eventos oficiais** (`tipo: "evento"`), mantidos por 30 dias, depois vão para `data/archive/AAAA-MM.json`:

| Fonte | Endpoint | Regras |
|---|---|---|
| USGS | `earthquake.usgs.gov/.../4.5_day.geojson` | Terremotos M4.5+. Severidade: <5.5→1, <6.5→2, <7.5→3, senão 4; alerta PAGER soma 1–3 |
| GDACS | `gdacs.org/gdacsapi/api/events/geteventlist/EVENTS4APP` | Ignora terremotos (vêm do USGS) e alertas **verdes** de queimada (WF) e seca (DR). Verde=1, laranja=3, vermelho=5 |
| NASA EONET | `eonet.gsfc.nasa.gov/api/v3/events?status=open&days=14` | Incêndio=1; tempestade/vulcão/enchente/deslizamento=2 |
| CISA KEV | `cisa.gov/.../known_exploited_vulnerabilities.json` | Últimos 30 dias. Ransomware conhecido=3, senão 2. Sem país |

**Notícias** (`tipo: "noticia"`), via arquivos GKG do GDELT publicados a cada 15 min em
`data.gdeltproject.org/gdeltv2/AAAAMMDDHHMMSS.gkg.csv.zip`:
- **Não usar a API de busca do GDELT** (`api.gdeltproject.org/api/v2/doc`): limita a 1 requisição a cada 5s e bloqueia IP.
- O feed `.translation.gkg.csv.zip` (outros idiomas) dá 404 desde 2026-11-10; o código tenta e ignora a falha.
- Ler o CSV com `quoting=csv.QUOTE_NONE` (títulos com aspas quebravam linhas).
- Cada execução processa os slots de 15 min desde `state.json → gdelt_ultimo`, no máximo `MAX_SLOTS = 8` (2h).
- `--backfill-horas N` reprocessa as últimas N horas.

**Classificação** (`collector/classify.py`):
1. **O título é obrigatório**: a notícia só entra se o título casar com as palavras-chave de um tema (`TITLE_RULES`, PT/EN/ES). Os temas do GDELT (`THEME_RULES`) sozinhos geram falsos positivos (ex.: "rochas vulcânicas" em notícia de mineração); eles só desempatam e definem o subtema.
2. `TITLE_REJECT` descarta a notícia inteira: história (Segunda Guerra, Guerra Civil americana), opinião, curiosidades.
3. `TITLE_EXCLUDE` remove usos figurados antes de casar: "guerra comercial", "trade war", "Star Wars".
4. País = país mais citado em `V2Locations` (código FIPS convertido para ISO3).

**Calor** (`collector/aggregate.py`):
`calor = nº de notícias + Σ pontos dos eventos`, com `EVENT_POINTS = {1:1, 2:3, 3:6, 4:10, 5:15}`.
Janelas `24h` e `7d`, alinhadas à hora cheia. A mesma manchete em 10 sites conta 10 vezes (mede "quanto se fala"),
mas aparece uma vez na lista. "Subindo" exige `total ≥ 20` e `anterior ≥ 10`.

## 5. Contrato de dados (`data/`)

```
data/
  state.json            {"gdelt_ultimo": ISO, "ultima_coleta": ISO, "falhas": [fonte...]}
  events.json           [Event]  eventos oficiais (30 dias)
  news.json             [Event]  notícias (72h, sem títulos repetidos, máx. 40 por país+tema)
  news_seen.json        {id: publicado_em}  ids já contados (evita contar duas vezes)
  counts/AAAA-MM-DD.json {"HH": {ISO3: {tema: n}}}  notícias por hora (35 dias)
  agg/heat_24h.json     {gerado_em, janela, temas, paises: {ISO3: {total, temas, noticias, eventos, anterior, variacao}}, ranking, subindo}
  agg/heat_7d.json      mesmo formato
  agg/serie_diaria.json {gerado_em, dias: {AAAA-MM-DD: {tema: n}}}
  archive/AAAA-MM.json  eventos com mais de 30 dias
```

`Event` (`collector/model.py`, espelhado em `site/src/lib/data.ts`):
`id, tipo, tema, subtema, titulo, fonte, fonte_url, publicado_em, atualizado_em, severidade (1–5), pais_iso, lat, lon, idioma`.
Se mudar o formato, mude os dois lados e os testes.

## 6. Comandos

```bash
# coletor (na raiz do projeto)
python3 -m venv .venv && .venv/bin/pip install httpx pytest
.venv/bin/python -m collector                       # coleta e grava em data/
.venv/bin/python -m collector --backfill-horas 48   # primeira vez
.venv/bin/python -m collector --only usgs,gdacs     # só algumas fontes
.venv/bin/python -m pytest                          # 30 testes

# site (em site/)
npm install
npx astro check     # tipos
npx astro build     # gera site/dist (funciona até sem data/)
npx astro preview --port 4321
```

Verificação mínima antes de commitar: `pytest` + `astro check` + `astro build` sem erros.

## 7. Site

- Rotas: `/` (sismograma + mapa + ranking + feed), `/tema/[slug]/`, `/pais/[slug]/` (só países com calor 7d ≥ 5), `/paises/`, `/evento/[id]/` (eventos oficiais com severidade ≥ 2), `/sobre/`, `/metodologia/`, `/privacidade/`, `/contato/`, `/rss.xml`, `/robots.txt`, sitemap.
- O site é servido numa subpasta: **todo link interno usa `u('/caminho/')`** de `site/src/config.ts`. Nunca escrever `href="/..."` direto.
- `astro.config.mjs`: `site = SITE_URL` (origem), `base = BASE_PATH` (padrão `/monitor-crise`). Com domínio próprio: `BASE_PATH=/`.
- Textos gerados a partir dos dados ficam em `site/src/lib/texts.ts` (só números e fatos).
- Variações: até +99% em porcentagem; acima disso como multiplicador (`×13,8`), em `site/src/lib/format.ts`.
- Anúncios: `AdSlot.astro` reserva a altura; o AdSense só carrega após consentimento (`Consent.astro`). Variáveis: `PUBLIC_ADSENSE_CLIENT`, `PUBLIC_AADS_UNIT`, `PUBLIC_CONTACT_EMAIL`.

**Visual ("sismograma de tambor", detalhes em `DESIGN.md`):** fundo fuligem `#121110`, traço osso `#EDE6D6`, linhas grafite,
**um único acento âmbar `#E8A33D`** (agulha "agora", picos, altas, links). Fonte Archivo variável, larguras condensadas para rótulos,
números tabulares. Sem cards (listas com filetes), sem gradientes, cantos retos, uma única animação (o traço "grava" uma vez).
Horas antes do início da coleta ficam **em branco** ("antes da coleta"), nunca desenhadas como calma.

## 8. Deploy e estado atual (2026-11-14)

- Repositório: `github.com/vitorms0597/monitor-crise` (**público**, branch `main`; o nome não tem "s", a pasta local tem: `~/develop/monitor-crises`).
- Workflow `Coleta e deploy`: cron `7,22,37,52 * * * *` + execução manual (input `backfill_horas`). Restaura `data/` do branch `data`, coleta, regrava o branch `data` como **um único commit forçado** (o repositório não cresce), gera o site e, se a variável `PUBLICAR=sim`, publica no GitHub Pages.
- Variáveis do repositório: `PUBLICAR=sim`, `SITE_URL=https://sbtechsoftware.com.br` (temporária, ver abaixo).
- **O site está publicado mas inacessível.** O repositório `vitorms0597.github.io` tem o domínio `sbtechsoftware.com.br` configurado, então o GitHub redireciona `vitorms0597.github.io/monitor-crise/` para esse domínio, que aponta para a Vercel (site da empresa SB Tech) e responde 404. **Decisão do dono: comprar um domínio próprio depois. Não mexer no repositório `vitorms0597.github.io` nem no site da SB Tech sem autorização.**
- Quando houver domínio: registros A para `185.199.108.153`, `.109.153`, `.110.153`, `.111.153`; custom domain no repositório `monitor-crise`; variáveis `SITE_URL=https://dominio` e `BASE_PATH=/`; ativar HTTPS.

## 9. Problemas conhecidos e próximos passos

1. **O GitHub está rodando o cron bem menos que a cada 15 min** (4 execuções em 24h em 13/11, com intervalos de ~5h). Como só se recuperam 2h de GDELT (`MAX_SLOTS = 8`), **notícias estão sendo perdidas**. Correção sugerida: subir `MAX_SLOTS` para 48 (12h) ou mais; o repositório é público e os minutos de Actions são ilimitados.
2. Manchetes quase todas em inglês. Ideias: RSS de veículos brasileiros (G1, Folha, Agência Brasil) e, se o orçamento permitir, tradução por IA.
3. Viés de imprensa: países com mais mídia (EUA) têm mais registros. "Calor" significa "mais falado", não "mais grave". Já explicado em `/metodologia/`.
4. A classificação por palavras-chave ainda erra; ajustes vão em `TITLE_RULES` / `TITLE_REJECT` / `TITLE_EXCLUDE`, sempre com um caso novo em `collector/tests/test_classify.py`.
5. Imagem OpenGraph para compartilhamento ainda não existe.
6. Um colaborador vai precisar de acesso de escrita (usuário do GitHub ainda não informado).
7. As actions do workflow (`checkout@v4`, `setup-node@v4`, `setup-python@v5`) avisam sobre Node 20 descontinuado; atualizar quando houver versões novas.

## 10. Decisões tomadas (não reabrir sem motivo)

- MapLibre trocado por **SVG gerado no build** (mais leve no celular, cada país é um link indexável).
- Cloudflare Pages trocado por **GitHub Pages**.
- Repositório ficou **público** para ter Pages e minutos de Actions grátis; não há segredos no código.
- Direção visual "sismograma" escolhida e registrada em `DESIGN.md`; o dono delega escolhas visuais: recomende e siga, sem menus de opções.
- O dono escreve em português; responda em português.
