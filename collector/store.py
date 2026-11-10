"""Persistência em arquivos JSON dentro de data/ (o site lê os mesmos arquivos no build)."""
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .classify import normalize
from .model import Event

EVENTS_DAYS = 30
NEWS_HOURS = 72
NEWS_PER_COUNTRY_TOPIC = 40
COUNTS_DAYS = 35


def _read(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    tmp.replace(path)


def _dt(s):
    return datetime.fromisoformat(s)


class Store:
    def __init__(self, root):
        self.root = Path(root)

    # --- estado da coleta ---
    def state(self):
        return _read(self.root / "state.json", {})

    def save_state(self, state):
        _write(self.root / "state.json", state)

    # --- eventos oficiais (USGS, GDACS, EONET, CISA) ---
    def events(self):
        return [Event.from_dict(d) for d in _read(self.root / "events.json", [])]

    def merge_events(self, new, now=None):
        now = now or datetime.now(UTC)
        by_id = {e.id: e for e in self.events()}
        by_id.update({e.id: e for e in new})
        cutoff = now - timedelta(days=EVENTS_DAYS)
        keep, old = [], defaultdict(list)
        for e in by_id.values():
            (keep if _dt(e.atualizado_em) >= cutoff else old[e.atualizado_em[:7]]).append(e)
        for month, items in old.items():
            path = self.root / "archive" / f"{month}.json"
            archived = {d["id"]: d for d in _read(path, [])}
            archived.update({e.id: e.to_dict() for e in items})
            _write(path, list(archived.values()))
        keep.sort(key=lambda e: e.atualizado_em, reverse=True)
        _write(self.root / "events.json", [e.to_dict() for e in keep])
        return keep

    # --- notícias (GDELT) ---
    def news(self):
        return [Event.from_dict(d) for d in _read(self.root / "news.json", [])]

    def merge_news(self, new, now=None):
        """Guarda as notícias recentes (sem títulos repetidos) e soma TODAS as novas nas contagens."""
        now = now or datetime.now(UTC)
        current = self.news()
        cutoff = now - timedelta(hours=NEWS_HOURS)
        # ids já contados (inclusive os que saíram da lista por título repetido)
        seen_path = self.root / "news_seen.json"
        seen = {i: t for i, t in _read(seen_path, {}).items() if _dt(t) >= cutoff}
        fresh = []
        for e in new:
            if e.id not in seen:
                seen[e.id] = e.publicado_em
                fresh.append(e)
        self._add_counts(fresh)
        _write(seen_path, seen)

        items = sorted(current + fresh, key=lambda e: e.publicado_em, reverse=True)
        seen_titles, per_bucket, keep = set(), Counter(), []
        for e in items:
            title = normalize(e.titulo)
            bucket = (e.pais_iso, e.tema)
            if _dt(e.publicado_em) < cutoff or title in seen_titles or per_bucket[bucket] >= NEWS_PER_COUNTRY_TOPIC:
                continue
            seen_titles.add(title)
            per_bucket[bucket] += 1
            keep.append(e)
        _write(self.root / "news.json", [e.to_dict() for e in keep])
        return keep, len(fresh)

    # --- contagens horárias de notícias por país e tema: counts/AAAA-MM-DD.json -> {"HH": {ISO: {tema: n}}} ---
    def _add_counts(self, events):
        by_day = defaultdict(list)
        for e in events:
            by_day[e.publicado_em[:10]].append(e)
        for day, items in by_day.items():
            path = self.root / "counts" / f"{day}.json"
            data = _read(path, {})
            for e in items:
                hour = data.setdefault(e.publicado_em[11:13], {})
                country = hour.setdefault(e.pais_iso, {})
                country[e.tema] = country.get(e.tema, 0) + 1
            _write(path, data)

    def hourly_counts(self, start, end):
        """Itera (datetime da hora, iso3, tema, n) com start <= hora < end."""
        day = start.date()
        while day <= end.date():
            for hh, countries in _read(self.root / "counts" / f"{day.isoformat()}.json", {}).items():
                at = datetime(day.year, day.month, day.day, int(hh), tzinfo=UTC)
                if start <= at < end:
                    for iso, temas in countries.items():
                        for tema, n in temas.items():
                            yield at, iso, tema, n
            day += timedelta(days=1)

    def prune_counts(self, now=None):
        now = now or datetime.now(UTC)
        cutoff = (now - timedelta(days=COUNTS_DAYS)).date().isoformat()
        for path in (self.root / "counts").glob("*.json"):
            if path.stem < cutoff:
                path.unlink()

    def write_agg(self, name, data):
        _write(self.root / "agg" / f"{name}.json", data)
