"""
CineAI Backend - TMDB Seeder
Script para poblar la base de datos con películas populares de TMDB.

Uso (dentro del contenedor backend):
    python -m app.seed.tmdb_seeder

O mediante docker-compose:
    docker-compose exec backend python -m app.seed.tmdb_seeder
"""
import asyncio
import logging
import os
import sys
import httpx
from sqlalchemy import select
from app.database import AsyncSessionLocal, init_db
from app.models import Movie, Genre

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
# Pedir películas en español para el catálogo
TMDB_LANGUAGE = "es-ES"
# Cantidad de páginas a traer (20 películas por página)
TOTAL_PAGES = 15  # 15 páginas × 20 = 300 películas


async def fetch_tmdb_genres(client: httpx.AsyncClient) -> list[dict]:
    """Obtiene la lista de géneros de TMDB."""
    logger.info("Fetching genres from TMDB...")
    url = f"{TMDB_BASE_URL}/genre/movie/list"
    params = {"api_key": TMDB_API_KEY, "language": TMDB_LANGUAGE}

    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        genres = response.json().get("genres", [])
        logger.info("Fetched %d genres from TMDB", len(genres))
        return genres
    except Exception as exc:
        logger.error("Failed to fetch genres: %s", exc, exc_info=True)
        return []


async def fetch_tmdb_popular_movies(
    client: httpx.AsyncClient, page: int
) -> list[dict]:
    """Obtiene una página de películas populares de TMDB."""
    url = f"{TMDB_BASE_URL}/movie/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "language": TMDB_LANGUAGE,
        "page": page,
    }

    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        results = response.json().get("results", [])
        logger.info("Fetched %d movies from TMDB page %d", len(results), page)
        return results
    except Exception as exc:
        logger.error("Failed to fetch movies page %d: %s", page, exc, exc_info=True)
        return []


async def seed_genres(session, tmdb_genres: list[dict]) -> dict[int, int]:
    """
    Inserta géneros en la DB y devuelve un mapeo tmdb_id → db_id.
    """
    logger.info("Seeding %d genres...", len(tmdb_genres))
    tmdb_to_db = {}

    for g in tmdb_genres:
        # Verificar si ya existe
        result = await session.execute(
            select(Genre).where(Genre.tmdb_id == g["id"])
        )
        existing = result.scalars().first()

        if existing:
            tmdb_to_db[g["id"]] = existing.id
            continue

        genre = Genre(name=g["name"], tmdb_id=g["id"])
        session.add(genre)
        await session.flush()
        tmdb_to_db[g["id"]] = genre.id

    await session.commit()
    logger.info("Genres seeded. Mapping: %d entries", len(tmdb_to_db))
    return tmdb_to_db


async def seed_movies(
    session, tmdb_movies: list[dict], genre_map: dict[int, int]
) -> int:
    """
    Inserta películas en la DB con sus relaciones de género.
    Retorna la cantidad de películas insertadas.
    """
    inserted = 0

    for m in tmdb_movies:
        # Verificar duplicado
        result = await session.execute(
            select(Movie).where(Movie.tmdb_id == m["id"])
        )
        if result.scalars().first():
            continue

        # Parsear release_date
        release_date = None
        if m.get("release_date"):
            try:
                from datetime import date as dt_date
                parts = m["release_date"].split("-")
                release_date = dt_date(int(parts[0]), int(parts[1]), int(parts[2]))
            except (ValueError, IndexError):
                release_date = None

        movie = Movie(
            tmdb_id=m["id"],
            title=m.get("title", "Sin título"),
            original_title=m.get("original_title"),
            overview=m.get("overview", ""),
            release_date=release_date,
            poster_path=m.get("poster_path"),
            backdrop_path=m.get("backdrop_path"),
            vote_average=m.get("vote_average", 0.0),
            vote_count=m.get("vote_count", 0),
            popularity=m.get("popularity", 0.0),
            original_language=m.get("original_language"),
        )

        # Asignar géneros
        genre_ids = m.get("genre_ids", [])
        for tmdb_genre_id in genre_ids:
            db_genre_id = genre_map.get(tmdb_genre_id)
            if db_genre_id:
                result = await session.execute(
                    select(Genre).where(Genre.id == db_genre_id)
                )
                genre_obj = result.scalars().first()
                if genre_obj:
                    movie.genres.append(genre_obj)

        session.add(movie)
        inserted += 1

    await session.commit()
    return inserted


async def run_seeder():
    """Ejecuta el proceso completo de seeding."""
    if not TMDB_API_KEY or TMDB_API_KEY == "your_tmdb_api_key_here":
        logger.error(
            "TMDB_API_KEY no configurada. "
            "Establece la variable de entorno TMDB_API_KEY con tu API key de TMDB."
        )
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("CineAI TMDB Seeder - Iniciando")
    logger.info("Páginas a traer: %d (~%d películas)", TOTAL_PAGES, TOTAL_PAGES * 20)
    logger.info("=" * 60)

    # Inicializar DB
    await init_db()

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Seedear géneros
        tmdb_genres = await fetch_tmdb_genres(client)
        if not tmdb_genres:
            logger.error("No se pudieron obtener géneros. Abortando.")
            sys.exit(1)

        async with AsyncSessionLocal() as session:
            genre_map = await seed_genres(session, tmdb_genres)

        # 2. Seedear películas página por página
        total_inserted = 0
        for page in range(1, TOTAL_PAGES + 1):
            movies_data = await fetch_tmdb_popular_movies(client, page)
            if not movies_data:
                logger.warning("Página %d vacía, continuando...", page)
                continue

            async with AsyncSessionLocal() as session:
                count = await seed_movies(session, movies_data, genre_map)
                total_inserted += count
                logger.info(
                    "Página %d/%d: insertadas %d películas (total: %d)",
                    page, TOTAL_PAGES, count, total_inserted,
                )

            # Respetar rate limit de TMDB (40 req / 10s)
            await asyncio.sleep(0.3)

    logger.info("=" * 60)
    logger.info("Seeding completado. Total películas insertadas: %d", total_inserted)
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_seeder())
