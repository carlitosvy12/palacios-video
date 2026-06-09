"""Renderizado con FFmpeg + utilidades de salida para YouTube."""

import subprocess
import shutil
from pathlib import Path

from config import Config


def renderizar(
    ruta_entrada: str,
    intervalos: list,
    ruta_salida: str,
    ruta_subtitulos: str | None = None,
    cfg: Config | None = None,
) -> None:
    """Una sola pasada de FFmpeg: selecciona los tramos buenos de video y audio
    y los concatena.

    Usamos los filtros select/aselect (reencodean una vez) en lugar de cortar
    sin reencodear, porque cortar por keyframes deja cortes imprecisos. Aqui
    el corte cae exactamente donde queremos.

    Nota: con MUCHOS intervalos la expresion se vuelve enorme. Para v0 vale; si
    algun dia tienes cientos de cortes, migra a un fichero de concat.
    """
    if not intervalos:
        raise ValueError("No hay intervalos que renderizar.")

    expr = "+".join(f"between(t,{s:.3f},{e:.3f})" for s, e in intervalos)
    video_filter = f"select='{expr}',setpts=N/FRAME_RATE/TB"
    if ruta_subtitulos:
        cfg = cfg or Config()
        video_filter += (
            f",subtitles='{_ruta_filtro_ffmpeg(ruta_subtitulos)}'"
            f":force_style='{_estilo_subtitulos(cfg)}'"
        )

    cfg = cfg or Config()
    audio_filter = f"aselect='{expr}',asetpts=N/SR/TB"
    if cfg.normalizar_audio:
        audio_filter += (
            f",loudnorm=I={cfg.loudnorm_i}:"
            f"LRA={cfg.loudnorm_lra}:TP={cfg.loudnorm_tp}"
        )

    cmd = [
        _ffmpeg(), "-y", "-i", ruta_entrada,
        "-vf", video_filter,
        "-af", audio_filter,
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-profile:v", "high", "-movflags", "+faststart", "-c:a", "aac",
        ruta_salida,
    ]
    print(f"[render] renderizando -> {ruta_salida}")
    subprocess.run(cmd, check=True)


def _ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe

    try:
        import imageio_ffmpeg
    except ImportError as exc:
        raise RuntimeError(
            "No encuentro ffmpeg. Instala ffmpeg o ejecuta: "
            "python -m pip install imageio-ffmpeg"
        ) from exc

    return imageio_ffmpeg.get_ffmpeg_exe()


def _ruta_filtro_ffmpeg(ruta: str) -> str:
    """Escapa rutas de Windows para filtros FFmpeg como ass/subtitles."""
    normalizada = Path(ruta).resolve().as_posix()
    return normalizada.replace(":", r"\:").replace("'", r"\'")


def _estilo_subtitulos(cfg: Config) -> str:
    alignment = {
        "abajo-centro": 2,
        "abajo-izquierda": 1,
        "abajo-derecha": 3,
        "centro": 5,
        "arriba-centro": 8,
    }.get(cfg.subtitulos_posicion, 2)
    return ",".join(
        [
            f"FontName={cfg.subtitulos_fuente}",
            f"FontSize={cfg.subtitulos_tamano}",
            f"PrimaryColour={_ass_color(cfg.subtitulos_color_texto)}",
            f"OutlineColour={_ass_color(cfg.subtitulos_color_borde)}",
            "Bold=1",
            f"Outline={cfg.subtitulos_contorno}",
            f"Shadow={cfg.subtitulos_sombra}",
            f"Alignment={alignment}",
            f"MarginV={cfg.subtitulos_margen_v}",
        ]
    )


def _ass_color(hex_color: str) -> str:
    limpio = hex_color.strip().lstrip("#")
    if len(limpio) != 6:
        limpio = "FFFFFF"
    rr, gg, bb = limpio[0:2], limpio[2:4], limpio[4:6]
    return f"&H00{bb}{gg}{rr}&"


def _hms(segundos: float) -> str:
    s = int(segundos)
    h, resto = divmod(s, 3600)
    m, s = divmod(resto, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def formato_capitulos_youtube(capitulos: list) -> str:
    """Convierte la lista de capitulos del LLM al formato de YouTube:
        00:00 Introduccion
        01:35 Tema principal
    YouTube exige que el primero sea 00:00.
    """
    if not capitulos:
        return ""
    lineas = []
    for i, c in enumerate(sorted(capitulos, key=lambda x: x["inicio"])):
        inicio = 0 if i == 0 else c["inicio"]
        lineas.append(f"{_hms(inicio)} {c['titulo']}")
    return "\n".join(lineas)
