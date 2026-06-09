# Palacios Video

Motor que convierte horas de grabación en bruto en un vídeo de YouTube editado
y casi listo para publicar. De *talking-head*, vlog o podcast con cámara →
corte limpio + título, descripción y capítulos.

## Qué hace hoy

- Transcribe el vídeo (faster-whisper, español).
- Elimina silencios largos y muletillas, con padding para que el corte no suene
  brusco.
- (Opcional, con LLM) Genera gancho, capítulos de YouTube, título, descripción
  y detecta secciones flojas por contenido.
- Renderiza el vídeo cortado con FFmpeg.

## Requisitos

- Python 3.10+
- `ffmpeg` instalado y en el PATH
- `ANTHROPIC_API_KEY` (solo para la capa narrativa)

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
# Pipeline completo (corte + narrativa)
python cli.py mi_video.mp4

# Solo corte, sin gastar tokens
python cli.py mi_video.mp4 --sin-llm

# Ajustes
python cli.py mi_video.mp4 --modelo medium --silencio 0.5
```

Salidas (junto al vídeo original):
- `mi_video_editado.mp4` — el vídeo cortado
- `mi_video_youtube.txt` — título, descripción y capítulos para pegar en YouTube

## Tests

```bash
python tests/test_cortar.py
```

## Roadmap

- **Fase 0 (hecho):** motor de corte en local.
- **Fase 0.5:** validar con vídeos reales. ¿El corte es publicable? Ajustar
  `padding` y `silencio_max` en `config.py`.
- **Fase 1:** mejorar `narrativa.py` (reordenar bloques, gancho automático real,
  miniatura).
- **Fase 2 (solo si el motor convence):** API + cola + UI web.

## Ajustes de calidad

Todo en `config.py`. Si los cortes salen agresivos, sube `padding` y
`silencio_max`. Si Whisper falla en español, sube `modelo_whisper` a `medium`.
