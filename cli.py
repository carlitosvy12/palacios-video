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
import sys
from pathlib import Path

from config import Config
from motor.pipeline import editar_video


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

    try:
        resultado = editar_video(str(entrada), cfg, usar_llm=not args.sin_llm)
    except (FileNotFoundError, RuntimeError) as exc:
        sys.exit(str(exc))

    dur_orig = resultado["duracion_original"]
    dur_final = resultado["duracion_final"]
    ahorro = resultado["ahorro"]
    print(f"\n  Original: {dur_orig:7.1f}s")
    print(f"  Editado : {dur_final:7.1f}s")
    print(f"  Recorte : {ahorro:6.1f}%  ({resultado['segmentos']} segmentos)\n")

    if resultado["subtitulos"]:
        print(f"  Subtitulos -> {resultado['subtitulos']}")

    narrativa = resultado["narrativa"]
    if narrativa:
        if "error" in narrativa:
            print(f"  [aviso] {narrativa['error']}")
        elif resultado["youtube"]:
            print(f"  Metadata YouTube -> {resultado['youtube']}")
        if "error" not in narrativa and narrativa.get("secciones_flojas"):
            print("\n  Secciones flojas detectadas (revisa si recortar):")
            for s in narrativa["secciones_flojas"]:
                print(f"    [{s['inicio']:.0f}-{s['fin']:.0f}s] {s['motivo']}")

    print(f"\nListo: {resultado['salida']}")


if __name__ == "__main__":
    main()
