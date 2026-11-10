"""Roda uma coleta: python -m collector [--data-dir data] [--only usgs,gdelt]"""
import argparse
import sys
import time
from datetime import UTC, datetime

from . import aggregate
from .sources import cisa_kev, eonet, gdacs, gdelt, usgs
from .store import Store

OFFICIAL = {"usgs": usgs, "gdacs": gdacs, "eonet": eonet, "cisa": cisa_kev}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--only", help="fontes separadas por vírgula (padrão: todas)")
    ap.add_argument("--backfill-horas", type=int, help="reprocessa as últimas N horas do GDELT")
    args = ap.parse_args(argv)
    only = set(args.only.split(",")) if args.only else None
    store = Store(args.data_dir)
    state = store.state()
    now = datetime.now(UTC)
    ok, failed = 0, []

    official = []
    for name, mod in OFFICIAL.items():
        if only and name not in only:
            continue
        t = time.monotonic()
        try:
            items = mod.fetch()
            official += items
            ok += 1
            print(f"{name}: {len(items)} eventos ({time.monotonic() - t:.1f}s)")
        except Exception as e:
            failed.append(name)
            print(f"{name}: FALHOU — {e}", file=sys.stderr)
    events = store.merge_events(official, now)

    if not only or "gdelt" in only:
        t = time.monotonic()
        try:
            last = state.get("gdelt_ultimo")
            news, done = gdelt.fetch(datetime.fromisoformat(last) if last else None,
                                     log=lambda m: print(m, file=sys.stderr), backfill_hours=args.backfill_horas)
            kept, fresh = store.merge_news(news, now)
            if done:
                state["gdelt_ultimo"] = done.isoformat()
            ok += 1
            print(f"gdelt: {fresh} notícias novas, {len(kept)} guardadas ({time.monotonic() - t:.1f}s)")
        except Exception as e:
            failed.append("gdelt")
            print(f"gdelt: FALHOU — {e}", file=sys.stderr)

    for window in aggregate.WINDOWS:
        store.write_agg(f"heat_{window}", aggregate.heat(store, events, window, now))
    store.write_agg("serie_diaria", aggregate.daily_series(store, events, now=now))
    store.prune_counts(now)
    state["ultima_coleta"] = now.isoformat(timespec="seconds")
    state["falhas"] = failed
    store.save_state(state)
    print(f"ok: {ok} fontes, falhas: {failed or 'nenhuma'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
