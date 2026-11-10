"""Classifica notícias nos 4 temas usando os temas do GDELT + palavras-chave do título (PT/EN/ES)."""
import re
import unicodedata
from collections import Counter

# (regex sobre o código de tema do GDELT, tema, subtema, peso por menção)
THEME_RULES = [
    (r"CYBER_ATTACK|TAX_FNCACT_HACKERS?$", "ciber", "ataque", 2),
    (r"WB_2457_CYBER|CYBER", "ciber", "ataque", 1),
    (r"POWER_OUTAGE|WITHOUT_POWER|BLACKOUT", "energia", "apagao", 2),
    (r"ARMEDCONFLICT|WB_2468_CONVENTIONAL_WAR|WB_2462_POLITICAL_VIOLENCE_AND_WAR|WB_2510_WAR_CRIMES",
     "conflito", "guerra", 1),
    (r"^TERROR$|WB_2467_TERRORISM|SUICIDE_ATTACK", "conflito", "terrorismo", 1),
    (r"TAX_WEAPONS_(MISSILE|ROCKET|BOMB|DRONE|ARTILLERY)", "conflito", "guerra", 1),
    (r"NATURAL_DISASTER_(EARTHQUAKE|TREMOR|AFTERSHOCK)", "desastre", "terremoto", 1),
    (r"NATURAL_DISASTER_(FLOOD|FLASH_FLOOD|MONSOON)", "desastre", "enchente", 1),
    (r"NATURAL_DISASTER_(HURRICANE|TYPHOON|CYCLONE|TROPICAL_STORM|TORNADO)", "desastre", "ciclone", 1),
    (r"NATURAL_DISASTER_(WILDFIRE|BUSHFIRE|FOREST_FIRE)", "desastre", "incendio", 1),
    (r"NATURAL_DISASTER_(VOLCAN|ERUPT|LAVA)", "desastre", "vulcao", 1),
    (r"NATURAL_DISASTER_TSUNAMI", "desastre", "tsunami", 1),
    (r"NATURAL_DISASTER_(LANDSLIDE|MUDSLIDE)", "desastre", "deslizamento", 1),
]
THEME_RULES = [(re.compile(p), t, s, w) for p, t, s, w in THEME_RULES]

# Palavras no título (sem acento, minúsculas). Peso alto: o título diz do que a notícia trata.
TITLE_RULES = [
    (r"ransomware", "ciber", "ransomware"),
    (r"vazamento de dados|data breach|data leak|filtracion de datos", "ciber", "vazamento"),
    (r"ciberataque|ataque (hacker|cibernetico)|cyber ?attack|hackers?\b|hackead|ddos|malware|ciberseguridad",
     "ciber", "ataque"),
    (r"apagao|apagon|blackout|power (outage|cut)|sem (energia|luz)|falta de (energia|luz)|"
     r"corte de (energia|luz)|without power|cortes? de electricidad", "energia", "apagao"),
    (r"atentado|terroris|suicide bomb", "conflito", "terrorismo"),
    (r"\bguerra\b|\bwar\b|airstrike|air strike|bombardeio|bombardeo|\bmisseis?\b|\bmissil\b|missiles?\b|"
     r"drone (strike|attack)|ataque com drones?|ofensiva|invasion|invasao|cessar-fogo|ceasefire|"
     r"\btropas\b|\btroops\b|shelling|\bbomb(s|ing|ings)?\b|\bbombas?\b|explos(ion|ao|oes|ions)|gunmen|"
     r"\bmilitants?\b|\brebe(ls?|ldes?)\b|insurgen|conflito armado|armed conflict|\bmilitias?\b|milicia",
     "conflito", "guerra"),
    (r"terremoto|earthquake|\bsismo\b|tremor de terra", "desastre", "terremoto"),
    (r"enchente|inundac|\bflood|chuvas? fortes|temporal", "desastre", "enchente"),
    (r"furacao|huracan|hurricane|tufao|typhoon|ciclone|cyclone|tornado", "desastre", "ciclone"),
    (r"incendio florestal|queimada|wildfire|bushfire|incendio forestal", "desastre", "incendio"),
    (r"erupcao|erupcion|eruption|vulcao|volcan|volcano", "desastre", "vulcao"),
    (r"tsunami", "desastre", "tsunami"),
    (r"deslizamento|landslide|mudslide|deslave", "desastre", "deslizamento"),
]
TITLE_RULES = [(re.compile(p), t, s) for p, t, s in TITLE_RULES]
# Usos figurados que não são crise de verdade.
TITLE_EXCLUDE = re.compile(r"(trade|price|culture|tariff|bidding|talent|console|streaming) wars?|war of words|"
                           r"guerra (comercial|fiscal|de precos|cultural|tarifaria)|star wars|"
                           r"(blackout|apagao) (dates?|period|window)|tornado cash|hackathon")
TITLE_WEIGHT = 4
MAX_MENTIONS = 5  # um tema citado 50 vezes não deve valer 50 vezes mais


def normalize(text):
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    return text.lower()


def theme_counts(v2themes):
    """'ARMEDCONFLICT,123;KILL,456' -> Counter({'ARMEDCONFLICT': 1, 'KILL': 1})"""
    return Counter(item.split(",")[0] for item in (v2themes or "").split(";") if item)


def classify(title, themes):
    """Devolve (tema, subtema) ou None se a notícia não trata de nenhum dos temas.

    O título é obrigatório: os temas do GDELT sozinhos pegam muito ruído (ex.: "rochas
    vulcânicas" em notícia de mineração). Eles só desempatam e refinam o subtema.
    """
    score, sub = Counter(), {}
    norm = normalize(title)
    if TITLE_EXCLUDE.search(norm):
        norm = TITLE_EXCLUDE.sub(" ", norm)
    for rx, tema, subtema in TITLE_RULES:
        if rx.search(norm):
            score[tema] += TITLE_WEIGHT
            sub.setdefault(tema, Counter())[subtema] += TITLE_WEIGHT
    if not score:
        return None
    for code, n in themes.items():
        for rx, tema, subtema, w in THEME_RULES:
            if rx.search(code) and tema in score:
                pts = min(n, MAX_MENTIONS) * w
                score[tema] += pts
                sub.setdefault(tema, Counter())[subtema] += pts
                break
    tema = score.most_common(1)[0][0]
    return tema, sub[tema].most_common(1)[0][0]
