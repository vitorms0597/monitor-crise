from datetime import UTC, datetime, timedelta

from collector import aggregate
from collector.model import Event
from collector.store import Store

NOW = datetime(2026, 11, 10, 12, tzinfo=UTC)


def news(i, iso="BRA", tema="energia", hours_ago=1, title=None):
    when = (NOW - timedelta(hours=hours_ago)).isoformat()
    return Event(id=f"n{i}", tipo="noticia", tema=tema, subtema="x", titulo=title or f"Notícia {i}",
                 fonte="x", fonte_url=f"https://x/{i}", publicado_em=when, atualizado_em=when,
                 severidade=1, pais_iso=iso)


def event(i, iso, sev, days_ago=0):
    when = (NOW - timedelta(days=days_ago)).isoformat()
    return Event(id=f"e{i}", tipo="evento", tema="desastre", subtema="terremoto", titulo="T",
                 fonte="USGS", fonte_url="u", publicado_em=when, atualizado_em=when, severidade=sev,
                 pais_iso=iso)


def test_noticias_contam_uma_vez_e_titulos_repetidos_somem_da_lista(tmp_path):
    store = Store(tmp_path)
    batch = [news(1), news(2, title="Notícia 1"), news(3)]
    kept, fresh = store.merge_news(batch, NOW)
    assert fresh == 3 and len(kept) == 2  # mesma manchete em 2 sites: conta 2x, lista 1x
    _, fresh = store.merge_news(batch, NOW)
    assert fresh == 0  # reprocessar o mesmo arquivo não infla as contagens
    total = sum(n for *_, n in store.hourly_counts(NOW - timedelta(days=1), NOW))
    assert total == 3


def test_eventos_antigos_vao_para_o_arquivo(tmp_path):
    store = Store(tmp_path)
    keep = store.merge_events([event(1, "CHL", 1), event(2, "CHL", 1, days_ago=40)], NOW)
    assert [e.id for e in keep] == ["e1"]
    assert list((tmp_path / "archive").glob("*.json"))


def test_calor_soma_noticias_e_eventos_e_calcula_variacao(tmp_path):
    store = Store(tmp_path)
    store.merge_news([news(i, hours_ago=2) for i in range(10)] +
                     [news(100 + i, hours_ago=30) for i in range(5)], NOW)
    events = [event(1, "BRA", 3), event(2, "CHL", 5)]
    h = aggregate.heat(store, events, "24h", NOW)
    bra = h["paises"]["BRA"]
    assert bra["temas"]["energia"] == 10 and bra["temas"]["desastre"] == aggregate.EVENT_POINTS[3]
    assert bra["anterior"] == 5 and bra["variacao"] == round((16 - 5) / 5 * 100)
    assert h["ranking"][0] == "BRA" and "BRA" in h["subindo"]
    assert h["paises"]["CHL"]["total"] == aggregate.EVENT_POINTS[5]
