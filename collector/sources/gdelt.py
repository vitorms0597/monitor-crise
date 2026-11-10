"""Cobertura da imprensa mundial via arquivos GKG do GDELT (publicados a cada 15 min).

Cada notícia vira um Event tipo "noticia", com país = país mais citado no texto.
Não usamos a API de busca do GDELT: ela limita a 1 requisição a cada 5s e bloqueia IPs.
"""
import csv
import hashlib
import html
import io
import re
import sys
import zipfile
from collections import Counter
from datetime import UTC, datetime, timedelta

from .. import geo, http
from ..classify import classify, theme_counts
from ..model import Event

BASE = "https://data.gdeltproject.org/gdeltv2/"
LASTUPDATE = BASE + "lastupdate.txt"
SLOT = timedelta(minutes=15)
MAX_SLOTS = 8  # se o cron atrasar, recupera até 2h de arquivos
FEEDS = (("", "en"), (".translation", None))  # (sufixo do arquivo, idioma padrão)
LANGS = {"por": "pt", "spa": "es", "fra": "fr", "deu": "de", "ita": "it", "rus": "ru", "ukr": "uk",
         "ara": "ar", "zho": "zh", "jpn": "ja", "heb": "he", "tur": "tr", "fas": "fa"}
TITLE_RX = re.compile(r"<PAGE_TITLE>(.*?)</PAGE_TITLE>", re.S)
LANG_RX = re.compile(r"srclc:(\w+)")

# Colunas do GKG 2.1
DATE, SOURCE, URL, V2THEMES, V2LOCATIONS, TRANSLATION, EXTRAS = 1, 3, 4, 8, 10, 25, 26

csv.field_size_limit(sys.maxsize)


def _ts(dt):
    return dt.strftime("%Y%m%d%H%M%S")


def latest_slot():
    text = http.get(LASTUPDATE, timeout=30).text
    m = re.search(r"/(\d{14})\.gkg\.csv\.zip", text)
    return datetime.strptime(m.group(1), "%Y%m%d%H%M%S").replace(tzinfo=UTC)


def slots_to_fetch(last_done, latest, max_slots=MAX_SLOTS):
    """Slots de 15 min ainda não processados, do mais antigo ao mais novo."""
    start = last_done + SLOT if last_done else latest - SLOT * 3
    start = max(start, latest - SLOT * (max_slots - 1))
    out = []
    while start <= latest:
        out.append(start)
        start += SLOT
    return out


def _main_location(v2locations):
    """(fips do país mais citado, lat, lon do lugar mais específico nesse país)"""
    locs = []
    for item in (v2locations or "").split(";"):
        parts = item.split("#")
        if len(parts) >= 7 and parts[2]:
            locs.append(parts)
    if not locs:
        return None, None, None
    fips = Counter(p[2] for p in locs).most_common(1)[0][0]
    # tipo 1 = país inteiro; 2/5 = estado/província; 3/4 = cidade
    specific = [p for p in locs if p[2] == fips and p[0] != "1" and p[5] and p[6]]
    if not specific:
        return fips, None, None
    best = Counter((p[5], p[6]) for p in specific).most_common(1)[0][0]
    return fips, float(best[0]), float(best[1])


def parse_gkg(text, default_lang="en"):
    out = []
    for row in csv.reader(io.StringIO(text), delimiter="\t", quoting=csv.QUOTE_NONE):
        if len(row) <= EXTRAS:
            continue
        m = TITLE_RX.search(row[EXTRAS])
        title = html.unescape(m.group(1)).strip() if m else ""
        url = row[URL]
        if not title or not url.startswith("http"):
            continue
        kind = classify(title, theme_counts(row[V2THEMES]))
        if not kind:
            continue
        fips, lat, lon = _main_location(row[V2LOCATIONS])
        iso = geo.from_fips(fips) if fips else None
        if not iso:
            continue
        lang = LANG_RX.search(row[TRANSLATION])
        when = datetime.strptime(row[DATE], "%Y%m%d%H%M%S").replace(tzinfo=UTC).isoformat()
        out.append(Event(
            id="gdelt:" + hashlib.sha1(url.encode()).hexdigest()[:16],
            tipo="noticia",
            tema=kind[0],
            subtema=kind[1],
            titulo=title[:300],
            fonte=row[SOURCE],
            fonte_url=url,
            publicado_em=when,
            atualizado_em=when,
            severidade=1,
            pais_iso=iso,
            lat=lat,
            lon=lon,
            idioma=LANGS.get(lang.group(1), lang.group(1)) if lang else default_lang,
        ))
    return out


def _download(url):
    data = http.get(url, timeout=180, retries=2).content
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        return z.read(z.namelist()[0]).decode("utf-8", errors="replace")


def fetch(last_done=None, log=print, backfill_hours=None):
    """Devolve (eventos, último slot processado). backfill_hours reprocessa as últimas N horas."""
    latest = latest_slot()
    max_slots = MAX_SLOTS
    if backfill_hours:
        max_slots = backfill_hours * 4
        last_done = latest - SLOT * max_slots
    events, done = [], last_done
    for slot in slots_to_fetch(last_done, latest, max_slots):
        for suffix, lang in FEEDS:
            url = f"{BASE}{_ts(slot)}{suffix}.gkg.csv.zip"
            try:
                events += parse_gkg(_download(url), lang or "en")
            except Exception as e:  # feed traduzido às vezes não sai; não pode derrubar a coleta
                log(f"  gdelt: falhou {url.rsplit('/', 1)[-1]}: {type(e).__name__}")
        done = slot
    return events, done
