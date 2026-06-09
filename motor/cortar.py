"""Logica de corte: silencios + muletillas -> intervalos a conservar.

IMPORTANTE: este modulo es LOGICA PURA. No transcribe ni renderiza, solo
calcula. Asi se puede testear sin necesidad de un video real (ver
tests/test_cortar.py). Mantenlo asi: los efectos (IO, ffmpeg, red) van en
otros modulos.
"""

from config import Config


def _limpiar(texto: str) -> str:
    """Normaliza una palabra para comparar con la lista de muletillas."""
    return texto.strip().lower().strip(".,;:!?¿¡")


def filtrar_muletillas(palabras: list, muletillas: set) -> list:
    """Devuelve las palabras que NO son muletillas."""
    return [p for p in palabras if _limpiar(p["texto"]) not in muletillas]


def construir_intervalos(palabras: list, cfg: Config) -> list:
    """Construye la lista de intervalos (inicio, fin) en segundos a CONSERVAR.

    Logica:
      1. Quitamos muletillas (eliminamos su tramo temporal).
      2. Recorremos las palabras restantes. Si el hueco entre una palabra y la
         siguiente supera cfg.silencio_max, cerramos el segmento actual y
         abrimos otro. Los silencios cortos se conservan: son lo que hace que
         el video no suene robotico.
      3. Aplicamos padding a cada corte y fusionamos intervalos solapados.
    """
    utiles = filtrar_muletillas(palabras, cfg.muletillas)
    if not utiles:
        return []

    intervalos = []
    ini = utiles[0]["inicio"]
    fin = utiles[0]["fin"]

    for prev, sig in zip(utiles, utiles[1:]):
        hueco = sig["inicio"] - prev["fin"]
        if hueco > cfg.silencio_max:
            intervalos.append((max(0.0, ini - cfg.padding), fin + cfg.padding))
            ini = sig["inicio"]
        fin = sig["fin"]
    intervalos.append((max(0.0, ini - cfg.padding), fin + cfg.padding))

    return _fusionar(intervalos)


def _fusionar(intervalos: list) -> list:
    """Une intervalos que se solapen o toquen tras aplicar el padding."""
    if not intervalos:
        return []
    fusionados = [intervalos[0]]
    for s, e in intervalos[1:]:
        ult_s, ult_e = fusionados[-1]
        if s <= ult_e:
            fusionados[-1] = (ult_s, max(ult_e, e))
        else:
            fusionados.append((s, e))
    return fusionados


def duracion_total(intervalos: list) -> float:
    """Suma de la duracion de los intervalos (= duracion del video editado)."""
    return sum(e - s for s, e in intervalos)
