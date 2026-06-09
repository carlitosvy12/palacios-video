import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config
from motor import subtitulos


def test_palabras_en_timeline_editado_recalcula_offsets():
    palabras = [
        {"inicio": 0.5, "fin": 1.0, "texto": "hola"},
        {"inicio": 3.0, "fin": 3.4, "texto": "mundo"},
    ]
    intervalos = [(0.0, 1.5), (2.5, 4.0)]

    editadas = subtitulos.palabras_en_timeline_editado(palabras, intervalos)

    assert editadas[0]["inicio"] == 0.5
    assert editadas[1]["inicio"] == 2.0


def test_construir_bloques_limita_palabras():
    cfg = Config(subtitulos_palabras_max=2)
    palabras = [
        {"inicio": 0.0, "fin": 0.2, "texto": "uno"},
        {"inicio": 0.2, "fin": 0.4, "texto": "dos"},
        {"inicio": 0.4, "fin": 0.6, "texto": "tres"},
    ]

    bloques = subtitulos.construir_bloques(palabras, cfg)

    assert len(bloques) == 2
    assert bloques[0]["palabras"] == ["uno", "dos"]


def test_texto_srt_en_mayusculas():
    texto = subtitulos._texto_srt(["hola", "mundo"])

    assert texto == "HOLA MUNDO"


def test_srt_time_usa_milisegundos():
    assert subtitulos._srt_time(65.4321) == "00:01:05,432"


if __name__ == "__main__":
    fallos = 0
    for nombre, fn in sorted(globals().items()):
        if nombre.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  OK  {nombre}")
            except AssertionError as e:
                fallos += 1
                print(f"  FALLO  {nombre}: {e}")
    print(f"\n{'TODOS OK' if not fallos else f'{fallos} FALLOS'}")
    sys.exit(1 if fallos else 0)
