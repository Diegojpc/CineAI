import { motion } from 'framer-motion'
import { Star } from 'lucide-react'
import { Link } from 'react-router-dom'
import { getPosterUrl } from '../services/api'
import './MovieCard.css'

export default function MovieCard({ movie, index = 0 }) {
  const posterUrl = getPosterUrl(movie.poster_path)
  const year = movie.release_date ? new Date(movie.release_date).getFullYear() : null

  return (
    <motion.div
      className="movie-card"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
      whileHover={{ y: -8 }}
    >
      <Link to={`/movie/${movie.id}`} className="movie-card__link" id={`movie-card-${movie.id}`}>
        {/* Poster */}
        <div className="movie-card__poster-wrapper">
          {posterUrl ? (
            <img
              src={posterUrl}
              alt={movie.title}
              className="movie-card__poster"
              loading="lazy"
            />
          ) : (
            <div className="movie-card__poster-placeholder">
              <span>🎬</span>
            </div>
          )}
          {/* Overlay */}
          <div className="movie-card__overlay">
            <span className="movie-card__view">Ver detalles</span>
          </div>
        </div>

        {/* Info */}
        <div className="movie-card__info">
          <h3 className="movie-card__title">{movie.title}</h3>
          <div className="movie-card__meta">
            {year && <span className="movie-card__year">{year}</span>}
            {movie.vote_average > 0 && (
              <span className="rating">
                <Star size={14} />
                {movie.vote_average.toFixed(1)}
              </span>
            )}
          </div>
          {movie.genres && movie.genres.length > 0 && (
            <div className="movie-card__genres">
              {movie.genres.slice(0, 2).map((genre) => (
                <span key={genre.id} className="badge">{genre.name}</span>
              ))}
            </div>
          )}
        </div>
      </Link>
    </motion.div>
  )
}
