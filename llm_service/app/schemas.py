"""
CineAI LLM Service - Pydantic Schemas
"""
from pydantic import BaseModel, Field


class MovieContext(BaseModel):
    """Película del catálogo enviada como contexto."""
    id: int
    title: str
    genres: list[str] = []
    year: int | None = None
    overview: str | None = None
    vote_average: float = 0.0
    poster_path: str | None = None


class ConversationMessage(BaseModel):
    """Mensaje en el historial de conversación."""
    role: str
    content: str


class RecommendRequest(BaseModel):
    """Request al endpoint /recommend."""
    user_message: str = Field(..., min_length=1, max_length=2000)
    conversation_history: list[ConversationMessage] = []
    movie_catalog: list[MovieContext] = []


class RecommendResponse(BaseModel):
    """Response del endpoint /recommend."""
    response: str
    recommended_movie_ids: list[int] = []


class HealthResponse(BaseModel):
    """Health check."""
    status: str = "ok"
    service: str = "llm_service"
