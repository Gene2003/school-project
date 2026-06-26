import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

const ROLES = [
  { value: 'consumer', label: 'Consumer — buy produce' },
  { value: 'farmer', label: 'Farmer — sell my produce' },
  { value: 'wholesaler', label: 'Wholesaler — supply in bulk' },
  { value: 'retailer', label: 'Retailer — resell produce' },
]

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    full_name: '', email: '', password: '', role: 'consumer',
    phone_number: '', location: '', referral_code: '',
  })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [searchParams] = useSearchParams()

  // Pre-fill referral code when arriving via a promoter's share link.
  useEffect(() => {
    const ref = searchParams.get('ref')
    if (ref) setForm((f) => ({ ...f, referral_code: ref }))
  }, [searchParams])

  function update(key) {
    return (e) => setForm({ ...form, [key]: e.target.value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      const user = await register(form)
      if (user.is_seller) navigate('/dashboard')
      else navigate('/products')
    } catch (err) {
      const data = err.response?.data
      const msg = data
        ? Object.entries(data).map(([k, v]) => `${k}: ${v}`).join(' ')
        : 'Registration failed. Please check your details.'
      setError(msg)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-wrap">
      <form className="auth-card wide" onSubmit={handleSubmit}>
        <h1>Create your account</h1>
        <p className="muted">Join the agricultural marketplace.</p>
        {error && <div className="alert alert-error">{error}</div>}

        <div className="grid-2">
          <label>Full name
            <input required value={form.full_name} onChange={update('full_name')} />
          </label>
          <label>Email
            <input type="email" required value={form.email} onChange={update('email')} />
          </label>
          <label>Password
            <input type="password" required minLength={8}
              value={form.password} onChange={update('password')} />
          </label>
          <label>I am a…
            <select value={form.role} onChange={update('role')}>
              {ROLES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
            </select>
          </label>
          <label>Phone number
            <input value={form.phone_number} onChange={update('phone_number')}
              placeholder="07XXXXXXXX" />
          </label>
          <label>Location
            <input value={form.location} onChange={update('location')}
              placeholder="Town / County" />
          </label>
          <label className="span-2">Referral code (optional)
            <input value={form.referral_code} onChange={update('referral_code')}
              placeholder="Code from a promoter who invited you" />
          </label>
        </div>

        <button className="btn btn-primary btn-block" disabled={busy}>
          {busy ? 'Creating account…' : 'Sign up'}
        </button>
        <p className="muted center">
          Already registered? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  )
}
