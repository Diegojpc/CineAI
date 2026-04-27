import { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import ChatPanel from './components/ChatPanel'
import HomePage from './pages/HomePage'
import MoviePage from './pages/MoviePage'
import './App.css'

export default function App() {
  const [isChatOpen, setIsChatOpen] = useState(false)

  return (
    <div className="app">
      <div className="ambient-bg" />
      <Navbar onToggleChat={() => setIsChatOpen(!isChatOpen)} isChatOpen={isChatOpen} />
      <main className={`app__main container ${isChatOpen ? 'app__main--chat-open' : ''}`}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/movie/:id" element={<MoviePage />} />
        </Routes>
      </main>
      <ChatPanel isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
    </div>
  )
}
