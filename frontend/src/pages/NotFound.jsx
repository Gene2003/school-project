import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="section empty">
      <h1>404</h1>
      <p className="muted">The page you’re looking for doesn’t exist.</p>
      <Link to="/" className="btn btn-primary">Back home</Link>
    </div>
  )
}
