"""Pontuação de "calor" por país e tema: quanto cada crise está sendo falada e acontecendo.

calor = nº de notícias no período + pontos dos eventos oficiais no período (crescem com a severidade:
um tremor M4.5 vale como 1 notícia; um alerta vermelho do GDACS, como 15).
"""
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from .model import TEMAS

EVENT_POINTS = {1: 1, 2: 3, 3: 6, 4: 10, 5: 15}
WINDOWS = {"24h": timedelta(hours=24), "7d": timedelta(days=7)}
# "subindo" exige volume mínimo nos dois períodos: 1 → 10 não é uma alta de 900% que mereça destaque
MIN_TOTAL_RISING = 20
MIN_PREVIOUS_RISING = 10


def _empty():
    return {"total": 0, "temas": dict.fromkeys(TEMAS, 0), "noticias": 0, "eventos": 0}


def _scores(store, events, start, end):
    paises = defaultdict(_empty)
    for _, iso, tema, n in store.hourly_counts(start, end):
        p = paises[iso]
        p["temas"][tema] += n
        p["total"] += n
        p["noticias"] += n
    for e in events:
        if e.pais_iso and start <= datetime.fromisoformat(e.atualizado_em) < end:
            p = paises[e.pais_iso]
            pts = EVENT_POINTS[e.severidade]
            p["temas"][e.tema] += pts
            p["total"] += pts
            p["eventos"] += 1
    return paises


def heat(store, events, window, now=None):
    now = now or datetime.now(UTC)
    span = WINDOWS[window]
    # janelas alinhadas à hora cheia, incluindo a hora corrente (as contagens são por hora)
    end = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    current = _scores(store, events, end - span, end)
    previous = _scores(store, events, end - 2 * span, end - span)
    temas = dict.fromkeys(TEMAS, 0)
    for iso, p in current.items():
        p["anterior"] = previous[iso]["total"] if iso in previous else 0
        p["variacao"] = round((p["total"] - p["anterior"]) / p["anterior"] * 100) if p["anterior"] else None
        for t, v in p["temas"].items():
            temas[t] += v
    ranking = sorted(current, key=lambda i: current[i]["total"], reverse=True)
    rising = sorted((i for i in current
                     if current[i]["total"] >= MIN_TOTAL_RISING and current[i]["anterior"] >= MIN_PREVIOUS_RISING),
                    key=lambda i: current[i]["total"] / current[i]["anterior"], reverse=True)
    return {
        "gerado_em": now.isoformat(timespec="seconds"),
        "janela": window,
        "temas": temas,
        "paises": dict(current),
        "ranking": ranking[:30],
        "subindo": rising[:10],
    }


def daily_series(store, events, days=14, now=None):
    """Totais diários por tema (notícias + eventos ponderados) para o gráfico do termômetro."""
    now = now or datetime.now(UTC)
    start = datetime(now.year, now.month, now.day, tzinfo=UTC) - timedelta(days=days - 1)
    series = {(start + timedelta(days=i)).date().isoformat(): dict.fromkeys(TEMAS, 0) for i in range(days)}
    for at, _, tema, n in store.hourly_counts(start, now + timedelta(hours=1)):
        series[at.date().isoformat()][tema] += n
    for e in events:
        day = e.atualizado_em[:10]
        if day in series and e.pais_iso:
            series[day][e.tema] += EVENT_POINTS[e.severidade]
    return {"gerado_em": now.isoformat(timespec="seconds"), "dias": series}
