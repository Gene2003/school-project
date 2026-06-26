import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      const user = await login(form.email, form.password)
      const dest = location.state?.from?.pathname
      if (dest) navigate(dest)
      else if (user.role === 'admin') navigate('/admin')
      else if (user.is_seller) navigate('/dashboard')
      else navigate('/products')
    } catch {
      setError('Invalid email or password. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-wrap">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Welcome back</h1>
        <p className="muted">Log in to your AgriChain account.</p>
        {error && <div className="alert alert-error">{error}</div>}

        <label>Email
          <input type="email" required value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            placeholder="you@example.com" />
        </label>
        <label>Password
          <input type="password" required value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            placeholder="••••••••" />
        </label>

        <button className="btn btn-primary btn-block" disabled={busy}>
          {busy ? 'Logging in…' : 'Log in'}
        </button>
        <p className="muted center">
          No account? <Link to="/register">Sign up</Link>
        </p>
        <div className="demo-hint">
          <strong>Demo accounts</strong> (password <code>Password123</code>):<br />
          farmer@agric.co.ke · consumer@agric.co.ke · admin@agric.co.ke
        </div>
      </form>
    </div>
  )
}
