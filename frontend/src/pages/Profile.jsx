import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { authApi, commissionApi, notificationApi } from '../api/services'

export default function Profile() {
  const { user, refreshUser } = useAuth()
  const [form, setForm] = useState({
    full_name: user.full_name || '', phone_number: user.phone_number || '', location: user.location || '',
  })
  const [saved, setSaved] = useState(false)
  const [commissions, setCommissions] = useState({ summary: {}, results: [] })
  const [notifications, setNotifications] = useState([])

  useEffect(() => {
    commissionApi.list().then((r) => setCommissions(r.data)).catch(() => {})
    notificationApi.list().then((r) => setNotifications(r.data.results || r.data)).catch(() => {})
  }, [])

  function update(key) {
    return (e) => setForm({ ...form, [key]: e.target.value })
  }

  async function save(e) {
    e.preventDefault()
    await authApi.updateMe(form)
    await refreshUser()
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  const referralLink = `${window.location.origin}/register?ref=${user.referral_code}`

  return (
    <div className="section">
      <h1>My Profile</h1>

      <div className="profile-layout">
        <form className="card-form" onSubmit={save}>
          <h3>Account details</h3>
          {saved && <div className="alert alert-success">Profile updated.</div>}
          <label>Full name<input value={form.full_name} onChange={update('full_name')} /></label>
          <label>Email<input value={user.email} disabled /></label>
          <label>Role<input value={user.role} disabled /></label>
          <label>Phone number<input value={form.phone_number} onChange={update('phone_number')} /></label>
          <label>Location<input value={form.location} onChange={update('location')} /></label>
          <button className="btn btn-primary">Save changes</button>
        </form>

        <aside className="profile-side">
          <div className="card">
            <h3>Refer & earn</h3>
            <p className="muted">
              Share your referral code. You earn commission when people you invite buy on the platform.
            </p>
            <div className="referral-code">{user.referral_code}</div>
            <button className="btn btn-ghost btn-block"
              onClick={() => { navigator.clipboard?.writeText(referralLink); }}>
              Copy referral link
            </button>
            <div className="summary-row" style={{ marginTop: 12 }}>
              <span>Referrals</span><strong>{user.referrals_count ?? 0}</strong>
            </div>
            <div className="summary-row">
              <span>Referral earnings</span>
              <strong>KES {Number(commissions.summary?.total_earned || 0).toLocaleString()}</strong>
            </div>
          </div>

          <div className="card">
            <h3>Recent notifications</h3>
            {notifications.length === 0 ? (
              <p className="muted">No notifications yet.</p>
            ) : (
              <ul className="notif-list">
                {notifications.slice(0, 6).map((n) => (
                  <li key={n.id}>
                    <span className={`chip chip-${n.channel}`}>{n.channel}</span>
                    {n.subject || n.message.slice(0, 48)}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}
