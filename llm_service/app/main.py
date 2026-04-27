"""
CineAI LLM Service - FastAPI Application
Microservicio dedicado a la orquestación del LLM para recomendaciones.
"""
import logging
from fastapi import FastAPI
from app.config import settings
from app.schemas import RecommendRequest, RecommendResponse, HealthResponse
from app.services.prompt_builder import build_catalog_context, build_messages
from app.services.gemini_client import generate_recommendation

# ─── Logging ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── App ─────────────────────────────────────────────────
app = FastAPI(
    title="CineAI - LLM Recommendation Service",
    description="Microservicio de recomendaciones de películas basado en Gemini.",
    version="1.0.0",
)


@app.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):
    """
    Genera recomendaciones de películas basadas en lenguaje natural.

    Flujo:
    1. Construir contexto del catálogo.
    2. Construir mensajes con historial.
    3. Enviar a Gemini y parsear respuesta.
    """
    logger.info(
        "POST /recommend: message='%s', catalog_size=%d, history_size=%d",
        request.user_message[:100],
        len(request.movie_catalog),
        len(request.conversation_history),
    )

    # 1. Construir contexto del catálogo
    catalog_dicts = [m.model_dump() for m in request.movie_catalog]
    catalog_context = build_catalog_context(catalog_dicts)

    # 2. Construir mensajes
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in request.conversation_history
    ]
    messages = build_messages(
        user_message=request.user_message,
        conversation_history=history,
        catalog_context=catalog_context,
    )

    # 3. Generar recomendación
    result = await generate_recommendation(messages)

    logger.info(
        "POST /recommend: response_length=%d, recommended_ids=%s",
        len(result["response"]),
        result["recommended_movie_ids"],
    )

    return RecommendResponse(
        response=result["response"],
        recommended_movie_ids=result["recommended_movie_ids"],
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok", service="llm_service")


logger.info("CineAI LLM Service configured. Endpoints: /recommend, /health")
