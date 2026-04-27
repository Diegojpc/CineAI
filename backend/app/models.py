"""
CineAI Backend - SQLAlchemy ORM Models
Define las tablas de películas, géneros y la relación many-to-many.
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Text, Date, DateTime,
    ForeignKey, Table
)
from sqlalchemy.orm import relationship
from app.database import Base


# Tabla asociativa many-to-many
movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)


class Genre(Base):
    """Modelo ORM para géneros de películas."""
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    tmdb_id = Column(Integer, unique=True, nullable=True)

    # Relación inversa
    movies = relationship("Movie", secondary=movie_genres, back_populates="genres")

    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"


class Movie(Base):
    """Modelo ORM para películas."""
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, nullable=True)
    title = Column(String(500), nullable=False)
    original_title = Column(String(500), nullable=True)
    overview = Column(Text, nullable=True)
    release_date = Column(Date, nullable=True)
    poster_path = Column(String(500), nullable=True)
    backdrop_path = Column(String(500), nullable=True)
    vote_average = Column(Float, default=0.0)
    vote_count = Column(Integer, default=0)
    popularity = Column(Float, default=0.0)
    original_language = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación many-to-many con géneros
    genres = relationship("Genre", secondary=movie_genres, back_populates="movies")

    def __repr__(self):
        return f"<Movie(id={self.id}, title='{self.title}')>"
