"""
CineAI LLM Service - Gemini Client
Integración con Google Gemini API para generar recomendaciones.
"""
import logging
import re
from google import genai
from app.config import settings
from app.services.prompt_builder import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Inicializar cliente de Gemini
_client = None


def get_gemini_client() -> genai.Client:
    """Singleton lazy del cliente Gemini."""
    global _client
    if _client is None:
        logger.info("Initializing Gemini client with model=%s", settings.gemini_model)
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def parse_recommended_ids(response_text: str) -> list[int]:
    """
    Extrae los IDs de películas recomendadas del texto de respuesta.

    Busca la línea: RECOMMENDED_IDS: [1, 2, 3]

    Args:
        response_text: Texto completo de la respuesta del LLM.

    Returns:
        Lista de IDs enteros.
    """
    logger.debug("parse_recommended_ids: parsing response of length=%d", len(response_text))

    # Buscar el patrón RECOMMENDED_IDS: [...]
    pattern = r"RECOMMENDED_IDS:\s*\[([\d\s,]*)\]"
    match = re.search(pattern, response_text)

    if not match:
        logger.warning("parse_recommended_ids: no RECOMMENDED_IDS pattern found")
        return []

    ids_str = match.group(1).strip()
    if not ids_str:
        return []

    try:
        ids = [int(x.strip()) for x in ids_str.split(",") if x.strip()]
        logger.info("parse_recommended_ids: extracted IDs=%s", ids)
        return ids
    except ValueError as exc:
        logger.error("parse_recommended_ids: failed to parse IDs: %s", exc)
        return []


def clean_response_text(response_text: str) -> str:
    """
    Limpia el texto de respuesta removiendo la línea RECOMMENDED_IDS.

    Args:
        response_text: Texto completo de la respuesta del LLM.

    Returns:
        Texto limpio sin la línea de IDs.
    """
    # Remover la línea de RECOMMENDED_IDS
    cleaned = re.sub(r"\n?\s*RECOMMENDED_IDS:\s*\[[\d\s,]*\]\s*$", "", response_text)
    return cleaned.strip()


async def generate_recommendation(messages: list[dict]) -> dict:
    """
    Genera una recomendación usando Gemini.

    Args:
        messages: Lista de mensajes formateados (role/content).

    Returns:
        dict con 'response' (texto limpio) y 'recommended_movie_ids' (lista de IDs).
    """
    logger.info("generate_recommendation: sending %d messages to Gemini", len(messages))

    try:
        client = get_gemini_client()

        # Construir el contenido para Gemini
        # Gemini usa una estructura de contenido diferente
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                genai.types.Content(
                    role=role,
                    parts=[genai.types.Part(text=msg["content"])],
                )
            )

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=contents,
            config=genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=1500,
            ),
        )

        response_text = response.text
        logger.info(
            "generate_recommendation: received response of length=%d",
            len(response_text),
        )

        # Extraer IDs y limpiar respuesta
        recommended_ids = parse_recommended_ids(response_text)
        clean_text = clean_response_text(response_text)

        return {
            "response": clean_text,
            "recommended_movie_ids": recommended_ids,
        }

    except Exception as exc:
        logger.error(
            "generate_recommendation: Gemini API error: %s",
            exc, exc_info=True,
        )
        return {
            "response": "Lo siento, hubo un problema al generar la recomendación. Por favor intenta de nuevo.",
            "recommended_movie_ids": [],
        }
