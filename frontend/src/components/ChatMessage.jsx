import { getPosterUrl } from '../services/api'
import './ChatMessage.css'

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`chat-msg ${isUser ? 'chat-msg--user' : 'chat-msg--assistant'}`}>
      {!isUser && (
        <div className="chat-msg__avatar">
          <span>🤖</span>
        </div>
      )}
      <div className="chat-msg__content">
        <div className="chat-msg__bubble">
          <p className="chat-msg__text">{message.content}</p>
        </div>

        {/* Películas recomendadas inline */}
        {message.movies && message.movies.length > 0 && (
          <div className="chat-msg__movies">
            {message.movies.map((movie) => (
              <a
                key={movie.id}
                href={`/movie/${movie.id}`}
                className="chat-msg__movie-chip"
              >
                {getPosterUrl(movie.poster_path, 'w92') ? (
                  <img
                    src={getPosterUrl(movie.poster_path, 'w92')}
                    alt={movie.title}
                    className="chat-msg__movie-poster"
                  />
                ) : (
                  <div className="chat-msg__movie-poster-empty">🎬</div>
                )}
                <div className="chat-msg__movie-info">
                  <span className="chat-msg__movie-title">{movie.title}</span>
                  {movie.vote_average > 0 && (
                    <span className="chat-msg__movie-rating">⭐ {movie.vote_average.toFixed(1)}</span>
                  )}
                </div>
              </a>
            ))}
          </div>
        )}
      </div>
      {isUser && (
        <div className="chat-msg__avatar chat-msg__avatar--user">
          <span>👤</span>
        </div>
      )}
    </div>
  )
}
