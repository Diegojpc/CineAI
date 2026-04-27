"""
CineAI Backend - Movie Service
Capa de lógica de negocio para operaciones con películas.
"""
import logging
import math
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import Movie, Genre

logger = logging.getLogger(__name__)


async def get_movies_paginated(
    db: AsyncSession,
    page: int = 1,
    limit: int = 20,
    genre_id: int | None = None,
    sort_by: str = "popularity",
) -> tuple[list[Movie], int]:
    """
    Obtiene películas paginadas con sus géneros.

    Args:
        db: Sesión async de la base de datos.
        page: Número de página (1-indexed).
        limit: Cantidad de resultados por página.
        genre_id: Filtrar por ID de género (opcional).
        sort_by: Campo de ordenamiento (popularity, vote_average, release_date).

    Returns:
        Tupla (lista de películas, total de registros).
    """
    logger.info(
        "get_movies_paginated: page=%d, limit=%d, genre_id=%s, sort_by=%s",
        page, limit, genre_id, sort_by,
    )
    offset = (page - 1) * limit

    # Query base con eager loading de géneros
    query = select(Movie).options(selectinload(Movie.genres))

    # Filtro por género
    if genre_id:
        query = query.join(Movie.genres).where(Genre.id == genre_id)

    # Ordenamiento
    sort_column = {
        "popularity": Movie.popularity.desc(),
        "vote_average": Movie.vote_average.desc(),
        "release_date": Movie.release_date.desc(),
    }.get(sort_by, Movie.popularity.desc())
    query = query.order_by(sort_column)

    # Contar total
    count_query = select(func.count(Movie.id))
    if genre_id:
        count_query = count_query.join(Movie.genres).where(Genre.id == genre_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginación
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    movies = result.scalars().unique().all()

    logger.info("get_movies_paginated: returned %d movies, total=%d", len(movies), total)
    return list(movies), total


async def get_movie_by_id(db: AsyncSession, movie_id: int) -> Movie | None:
    """Obtiene una película por ID con sus géneros."""
    logger.info("get_movie_by_id: movie_id=%d", movie_id)
    query = select(Movie).options(selectinload(Movie.genres)).where(Movie.id == movie_id)
    result = await db.execute(query)
    movie = result.scalars().first()
    if not movie:
        logger.warning("get_movie_by_id: movie_id=%d not found", movie_id)
    return movie


async def search_movies(
    db: AsyncSession,
    query_text: str,
    limit: int = 20,
) -> tuple[list[Movie], int]:
    """
    Búsqueda de películas por texto usando full-text search de PostgreSQL.

    Args:
        db: Sesión async de la base de datos.
        query_text: Término de búsqueda.
        limit: Máximo de resultados.

    Returns:
        Tupla (lista de películas, total encontrado).
    """
    logger.info("search_movies: query='%s', limit=%d", query_text, limit)

    # Usar ILIKE como fallback más simple y confiable
    search_pattern = f"%{query_text}%"
    query = (
        select(Movie)
        .options(selectinload(Movie.genres))
        .where(
            or_(
                Movie.title.ilike(search_pattern),
                Movie.overview.ilike(search_pattern),
            )
        )
        .order_by(Movie.popularity.desc())
        .limit(limit)
    )

    result = await db.execute(query)
    movies = result.scalars().unique().all()

    # Contar total
    count_query = select(func.count(Movie.id)).where(
        or_(
            Movie.title.ilike(search_pattern),
            Movie.overview.ilike(search_pattern),
        )
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    logger.info("search_movies: found %d movies for query='%s'", total, query_text)
    return list(movies), total


async def get_all_genres(db: AsyncSession) -> list[Genre]:
    """Obtiene todos los géneros disponibles."""
    logger.info("get_all_genres: fetching all genres")
    result = await db.execute(select(Genre).order_by(Genre.name))
    genres = result.scalars().all()
    logger.info("get_all_genres: returned %d genres", len(genres))
    return list(genres)


async def get_movies_for_llm_context(
    db: AsyncSession,
    limit: int = 100,
) -> list[dict]:
    """
    Obtiene un resumen de películas para enviar como contexto al LLM.
    Devuelve datos mínimos para no exceder el token limit.
    """
    logger.info("get_movies_for_llm_context: fetching up to %d movies", limit)
    query = (
        select(Movie)
        .options(selectinload(Movie.genres))
        .order_by(Movie.popularity.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    movies = result.scalars().unique().all()

    context = []
    for m in movies:
        context.append({
            "id": m.id,
            "title": m.title,
            "genres": [g.name for g in m.genres],
            "year": m.release_date.year if m.release_date else None,
            "overview": (m.overview[:200] + "...") if m.overview and len(m.overview) > 200 else m.overview,
            "vote_average": m.vote_average,
            "poster_path": m.poster_path,
        })

    logger.info("get_movies_for_llm_context: built context for %d movies", len(context))
    return context
