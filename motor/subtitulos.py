"""Subtitulos para quemar en el video: grandes, rapidos y legibles."""

from config import Config


def palabras_en_timeline_editado(palabras: list, intervalos: list) -> list:
    """Convierte timestamps originales a timestamps del video ya cortado."""
    editadas = []
    offset = 0.0

    for ini, fin in intervalos:
        for palabra in palabras:
            p_ini = palabra["inicio"]
            p_fin = palabra["fin"]
            if p_fin <= ini or p_ini >= fin:
                continue

            editadas.append(
                {
                    "inicio": offset + max(p_ini, ini) - ini,
                    "fin": offset + min(p_fin, fin) - ini,
                    "texto": palabra["texto"].strip(),
                }
            )
        offset += fin - ini

    return [p for p in editadas if p["texto"]]


def construir_bloques(palabras: list, cfg: Config) -> list:
    """Agrupa palabras en golpes cortos para subtitulos tipo Shorts/YouTube."""
    bloques = []
    actual = []
    inicio = None
    ultimo_fin = None

    for palabra in palabras:
        texto = palabra["texto"].strip()
        if not texto:
            continue

        if not actual:
            inicio = palabra["inicio"]
            actual = [palabra]
            ultimo_fin = palabra["fin"]
            continue

        hueco = palabra["inicio"] - ultimo_fin
        textos = [p["texto"] for p in actual] + [texto]
        duracion = palabra["fin"] - inicio
        chars = len(" ".join(textos))

        if (
            len(actual) >= cfg.subtitulos_palabras_max
            or duracion > cfg.subtitulos_duracion_max
            or chars > cfg.subtitulos_chars_max
            or hueco > cfg.subtitulos_hueco_max
        ):
            bloques.append(_bloque(actual))
            inicio = palabra["inicio"]
            actual = [palabra]
        else:
            actual.append(palabra)

        ultimo_fin = palabra["fin"]

    if actual:
        bloques.append(_bloque(actual))

    return bloques


def generar_srt(palabras: list, intervalos: list, ruta_srt: str, cfg: Config) -> None:
    """Escribe un .srt en la timeline editada del video final."""
    palabras_editadas = palabras_en_timeline_editado(palabras, intervalos)
    bloques = construir_bloques(palabras_editadas, cfg)

    with open(ruta_srt, "w", encoding="utf-8") as f:
        for i, bloque in enumerate(bloques, start=1):
            f.write(f"{i}\n")
            f.write(f"{_srt_time(bloque['inicio'])} --> {_srt_time(bloque['fin'])}\n")
            f.write(f"{_texto_srt(bloque['palabras'])}\n\n")


def _bloque(palabras: list) -> dict:
    return {
        "inicio": palabras[0]["inicio"],
        "fin": max(palabras[-1]["fin"], palabras[0]["inicio"] + 0.28),
        "palabras": [p["texto"] for p in palabras],
    }


def _texto_srt(palabras: list) -> str:
    return " ".join(p.strip().upper() for p in palabras if p.strip())


def _srt_time(segundos: float) -> str:
    ms_total = int(round(max(0.0, segundos) * 1000))
    h, resto = divmod(ms_total, 3600000)
    m, resto = divmod(resto, 60000)
    s, ms = divmod(resto, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
