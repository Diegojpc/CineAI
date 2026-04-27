import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Send, Sparkles, Trash2 } from 'lucide-react'
import { sendChatMessage } from '../services/api'
import ChatMessage from './ChatMessage'
import './ChatPanel.css'

export default function ChatPanel({ isOpen, onClose }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '¡Hola! 🎬 Soy CineAI, tu asistente cinéfilo. Cuéntame qué tipo de película buscas: un género, un estado de ánimo, o algo parecido a una película que te haya gustado. ¡Te ayudo a encontrar tu próxima favorita!',
      movies: [],
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Auto-scroll al último mensaje
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus input cuando se abre el panel
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 300)
    }
  }, [isOpen])

  const handleSend = async () => {
    const trimmed = input.trim()
    if (!trimmed || isLoading) return

    console.info('[ChatPanel] Sending message:', trimmed)

    // Agregar mensaje del usuario
    const userMessage = { role: 'user', content: trimmed, movies: [] }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Construir historial (excluir el greeting inicial)
      const history = messages
        .filter((_, i) => i > 0)
        .map((m) => ({ role: m.role, content: m.content }))

      const data = await sendChatMessage(trimmed, history)

      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        movies: data.recommended_movies || [],
      }

      setMessages((prev) => [...prev, assistantMessage])
      console.info('[ChatPanel] Received response with', data.recommended_movies?.length || 0, 'recommendations')
    } catch (error) {
      console.error('[ChatPanel] Chat error:', error)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Lo siento, hubo un error al procesar tu mensaje. Intenta de nuevo.',
          movies: [],
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleClear = () => {
    setMessages([
      {
        role: 'assistant',
        content: '¡Chat reiniciado! 🎬 ¿Qué película buscamos ahora?',
        movies: [],
      },
    ])
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop para mobile */}
          <motion.div
            className="chat-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            className="chat-panel glass-strong"
            initial={{ x: '100%', opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: '100%', opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          >
            {/* Header */}
            <div className="chat-panel__header">
              <div className="chat-panel__header-info">
                <Sparkles size={18} className="chat-panel__header-icon" />
                <div>
                  <h3 className="chat-panel__title">CineAI</h3>
                  <p className="chat-panel__subtitle">Asistente de recomendaciones</p>
                </div>
              </div>
              <div className="chat-panel__header-actions">
                <button onClick={handleClear} className="chat-panel__btn" aria-label="Limpiar chat" id="chat-clear-btn">
                  <Trash2 size={16} />
                </button>
                <button onClick={onClose} className="chat-panel__btn" aria-label="Cerrar chat" id="chat-close-btn">
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="chat-panel__messages" id="chat-messages">
              {messages.map((msg, i) => (
                <ChatMessage key={i} message={msg} />
              ))}

              {isLoading && (
                <div className="chat-panel__typing">
                  <div className="chat-msg__avatar"><span>🤖</span></div>
                  <div className="chat-panel__typing-dots">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="chat-panel__input-area">
              <div className="chat-panel__input-wrapper">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Describe qué película buscas..."
                  rows={1}
                  className="chat-panel__input"
                  disabled={isLoading}
                  id="chat-input"
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  className="chat-panel__send"
                  aria-label="Enviar mensaje"
                  id="chat-send-btn"
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
