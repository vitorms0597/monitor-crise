from datetime import UTC, datetime

from collector.sources import cisa_kev, eonet, gdacs, gdelt, usgs


def test_usgs_traduz_titulo_e_acha_pais(fixture):
    events = {e.id: e for e in usgs.parse(fixture("usgs.json"))}
    jp = events["usgs:us7000tx9i"]
    assert jp.titulo == "Terremoto de magnitude 4,7 a 90 km de Tateyama, Japão"
    assert jp.pais_iso == "JPN" and jp.tema == "desastre" and jp.subtema == "terremoto"
    assert events["usgs:us7000tx9z"].pais_iso == "IDN"
    assert events["usgs:us7000tx9n"].pais_iso is None  # dorsal no meio do Atlântico


def test_usgs_severidade_cresce_com_magnitude_e_alerta():
    assert usgs.severity(4.6) == 1
    assert usgs.severity(6.0) == 2
    assert usgs.severity(7.1, "red") == 5


def test_gdacs_ignora_terremoto_e_queimada_verde(fixture):
    events = {e.id: e for e in gdacs.parse(fixture("gdacs.json"))}
    assert "gdacs:EQ:1576577" not in events  # terremotos vêm do USGS
    assert "gdacs:WF:1033686" not in events  # alerta verde de queimada é ruído
    fl = events["gdacs:FL:1104276"]
    assert fl.titulo == "Enchente — Portugal" and fl.pais_iso == "PRT" and fl.subtema == "enchente"
    assert events["gdacs:TC:1001348"].subtema == "ciclone"


def test_eonet_pula_categorias_fora_do_escopo(fixture):
    events = {e.id: e for e in eonet.parse(fixture("eonet.json"))}
    assert "eonet:EONET_2736" not in events  # gelo marinho
    fire = events["eonet:EONET_26258"]
    assert fire.subtema == "incendio" and fire.pais_iso == "USA"


def test_cisa_so_vulnerabilidades_recentes(fixture):
    now = datetime(2026, 11, 10, tzinfo=UTC)
    events = cisa_kev.parse(fixture("cisa_kev.json"), now=now)
    assert {e.id for e in events} == {"kev:CVE-2026-102895", "kev:CVE-2026-123158"}
    assert all(e.tema == "ciber" and e.pais_iso is None for e in events)


def test_gdelt_classifica_e_localiza_noticias(fixture):
    events = gdelt.parse_gkg(fixture("sample.gkg.csv"))

    def find(prefix):
        return next(e for e in events if e.titulo.startswith(prefix))

    cyber = find("France accuses Iran")
    assert (cyber.tema, cyber.tipo, cyber.idioma) == ("ciber", "noticia", "en")
    assert find("Airstrikes hit gas facility").pais_iso == "YEM"  # Arábia Saudita também é citada
    assert find("Colorado communities").subtema == "enchente"
    # falsos positivos que os temas do GDELT sozinhos deixariam passar
    assert not any(e.titulo.startswith(("Religious Freedom", "Total Metals", "Working for")) for e in events)
    assert len(events) == 3


def test_gdelt_slots_recupera_atraso_limitado():
    latest = datetime(2026, 11, 10, 10, 15, tzinfo=UTC)
    assert len(gdelt.slots_to_fetch(None, latest)) == 4
    assert gdelt.slots_to_fetch(datetime(2026, 11, 10, 9, 45, tzinfo=UTC), latest) == [
        datetime(2026, 11, 10, 10, 0, tzinfo=UTC), latest]
    assert len(gdelt.slots_to_fetch(datetime(2026, 11, 9, tzinfo=UTC), latest)) == gdelt.MAX_SLOTS
    assert gdelt.slots_to_fetch(latest, latest) == []
