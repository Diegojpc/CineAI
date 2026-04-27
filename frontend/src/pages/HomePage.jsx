import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { getMovies, searchMovies, getGenres } from '../services/api'
import MovieGrid from '../components/MovieGrid'
import './HomePage.css'

export default function HomePage() {
  const [searchParams] = useSearchParams()
  const searchQuery = searchParams.get('search') || ''

  const [movies, setMovies] = useState([])
  const [genres, setGenres] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [activeGenre, setActiveGenre] = useState(null)
  const [sortBy, setSortBy] = useState('popularity')

  // Fetch genres on mount
  useEffect(() => {
    getGenres().then(setGenres).catch(console.error)
  }, [])

  // Fetch movies
  useEffect(() => {
    const fetchMovies = async () => {
      setLoading(true)
      try {
        let data
        if (searchQuery) {
          data = await searchMovies(searchQuery, 40)
        } else {
          data = await getMovies(page, 20, activeGenre, sortBy)
        }
        setMovies(data.movies)
        setTotalPages(data.pages)
      } catch (err) {
        console.error('[HomePage] Error:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchMovies()
  }, [page, activeGenre, sortBy, searchQuery])

  // Reset page on filter change
  useEffect(() => { setPage(1) }, [activeGenre, sortBy, searchQuery])

  const title = searchQuery
    ? `Resultados para "${searchQuery}"`
    : activeGenre
    ? genres.find(g => g.id === activeGenre)?.name || 'Películas'
    : 'Películas Populares'

  return (
    <div className="home">
      {/* Hero */}
      <motion.section className="home__hero" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
        <h1 className="home__hero-title">Descubre tu próxima<br/><span className="home__hero-accent">película favorita</span></h1>
        <p className="home__hero-subtitle">Explora el catálogo o pregúntale a nuestro asistente IA</p>
      </motion.section>

      {/* Filters */}
      {!searchQuery && (
        <div className="home__filters">
          <div className="home__genres">
            <button className={`home__genre-btn ${!activeGenre ? 'home__genre-btn--active' : ''}`} onClick={() => setActiveGenre(null)}>Todas</button>
            {genres.map(g => (
              <button key={g.id} className={`home__genre-btn ${activeGenre === g.id ? 'home__genre-btn--active' : ''}`} onClick={() => setActiveGenre(g.id)}>{g.name}</button>
            ))}
          </div>
          <select className="home__sort" value={sortBy} onChange={e => setSortBy(e.target.value)} id="sort-select">
            <option value="popularity">Más populares</option>
            <option value="vote_average">Mejor puntuadas</option>
            <option value="release_date">Más recientes</option>
          </select>
        </div>
      )}

      {/* Grid */}
      <MovieGrid movies={movies} loading={loading} title={title} />

      {/* Pagination */}
      {totalPages > 1 && !searchQuery && (
        <div className="home__pagination">
          <button className="home__page-btn" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Anterior</button>
          <span className="home__page-info">Página {page} de {totalPages}</span>
          <button className="home__page-btn" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>Siguiente →</button>
        </div>
      )}
    </div>
  )
}
