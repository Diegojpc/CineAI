import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, Star, Calendar, Globe, TrendingUp } from 'lucide-react'
import { getMovie, getPosterUrl, getBackdropUrl } from '../services/api'
import Loader from './Loader'
import './MovieDetail.css'

export default function MovieDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [movie, setMovie] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchMovie = async () => {
      setLoading(true)
      try {
        const data = await getMovie(id)
        setMovie(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchMovie()
  }, [id])

  if (loading) return <div className="movie-detail__loading"><Loader size="lg" /></div>
  if (error || !movie) return (
    <div className="movie-detail__error">
      <p>Película no encontrada</p>
      <button onClick={() => navigate('/')} className="movie-detail__back-btn">Volver</button>
    </div>
  )

  const backdropUrl = getBackdropUrl(movie.backdrop_path)
  const posterUrl = getPosterUrl(movie.poster_path)
  const year = movie.release_date ? new Date(movie.release_date).getFullYear() : null

  return (
    <motion.div className="movie-detail" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      {backdropUrl && (
        <div className="movie-detail__backdrop">
          <img src={backdropUrl} alt="" className="movie-detail__backdrop-img" />
          <div className="movie-detail__backdrop-overlay" />
        </div>
      )}
      <div className="movie-detail__content container">
        <button onClick={() => navigate(-1)} className="movie-detail__back" id="movie-detail-back">
          <ArrowLeft size={20} /><span>Volver</span>
        </button>
        <div className="movie-detail__layout">
          <motion.div className="movie-detail__poster-col" initial={{ x: -30, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.2 }}>
            {posterUrl ? <img src={posterUrl} alt={movie.title} className="movie-detail__poster" /> : <div className="movie-detail__poster-placeholder">🎬</div>}
          </motion.div>
          <motion.div className="movie-detail__info-col" initial={{ x: 30, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.3 }}>
            <h1 className="movie-detail__title">{movie.title}</h1>
            {movie.original_title && movie.original_title !== movie.title && <p className="movie-detail__original-title">{movie.original_title}</p>}
            <div className="movie-detail__meta">
              {movie.vote_average > 0 && <div className="movie-detail__meta-item rating"><Star size={18} /><span>{movie.vote_average.toFixed(1)}</span><span className="movie-detail__meta-label">/ 10</span></div>}
              {year && <div className="movie-detail__meta-item"><Calendar size={16} /><span>{year}</span></div>}
              {movie.original_language && <div className="movie-detail__meta-item"><Globe size={16} /><span>{movie.original_language.toUpperCase()}</span></div>}
              {movie.popularity > 0 && <div className="movie-detail__meta-item"><TrendingUp size={16} /><span>{Math.round(movie.popularity)}</span></div>}
            </div>
            {movie.genres?.length > 0 && <div className="movie-detail__genres">{movie.genres.map(g => <span key={g.id} className="badge badge--accent">{g.name}</span>)}</div>}
            {movie.overview && <div className="movie-detail__synopsis"><h2 className="movie-detail__section-title">Sinopsis</h2><p className="movie-detail__overview">{movie.overview}</p></div>}
          </motion.div>
        </div>
      </div>
    </motion.div>
  )
}
