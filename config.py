"""Configuracion centralizada de Palacios Video.

Todo lo ajustable vive aqui para no tener numeros magicos repartidos por el
codigo. Cuando ajustes calidad de cortes, tocas esto.
"""

from dataclasses import dataclass, field


@dataclass
class Config:
    # --- Corte ---
    # Hueco de silencio (s) a partir del cual cortamos. Mas bajo = mas agresivo.
    silencio_max: float = 0.6
    # Padding a cada lado de un corte (s). Es lo que separa "limpio" de
    # "metralleta". No lo pongas a 0 o los cortes sonaran bruscos (queja nº1
    # de Gling).
    padding: float = 0.12

    # --- Transcripcion ---
    idioma: str = "es"
    # tiny | base | small | medium | large-v3. 'small' es buen punto de
    # partida en CPU; sube a 'medium' si el espanol se queda corto.
    modelo_whisper: str = "small"

    # Muletillas a eliminar. CONSERVADOR a proposito: "pues", "bueno", "o sea",
    # "este" tambien son palabras legitimas; si las metes aqui destrozaras
    # frases enteras. Empieza solo con interjecciones puras y amplia con datos
    # reales de que cortes acepta/rechaza el usuario.
    muletillas: set = field(
        default_factory=lambda: {"eh", "em", "ehm", "mmm", "mm", "uhm", "ah"}
    )

    # --- Subtitulos ---
    # Se queman en el video por defecto con un .srt y el filtro subtitles de
    # ffmpeg. Estilo moderno: blanco, borde negro y abajo-centro.
    subtitulos: bool = True
    subtitulos_fuente: str = "Arial Black"
    subtitulos_tamano: int = 34
    subtitulos_color_texto: str = "#FFFFFF"
    subtitulos_color_borde: str = "#000000"
    subtitulos_posicion: str = "abajo-centro"
    subtitulos_contorno: int = 3
    subtitulos_sombra: int = 1
    subtitulos_margen_v: int = 70
    subtitulos_palabras_max: int = 3
    subtitulos_duracion_max: float = 1.15
    subtitulos_chars_max: int = 22
    subtitulos_hueco_max: float = 0.35

    # --- Audio ---
    normalizar_audio: bool = True
    loudnorm_i: float = -16.0
    loudnorm_lra: float = 11.0
    loudnorm_tp: float = -1.5

    # --- Capa narrativa (LLM) ---
    # Sonnet por defecto: buen balance coste/calidad para analizar transcripts
    # largos. Opus solo si necesitas mas calidad y te sobra presupuesto.
    modelo_llm: str = "claude-sonnet-4-6"
    max_tokens_llm: int = 2000
