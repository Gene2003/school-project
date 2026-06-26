import { useEffect, useState } from 'react'
import { authApi, commissionApi } from '../api/services'

const ROLES = ['farmer', 'wholesaler', 'retailer', 'consumer', 'admin']

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [commissions, setCommissions] = useState({ summary: {}, results: [] })
  const [tab, setTab] = useState('overview')

  function loadUsers() {
    authApi.users().then((r) => setUsers(r.data.results || r.data)).catch(() => {})
  }

  useEffect(() => {
    authApi.stats().then((r) => setStats(r.data)).catch(() => {})
    loadUsers()
    commissionApi.list().then((r) => setCommissions(r.data)).catch(() => {})
  }, [])

  async function changeRole(id, role) {
    await authApi.updateUser(id, { role })
    loadUsers()
  }

  async function removeUser(id) {
    if (!confirm('Delete this account permanently?')) return
    await authApi.deleteUser(id)
    loadUsers()
  }

  return (
    <div className="section">
      <h1>Admin Dashboard</h1>
      <p className="muted">Monitor platform activity, manage accounts and review commissions.</p>

      <div className="stat-row">
        <Stat label="Total users" value={stats?.users_total ?? '—'} />
        <Stat label="Products" value={stats?.products_total ?? '—'} />
        <Stat label="Orders" value={stats?.orders_total ?? '—'} />
        <Stat label="Paid orders" value={stats?.orders_paid ?? '—'} />
        <Stat label="Platform fees" value={`KES ${Number(commissions.summary?.platform_fees || 0).toLocaleString()}`} />
      </div>

      <div className="tabs">
        <button className={tab === 'overview' ? 'active' : ''} onClick={() => setTab('overview')}>Users by role</button>
        <button className={tab === 'users' ? 'active' : ''} onClick={() => setTab('users')}>Manage users</button>
        <button className={tab === 'commissions' ? 'active' : ''} onClick={() => setTab('commissions')}>Commissions</button>
      </div>

      {tab === 'overview' && stats && (
        <div className="role-grid">
          {Object.entries(stats.users_by_role).map(([role, count]) => (
            <div className="role-card" key={role}>
              <h3 style={{ textTransform: 'capitalize' }}>{role}s</h3>
              <div className="stat-value">{count}</div>
            </div>
          ))}
        </div>
      )}

      {tab === 'users' && (
        <table className="table">
          <thead>
            <tr><th>Name</th><th>Email</th><th>Role</th><th>Location</th><th>Referrals</th><th></th></tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.full_name || '—'}</td>
                <td>{u.email}</td>
                <td>
                  <select value={u.role} onChange={(e) => changeRole(u.id, e.target.value)}>
                    {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
                  </select>
                </td>
                <td>{u.location || '—'}</td>
                <td>{u.referrals_count}</td>
                <td><button className="link-danger" onClick={() => removeUser(u.id)}>Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {tab === 'commissions' && (
        <table className="table">
          <thead>
            <tr><th>Order</th><th>Type</th><th>Beneficiary</th><th>Rate</th><th>Base</th><th>Amount</th></tr>
          </thead>
          <tbody>
            {commissions.results.length === 0 && <tr><td colSpan="6" className="muted center">No commissions recorded yet.</td></tr>}
            {commissions.results.map((c) => (
              <tr key={c.id}>
                <td>#{String(c.order_reference).slice(0, 8)}</td>
                <td>{c.kind_display}</td>
                <td>{c.beneficiary_name || '—'}</td>
                <td>{c.rate_percent}%</td>
                <td>KES {Number(c.base_amount).toLocaleString()}</td>
                <td>KES {Number(c.amount).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="stat">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}
