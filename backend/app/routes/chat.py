"""
CineAI Backend - Chat Routes
Endpoint de chat que conecta al usuario con el servicio LLM.
"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import ChatRequest, ChatResponse, RecommendedMovie
from app.services import movie_service, llm_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_llm(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Envía un mensaje al asistente LLM y devuelve recomendaciones.

    Flujo:
    1. Obtener contexto de películas del catálogo.
    2. Enviar mensaje + contexto al microservicio LLM.
    3. Buscar las películas recomendadas por ID en la DB.
    4. Devolver respuesta del LLM + datos de películas recomendadas.
    """
    logger.info("POST /api/chat: message='%s'", request.message[:100])

    # 1. Obtener contexto del catálogo
    movie_context = await movie_service.get_movies_for_llm_context(db, limit=150)
    logger.info("POST /api/chat: built movie context with %d entries", len(movie_context))

    # 2. Enviar al LLM
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in request.conversation_history
    ]

    llm_response = await llm_client.send_to_llm(
        user_message=request.message,
        conversation_history=conversation_history,
        movie_context=movie_context,
    )

    # 3. Buscar películas recomendadas en la DB
    recommended_ids = llm_response.get("recommended_movie_ids", [])
    recommended_movies = []

    for movie_id in recommended_ids:
        try:
            movie = await movie_service.get_movie_by_id(db, int(movie_id))
            if movie:
                recommended_movies.append(
                    RecommendedMovie(
                        id=movie.id,
                        title=movie.title,
                        poster_path=movie.poster_path,
                        vote_average=movie.vote_average,
                    )
                )
        except (ValueError, TypeError) as exc:
            logger.warning(
                "POST /api/chat: invalid movie_id=%s from LLM: %s",
                movie_id, exc,
            )
            continue

    logger.info(
        "POST /api/chat: returning %d recommended movies",
        len(recommended_movies),
    )

    return ChatResponse(
        response=llm_response.get("response", "No pude generar una respuesta."),
        recommended_movies=recommended_movies,
    )
