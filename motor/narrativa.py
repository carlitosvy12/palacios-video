"""Capa narrativa con LLM. ESTO es lo que te diferencia de Gling.

Gling y companhia solo limpian (silencios/muletillas). Aqui damos el salto:
sobre el transcript ya transcrito, pedimos a un LLM que actue como editor y
devuelva una estructura editorial: gancho, secciones flojas (por CONTENIDO, no
por silencio), capitulos, titulo y descripcion listos para YouTube.

Cuesta dinero (tokens), por eso en el CLI es opcional (--sin-llm).

Requiere: ANTHROPIC_API_KEY como variable de entorno.
"""

import json
import os

from config import Config

PROMPT_SISTEMA = (
    "Eres un editor de video de YouTube experto. Recibes la transcripcion con "
    "marcas de tiempo de un video en bruto y devuelves un analisis editorial. "
    "Respondes SIEMPRE y UNICAMENTE con un objeto JSON valido, sin texto "
    "adicional, sin markdown, sin explicaciones."
)

PLANTILLA = """Transcripcion del video (cada linea: [inicio-fin] texto):

{transcript}

Devuelve un JSON con esta forma exacta:
{{
  "titulo": "titulo sugerido para YouTube, con gancho, max 70 caracteres",
  "descripcion": "2-3 frases para la descripcion del video",
  "gancho_inicio": "timestamp (segundos, numero) del mejor momento para abrir el video",
  "capitulos": [
    {{"inicio": 0, "titulo": "Introduccion"}},
    {{"inicio": 95, "titulo": "..."}}
  ],
  "secciones_flojas": [
    {{"inicio": 0, "fin": 0, "motivo": "por que esta seccion es aburrida o se puede recortar"}}
  ]
}}

Reglas:
- Los timestamps son numeros en segundos.
- "secciones_flojas" son tramos que recortarias por CONTENIDO (divagaciones,
  repeticiones, partes aburridas), no por silencio.
- Se honesto: si no hay secciones flojas, devuelve lista vacia."""


def _formatear_transcript(segmentos: list) -> str:
    lineas = []
    for s in segmentos:
        lineas.append(f"[{s['inicio']:.0f}-{s['fin']:.0f}] {s['texto']}")
    return "\n".join(lineas)


def analizar_narrativa(segmentos: list, cfg: Config) -> dict:
    """Llama al LLM y devuelve el analisis editorial parseado.

    Si algo falla (sin API key, error de red, JSON invalido) devuelve un dict
    vacio con la clave 'error' en vez de reventar: el corte ya es util por si
    solo, la narrativa es un extra.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return {"error": "Falta ANTHROPIC_API_KEY. Saltando capa narrativa."}

    try:
        from anthropic import Anthropic
    except ImportError:
        return {"error": "Instala 'anthropic' (pip install anthropic)."}

    cliente = Anthropic()
    transcript = _formatear_transcript(segmentos)

    print("[narrativa] analizando con el LLM...")
    respuesta = cliente.messages.create(
        model=cfg.modelo_llm,
        max_tokens=cfg.max_tokens_llm,
        system=PROMPT_SISTEMA,
        messages=[{"role": "user", "content": PLANTILLA.format(transcript=transcript)}],
    )

    texto = "".join(b.text for b in respuesta.content if b.type == "text").strip()
    # quitar fences ```json por si el modelo los anade
    texto = texto.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return {"error": "El LLM no devolvio JSON valido.", "crudo": texto}
