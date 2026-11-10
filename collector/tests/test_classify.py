import pytest

from collector.classify import classify, theme_counts


@pytest.mark.parametrize("title,expected", [
    ("Apagão deixa Lisboa sem energia por 6 horas", ("energia", "apagao")),
    ("Massive power outage hits Santiago", ("energia", "apagao")),
    ("Hospital sofre ataque de ransomware em SP", ("ciber", "ransomware")),
    ("Vazamento de dados expõe 2 milhões de clientes", ("ciber", "vazamento")),
    ("Rússia lança mísseis contra Kiev", ("conflito", "guerra")),
    ("Atentado em mercado deixa 12 mortos", ("conflito", "terrorismo")),
    ("Terremoto de magnitude 6 atinge o Chile", ("desastre", "terremoto")),
    ("Chuvas fortes causam enchente no RS", ("desastre", "enchente")),
    ("Huracán Mateo toca tierra en Cuba", ("desastre", "ciclone")),
])
def test_titulos(title, expected):
    assert classify(title, theme_counts("")) == expected


@pytest.mark.parametrize("title", [
    "Trade war between US and China escalates",
    "Guerra comercial derruba bolsas",
    "Box office: Star Wars returns",
    "Mumbai: Bombay High Court refuses permission",
    "Quarterly earnings beat expectations",
    "Women Shaped American Agriculture During the Civil War",
    "Russian volcano plays peek-a-boo with an astronaut",
    "Guest opinion: wildfire season is getting longer",
    "Lembrando os 80 anos do fim da Segunda Guerra",
])
def test_usos_figurados_e_irrelevantes(title):
    assert classify(title, theme_counts("ARMEDCONFLICT,1;ARMEDCONFLICT,9")) is None


def test_temas_do_gdelt_desempatam():
    # título fala de guerra e de ataque hacker; os temas do texto dizem que é sobre ciber
    themes = theme_counts(";".join(f"CYBER_ATTACK,{i}" for i in range(5)))
    assert classify("Hackers linked to war in Ukraine hit power grid", themes)[0] == "ciber"
