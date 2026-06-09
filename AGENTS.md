# AGENTS.md — Contexto para agentes de IA

> Léelo antes de tocar nada. (Sirve igual como `CLAUDE.md` para Claude Code o
> como reglas de Cursor/Codex.)

## Qué es esto

Palacios Video: motor que coge horas de grabación en bruto de un creador y
produce un vídeo de YouTube editado y casi listo para publicar. La promesa NO
es "te ayudo a editar", es "edito por ti".

Estado actual: **motor en local por CLI**. NO hay web, ni API, ni base de
datos, ni login, ni pagos. Y no los habrá hasta que el motor demuestre que
produce cortes publicables. No los construyas aunque parezca el siguiente paso
obvio.

## Arquitectura

```
config.py            parámetros (corte, modelos, muletillas)
motor/
  transcribir.py     faster-whisper -> palabras + segmentos con timestamps
  cortar.py          LÓGICA PURA: silencios + muletillas -> intervalos
  narrativa.py       LLM -> gancho, capítulos, título, secciones flojas
  render.py          FFmpeg (select/aselect) + capítulos YouTube
cli.py               orquesta el pipeline
tests/test_cortar.py tests de la lógica de corte (sin vídeo)
```

Pipeline: `transcribir -> cortar -> [narrativa] -> render`

## Reglas de oro

1. **`cortar.py` es lógica pura.** Sin IO, sin red, sin ffmpeg. Así se testea
   sin vídeo. Si añades lógica de corte, añade su test en `tests/`.
2. **La capa narrativa cuesta dinero (tokens).** Debe poder desactivarse
   (`--sin-llm`). Nunca la hagas obligatoria.
3. **Muletillas: conservador.** NO metas "pues", "bueno", "o sea", "este" en la
   lista por defecto: son palabras legítimas y destrozan frases.
4. **El padding en los cortes no se toca a 0.** Es lo que evita el efecto
   "metralleta" (la queja nº1 de los usuarios de Gling).
5. **Idioma primero: español.** Es la ventaja competitiva. No degrades el
   soporte de español por optimizar inglés.

## Diferenciación

Limpiar silencios/muletillas es commodity (lo hace Gling). Lo que nos separa es
`narrativa.py`: estructura editorial real (gancho, capítulos, recortes por
contenido). Ahí va el esfuerzo de calidad.

## Cómo correr

```bash
pip install -r requirements.txt
python cli.py video.mp4              # pipeline completo
python cli.py video.mp4 --sin-llm    # solo corte, sin tokens
python tests/test_cortar.py          # tests
```

Requiere `ffmpeg` en el sistema y `ANTHROPIC_API_KEY` para la capa narrativa.
