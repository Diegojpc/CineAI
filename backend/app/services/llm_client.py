"""
CineAI Backend - LLM Client
HTTP client para comunicarse con el microservicio LLM.
"""
import logging
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

# Timeout generoso: el LLM puede tardar
LLM_TIMEOUT = httpx.Timeout(timeout=60.0, connect=10.0)


async def send_to_llm(
    user_message: str,
    conversation_history: list[dict],
    movie_context: list[dict],
) -> dict:
    """
    Envía la consulta del usuario al microservicio LLM.

    Args:
        user_message: Mensaje actual del usuario.
        conversation_history: Historial de mensajes previos.
        movie_context: Lista de películas del catálogo para contexto.

    Returns:
        dict con 'response' (texto) y 'recommended_movie_ids' (lista de IDs).

    Raises:
        httpx.HTTPStatusError: Si el LLM service responde con error.
        httpx.ConnectError: Si el LLM service no está disponible.
    """
    llm_url = f"{settings.llm_service_url}/recommend"
    payload = {
        "user_message": user_message,
        "conversation_history": conversation_history,
        "movie_catalog": movie_context,
    }

    logger.info(
        "send_to_llm: sending request to %s, message='%s', catalog_size=%d",
        llm_url,
        user_message[:80],
        len(movie_context),
    )

    try:
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            response = await client.post(llm_url, json=payload)
            response.raise_for_status()

        data = response.json()
        logger.info(
            "send_to_llm: received response, recommended_ids=%s",
            data.get("recommended_movie_ids", []),
        )
        return data

    except httpx.ConnectError as exc:
        logger.error(
            "send_to_llm: LLM service unreachable at %s: %s",
            llm_url, exc, exc_info=True,
        )
        return {
            "response": "Lo siento, el servicio de recomendaciones no está disponible en este momento. Intenta de nuevo más tarde.",
            "recommended_movie_ids": [],
        }
    except httpx.HTTPStatusError as exc:
        logger.error(
            "send_to_llm: LLM service returned error %d: %s",
            exc.response.status_code,
            exc.response.text[:200],
            exc_info=True,
        )
        return {
            "response": "Hubo un error al procesar tu solicitud. Intenta reformular tu pregunta.",
            "recommended_movie_ids": [],
        }
    except Exception as exc:
        logger.error(
            "send_to_llm: unexpected error: %s", exc, exc_info=True,
        )
        return {
            "response": "Error inesperado al contactar el servicio de IA. Intenta de nuevo.",
            "recommended_movie_ids": [],
        }
