from dataclasses import asdict, dataclass

TEMAS = ("ciber", "conflito", "energia", "desastre")


@dataclass
class Event:
    id: str
    tipo: str  # "evento" (fonte oficial) | "noticia" (cobertura da imprensa via GDELT)
    tema: str  # um de TEMAS
    subtema: str
    titulo: str
    fonte: str
    fonte_url: str
    publicado_em: str  # ISO 8601 UTC
    atualizado_em: str  # ISO 8601 UTC; usado nas janelas de calor
    severidade: int  # 1 (baixa) a 5 (extrema)
    pais_iso: str | None = None
    lat: float | None = None
    lon: float | None = None
    idioma: str = "en"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)
