"""
CineAI Backend - Pydantic Schemas
Define los modelos de request/response para validación y serialización.
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


# ─── Genre Schemas ───────────────────────────────────────
class GenreOut(BaseModel):
    """Schema de salida para un género."""
    id: int
    name: str

    model_config = {"from_attributes": True}


# ─── Movie Schemas ───────────────────────────────────────
class MovieBase(BaseModel):
    """Campos compartidos de una película."""
    title: str
    original_title: Optional[str] = None
    overview: Optional[str] = None
    release_date: Optional[date] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    vote_average: float = 0.0
    vote_count: int = 0
    popularity: float = 0.0
    original_language: Optional[str] = None


class MovieOut(MovieBase):
    """Schema de salida para una película (listado)."""
    id: int
    genres: list[GenreOut] = []

    model_config = {"from_attributes": True}


class MovieDetailOut(MovieBase):
    """Schema de salida para detalle de película."""
    id: int
    tmdb_id: Optional[int] = None
    genres: list[GenreOut] = []
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Pagination ──────────────────────────────────────────
class PaginatedMovies(BaseModel):
    """Respuesta paginada de películas."""
    movies: list[MovieOut]
    total: int
    page: int
    pages: int


# ─── Chat Schemas ────────────────────────────────────────
class ChatMessageIn(BaseModel):
    """Mensaje del usuario en el chat."""
    role: str = "user"
    content: str


class ChatRequest(BaseModel):
    """Request para el endpoint de chat."""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_history: list[ChatMessageIn] = []


class RecommendedMovie(BaseModel):
    """Película recomendada en la respuesta del chat."""
    id: int
    title: str
    poster_path: Optional[str] = None
    vote_average: float = 0.0


class ChatResponse(BaseModel):
    """Response del endpoint de chat."""
    response: str
    recommended_movies: list[RecommendedMovie] = []


# ─── Health ──────────────────────────────────────────────
class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    service: str = "backend"
