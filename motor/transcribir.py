"""Transcripcion con faster-whisper.

Devolvemos dos cosas:
  - palabras: timestamps a nivel de palabra (los necesita el cortador para
    cortar con precision y para localizar muletillas).
  - segmentos: frases con timestamps (mas legibles; se los pasamos al LLM para
    que razone sobre narrativa sin ahogarse en ruido palabra-a-palabra).
"""

from faster_whisper import WhisperModel

from config import Config


def transcribir(ruta_video: str, cfg: Config) -> dict:
    print(f"[transcribir] cargando modelo '{cfg.modelo_whisper}'...")
    # int8 en CPU: lo bastante rapido para iterar en local sin GPU.
    modelo = WhisperModel(cfg.modelo_whisper, device="cpu", compute_type="int8")

    print("[transcribir] transcribiendo (puede tardar ~tiempo real en CPU)...")
    segmentos_iter, info = modelo.transcribe(
        ruta_video, language=cfg.idioma, word_timestamps=True
    )

    palabras = []
    segmentos = []
    for seg in segmentos_iter:
        segmentos.append(
            {"inicio": seg.start, "fin": seg.end, "texto": seg.text.strip()}
        )
        if seg.words:
            for w in seg.words:
                palabras.append(
                    {"inicio": w.start, "fin": w.end, "texto": w.word}
                )

    print(f"[transcribir] {len(palabras)} palabras, {len(segmentos)} segmentos.")
    return {
        "palabras": palabras,
        "segmentos": segmentos,
        "duracion": info.duration,
    }
