import './Loader.css'

export default function Loader({ size = 'md', text = 'Cargando...' }) {
  return (
    <div className={`loader loader--${size}`}>
      <div className="loader__spinner">
        <div className="loader__ring"></div>
        <div className="loader__ring"></div>
        <div className="loader__ring"></div>
      </div>
      {text && <p className="loader__text">{text}</p>}
    </div>
  )
}
