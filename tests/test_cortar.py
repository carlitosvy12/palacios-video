"""Tests de la logica de corte. No necesitan video ni dependencias pesadas:
solo Python. Corre con:  python -m pytest   o   python tests/test_cortar.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config
from motor import cortar


def _palabras():
    # hola que [silencio 2s] tal eh(muletilla) [silencio 0.8s] bien
    return [
        {"inicio": 0.0, "fin": 0.5, "texto": "hola"},
        {"inicio": 0.6, "fin": 1.0, "texto": "que"},
        {"inicio": 3.0, "fin": 3.5, "texto": "tal"},
        {"inicio": 3.6, "fin": 4.0, "texto": "eh"},
        {"inicio": 4.8, "fin": 5.2, "texto": "bien"},
    ]


def test_filtra_muletillas():
    cfg = Config()
    utiles = cortar.filtrar_muletillas(_palabras(), cfg.muletillas)
    textos = [p["texto"] for p in utiles]
    assert "eh" not in textos
    assert len(utiles) == 4


def test_corta_silencios_largos():
    cfg = Config(silencio_max=0.6, padding=0.12)
    intervalos = cortar.construir_intervalos(_palabras(), cfg)
    # esperamos 3 segmentos: "hola que" | "tal" | "bien"
    assert len(intervalos) == 3


def test_conserva_silencios_cortos():
    cfg = Config(silencio_max=0.6, padding=0.0)
    intervalos = cortar.construir_intervalos(_palabras(), cfg)
    # el hueco hola->que es 0.1s, no debe partirse: primer segmento llega a 1.0
    assert abs(intervalos[0][1] - 1.0) < 0.01


def test_padding_no_baja_de_cero():
    cfg = Config(padding=5.0)
    intervalos = cortar.construir_intervalos(_palabras(), cfg)
    assert intervalos[0][0] == 0.0


def test_duracion_total():
    cfg = Config(silencio_max=0.6, padding=0.0)
    intervalos = cortar.construir_intervalos(_palabras(), cfg)
    # (1.0-0.0) + (3.5-3.0) + (5.2-4.8) = 1.9
    assert abs(cortar.duracion_total(intervalos) - 1.9) < 0.01


def test_sin_palabras():
    assert cortar.construir_intervalos([], Config()) == []


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
