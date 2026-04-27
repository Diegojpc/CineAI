-- ============================================
-- CineAI - Database Initialization Script
-- ============================================
-- Este script se ejecuta automáticamente en el primer
-- docker-compose up si el volumen de PostgreSQL está vacío.

CREATE TABLE IF NOT EXISTS genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    tmdb_id INTEGER UNIQUE
);

CREATE TABLE IF NOT EXISTS movies (
    id SERIAL PRIMARY KEY,
    tmdb_id INTEGER UNIQUE,
    title VARCHAR(500) NOT NULL,
    original_title VARCHAR(500),
    overview TEXT,
    release_date DATE,
    poster_path VARCHAR(500),
    backdrop_path VARCHAR(500),
    vote_average FLOAT DEFAULT 0.0,
    vote_count INTEGER DEFAULT 0,
    popularity FLOAT DEFAULT 0.0,
    original_language VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS movie_genres (
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);

-- Índice para búsqueda full-text en español
CREATE INDEX IF NOT EXISTS idx_movies_search 
    ON movies USING gin(to_tsvector('spanish', title || ' ' || COALESCE(overview, '')));

-- Índice para ordenar por popularidad
CREATE INDEX IF NOT EXISTS idx_movies_popularity ON movies(popularity DESC);

-- Índice para ordenar por rating
CREATE INDEX IF NOT EXISTS idx_movies_rating ON movies(vote_average DESC);
