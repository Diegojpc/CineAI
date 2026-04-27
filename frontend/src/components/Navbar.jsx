import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Film, Search, MessageCircle, X } from 'lucide-react'
import './Navbar.css'

export default function Navbar({ onToggleChat, isChatOpen }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const navigate = useNavigate()

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/?search=${encodeURIComponent(searchQuery.trim())}`)
      setIsSearchOpen(false)
    }
  }

  return (
    <motion.nav
      className="navbar glass-strong"
      initial={{ y: -80 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      <div className="navbar__inner container">
        {/* Logo */}
        <Link to="/" className="navbar__logo">
          <Film className="navbar__logo-icon" />
          <span className="navbar__logo-text">
            Cine<span className="navbar__logo-accent">AI</span>
          </span>
        </Link>

        {/* Actions */}
        <div className="navbar__actions">
          {/* Search */}
          <div className={`navbar__search ${isSearchOpen ? 'navbar__search--open' : ''}`}>
            {isSearchOpen ? (
              <form onSubmit={handleSearch} className="navbar__search-form">
                <Search size={18} className="navbar__search-icon" />
                <input
                  type="text"
                  placeholder="Buscar películas..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  autoFocus
                  className="navbar__search-input"
                  id="navbar-search-input"
                />
                <button
                  type="button"
                  onClick={() => { setIsSearchOpen(false); setSearchQuery('') }}
                  className="navbar__search-close"
                  aria-label="Cerrar búsqueda"
                >
                  <X size={18} />
                </button>
              </form>
            ) : (
              <button
                onClick={() => setIsSearchOpen(true)}
                className="navbar__btn"
                aria-label="Abrir búsqueda"
                id="navbar-search-btn"
              >
                <Search size={20} />
              </button>
            )}
          </div>

          {/* Chat toggle */}
          <button
            onClick={onToggleChat}
            className={`navbar__btn navbar__btn--chat ${isChatOpen ? 'navbar__btn--active' : ''}`}
            aria-label="Abrir asistente IA"
            id="navbar-chat-btn"
          >
            <MessageCircle size={20} />
            <span className="navbar__btn-label">Asistente IA</span>
          </button>
        </div>
      </div>
    </motion.nav>
  )
}
