"""Interfaz grafica de Palacios Video."""

from pathlib import Path

import gradio as gr

from config import Config
from motor.pipeline import editar_video


def procesar(
    video,
    silencio,
    padding,
    subtitulos,
    narrativa,
    progress=gr.Progress(track_tqdm=False),
):
    if not video:
        raise gr.Error("Sube un video antes de editar.")

    if isinstance(video, dict):
        video = video.get("path") or video.get("name")

    cfg = Config()
    cfg.silencio_max = float(silencio)
    cfg.padding = float(padding)
    cfg.subtitulos = bool(subtitulos)

    def estado(valor: float, mensaje: str):
        progress(valor, desc=mensaje)

    try:
        resultado = editar_video(video, cfg, usar_llm=bool(narrativa), progreso=estado)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc

    meta = resultado["narrativa"] if resultado["narrativa"] else {}
    if "error" in meta:
        titulo = ""
        descripcion = meta["error"]
        capitulos = ""
    else:
        titulo = meta.get("titulo", "")
        descripcion = meta.get("descripcion", "")
        capitulos = resultado.get("capitulos", "")

    resumen = (
        f"Original: {resultado['duracion_original']:.1f}s | "
        f"Editado: {resultado['duracion_final']:.1f}s | "
        f"Recorte: {resultado['ahorro']:.1f}% | "
        f"Segmentos: {resultado['segmentos']}"
    )

    return str(resultado["salida"]), str(resultado["salida"]), titulo, descripcion, capitulos, resumen


with gr.Blocks(title="Palacios Video") as demo:
    gr.Markdown("# Palacios Video")

    with gr.Row():
        with gr.Column(scale=1):
            video = gr.Video(label="Video en bruto")
            silencio = gr.Slider(
                0.2,
                2.0,
                value=Config().silencio_max,
                step=0.1,
                label="Silencio maximo antes de cortar (s)",
            )
            padding = gr.Slider(
                0.0,
                0.6,
                value=Config().padding,
                step=0.02,
                label="Padding alrededor de cortes (s)",
            )
            subtitulos = gr.Checkbox(value=True, label="Anadir subtitulos")
            narrativa = gr.Checkbox(value=False, label="Generar metadata con LLM")
            editar = gr.Button("Editar", variant="primary")

        with gr.Column(scale=1):
            salida_video = gr.Video(label="Video editado")
            descarga = gr.File(label="Descargar video editado")
            resumen = gr.Textbox(label="Resumen", interactive=False)

    with gr.Row():
        titulo = gr.Textbox(label="Titulo de YouTube", interactive=False)
        descripcion = gr.Textbox(label="Descripcion", lines=5, interactive=False)
        capitulos = gr.Textbox(label="Capitulos", lines=8, interactive=False)

    editar.click(
        procesar,
        inputs=[video, silencio, padding, subtitulos, narrativa],
        outputs=[salida_video, descarga, titulo, descripcion, capitulos, resumen],
    )


if __name__ == "__main__":
    demo.launch()
