"""Pipeline reutilizable para CLI e interfaz grafica."""

from pathlib import Path

from config import Config
from motor import cortar, render
from motor.subtitulos import generar_srt
from motor.transcribir import transcribir


def editar_video(
    ruta_video: str,
    cfg: Config,
    usar_llm: bool = True,
    progreso=None,
) -> dict:
    """Ejecuta el pipeline completo y devuelve rutas, estadisticas y metadata."""
    entrada = Path(ruta_video)
    if not entrada.exists():
        raise FileNotFoundError(f"No existe el archivo: {entrada}")

    _progreso(progreso, 0.05, "Transcribiendo el video...")
    datos = transcribir(str(entrada), cfg)

    _progreso(progreso, 0.35, "Calculando cortes...")
    intervalos = cortar.construir_intervalos(datos["palabras"], cfg)
    if not intervalos:
        raise RuntimeError("No se detecto habla utilizable.")

    dur_orig = datos["duracion"]
    dur_final = cortar.duracion_total(intervalos)
    ahorro = (1 - dur_final / dur_orig) * 100 if dur_orig else 0

    narrativa = {}
    if usar_llm:
        _progreso(progreso, 0.45, "Generando metadata de YouTube...")
        from motor.narrativa import analizar_narrativa

        narrativa = analizar_narrativa(datos["segmentos"], cfg)

    ruta_subtitulos = None
    if cfg.subtitulos:
        _progreso(progreso, 0.60, "Generando subtitulos...")
        ruta_subtitulos = entrada.with_name(f"{entrada.stem}_subtitulos.srt")
        generar_srt(datos["palabras"], intervalos, str(ruta_subtitulos), cfg)

    _progreso(progreso, 0.75, "Renderizando y normalizando audio...")
    salida = entrada.with_name(f"{entrada.stem}_editado.mp4")
    render.renderizar(
        str(entrada),
        intervalos,
        str(salida),
        str(ruta_subtitulos) if ruta_subtitulos else None,
        cfg,
    )

    ruta_youtube = None
    capitulos = ""
    if narrativa and "error" not in narrativa:
        _progreso(progreso, 0.95, "Guardando metadata de YouTube...")
        ruta_youtube = entrada.with_name(f"{entrada.stem}_youtube.txt")
        capitulos = render.formato_capitulos_youtube(narrativa.get("capitulos", []))
        contenido = (
            f"TITULO:\n{narrativa.get('titulo', '')}\n\n"
            f"DESCRIPCION:\n{narrativa.get('descripcion', '')}\n\n"
            f"CAPITULOS:\n{capitulos}\n"
        )
        ruta_youtube.write_text(contenido, encoding="utf-8")

    _progreso(progreso, 1.0, "Listo.")
    return {
        "salida": salida,
        "subtitulos": ruta_subtitulos,
        "youtube": ruta_youtube,
        "narrativa": narrativa,
        "capitulos": capitulos,
        "duracion_original": dur_orig,
        "duracion_final": dur_final,
        "ahorro": ahorro,
        "segmentos": len(intervalos),
    }


def _progreso(callback, valor: float, mensaje: str) -> None:
    if callback:
        try:
            callback(valor, mensaje)
        except TypeError:
            callback(mensaje)
