import MovieCard from './MovieCard'
import Loader from './Loader'
import './MovieGrid.css'

export default function MovieGrid({ movies, loading, title }) {
  if (loading) {
    return (
      <div className="movie-grid__loading">
        <Loader />
      </div>
    )
  }

  if (!movies || movies.length === 0) {
    return (
      <div className="movie-grid__empty">
        <span className="movie-grid__empty-icon">🎬</span>
        <p>No se encontraron películas</p>
      </div>
    )
  }

  return (
    <section className="movie-grid">
      {title && <h2 className="movie-grid__title">{title}</h2>}
      <div className="movie-grid__grid">
        {movies.map((movie, index) => (
          <MovieCard key={movie.id} movie={movie} index={index} />
        ))}
      </div>
    </section>
  )
}
