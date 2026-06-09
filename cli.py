"""Palacios Video - CLI.

Orquesta el pipeline completo:
    transcribir -> cortar -> [narrativa con LLM] -> render

Uso:
    python cli.py video.mp4
    python cli.py video.mp4 --sin-llm          # solo corte (gratis, sin tokens)
    python cli.py video.mp4 --modelo medium --silencio 0.5

Salidas (junto al video original):
    <nombre>_editado.mp4   el video cortado
    <nombre>_youtube.txt   titulo, descripcion y capitulos para pegar en YouTube
"""

import argparse
import json
import sys
from pathlib import Path

from config import Config
from motor import cortar, render
from motor.subtitulos import generar_srt
from motor.transcribir import transcribir


def main():
    ap = argparse.ArgumentParser(description="Palacios Video - motor de edicion")
    ap.add_argument("video", help="ruta al video en bruto")
    ap.add_argument("--modelo", help="modelo whisper: tiny|base|small|medium")
    ap.add_argument("--silencio", type=float, help="hueco de silencio (s) para cortar")
    ap.add_argument("--sin-llm", action="store_true",
                    help="salta la capa narrativa (no gasta tokens)")
    ap.add_argument("--sin-subtitulos", action="store_true",
                    help="no quema subtitulos en el video final")
    args = ap.parse_args()

    cfg = Config()
    if args.modelo:
        cfg.modelo_whisper = args.modelo
    if args.silencio is not None:
        cfg.silencio_max = args.silencio
    if args.sin_subtitulos:
        cfg.subtitulos = False

    entrada = Path(args.video)
    if not entrada.exists():
        sys.exit(f"No existe el archivo: {entrada}")

    # 1. Transcribir
    datos = transcribir(str(entrada), cfg)

    # 2. Cortar (logica pura)
    intervalos = cortar.construir_intervalos(datos["palabras"], cfg)
    if not intervalos:
        sys.exit("No se detecto habla utilizable.")

    dur_orig = datos["duracion"]
    dur_final = cortar.duracion_total(intervalos)
    ahorro = (1 - dur_final / dur_orig) * 100 if dur_orig else 0
    print(f"\n  Original: {dur_orig:7.1f}s")
    print(f"  Editado : {dur_final:7.1f}s")
    print(f"  Recorte : {ahorro:6.1f}%  ({len(intervalos)} segmentos)\n")

    # 3. Capa narrativa (opcional)
    narrativa = {}
    if not args.sin_llm:
        from motor.narrativa import analizar_narrativa
        narrativa = analizar_narrativa(datos["segmentos"], cfg)
        if "error" in narrativa:
            print(f"  [aviso] {narrativa['error']}")

    # 4. Render
    salida = entrada.with_name(f"{entrada.stem}_editado.mp4")
    ruta_subtitulos = None
    if cfg.subtitulos:
        ruta_subtitulos = entrada.with_name(f"{entrada.stem}_subtitulos.srt")
        generar_srt(datos["palabras"], intervalos, str(ruta_subtitulos), cfg)
        print(f"  Subtitulos -> {ruta_subtitulos}")

    render.renderizar(
        str(entrada),
        intervalos,
        str(salida),
        str(ruta_subtitulos) if ruta_subtitulos else None,
        cfg,
    )

    # 5. Metadata para YouTube
    if narrativa and "error" not in narrativa:
        txt = entrada.with_name(f"{entrada.stem}_youtube.txt")
        capitulos = render.formato_capitulos_youtube(narrativa.get("capitulos", []))
        contenido = (
            f"TITULO:\n{narrativa.get('titulo', '')}\n\n"
            f"DESCRIPCION:\n{narrativa.get('descripcion', '')}\n\n"
            f"CAPITULOS:\n{capitulos}\n"
        )
        txt.write_text(contenido, encoding="utf-8")
        print(f"  Metadata YouTube -> {txt}")
        if narrativa.get("secciones_flojas"):
            print("\n  Secciones flojas detectadas (revisa si recortar):")
            for s in narrativa["secciones_flojas"]:
                print(f"    [{s['inicio']:.0f}-{s['fin']:.0f}s] {s['motivo']}")

    print(f"\nListo: {salida}")


if __name__ == "__main__":
    main()
