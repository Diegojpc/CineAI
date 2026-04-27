"""
CineAI Backend - Movies Routes
Endpoints REST para el catálogo de películas.
"""
import logging
import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import MovieOut, MovieDetailOut, PaginatedMovies, GenreOut
from app.services import movie_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["movies"])


@router.get("/movies", response_model=PaginatedMovies)
async def list_movies(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(20, ge=1, le=100, description="Resultados por página"),
    genre_id: int | None = Query(None, description="Filtrar por ID de género"),
    sort_by: str = Query("popularity", description="Ordenar por: popularity, vote_average, release_date"),
    db: AsyncSession = Depends(get_db),
):
    """Listar películas con paginación, filtro por género y ordenamiento."""
    logger.info("GET /api/movies: page=%d, limit=%d, genre_id=%s, sort_by=%s", page, limit, genre_id, sort_by)
    movies, total = await movie_service.get_movies_paginated(db, page, limit, genre_id, sort_by)
    pages = math.ceil(total / limit) if total > 0 else 1
    return PaginatedMovies(movies=movies, total=total, page=page, pages=pages)


@router.get("/movies/search", response_model=PaginatedMovies)
async def search_movies(
    q: str = Query(..., min_length=1, max_length=200, description="Término de búsqueda"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de resultados"),
    db: AsyncSession = Depends(get_db),
):
    """Buscar películas por título o sinopsis."""
    logger.info("GET /api/movies/search: q='%s', limit=%d", q, limit)
    movies, total = await movie_service.search_movies(db, q, limit)
    return PaginatedMovies(movies=movies, total=total, page=1, pages=1)


@router.get("/movies/{movie_id}", response_model=MovieDetailOut)
async def get_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Obtener detalle de una película por ID."""
    logger.info("GET /api/movies/%d", movie_id)
    movie = await movie_service.get_movie_by_id(db, movie_id)
    if not movie:
        logger.warning("GET /api/movies/%d: not found", movie_id)
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return movie


@router.get("/genres", response_model=list[GenreOut])
async def list_genres(db: AsyncSession = Depends(get_db)):
    """Listar todos los géneros disponibles."""
    logger.info("GET /api/genres")
    genres = await movie_service.get_all_genres(db)
    return genres
