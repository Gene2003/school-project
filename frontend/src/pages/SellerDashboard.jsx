import { useEffect, useState } from 'react'
import { productApi, orderApi, commissionApi } from '../api/services'
import { useAuth } from '../context/AuthContext.jsx'

const UNITS = ['kg', 'bag', 'crate', 'piece', 'litre', 'bunch']
const EMPTY = { name: '', price: '', unit: 'kg', quantity_available: '', location: '', category: '', description: '' }

export default function SellerDashboard() {
  const { user } = useAuth()
  const [tab, setTab] = useState('products')
  const [products, setProducts] = useState([])
  const [sales, setSales] = useState([])
  const [categories, setCategories] = useState([])
  const [commissions, setCommissions] = useState({ summary: {}, results: [] })
  const [form, setForm] = useState(EMPTY)
  const [editingId, setEditingId] = useState(null)
  const [error, setError] = useState('')

  function loadProducts() {
    productApi.mine().then((r) => setProducts(r.data.results || r.data))
  }

  useEffect(() => {
    loadProducts()
    orderApi.sales().then((r) => setSales(r.data)).catch(() => {})
    productApi.categories().then((r) => setCategories(r.data.results || r.data)).catch(() => {})
    commissionApi.list().then((r) => setCommissions(r.data)).catch(() => {})
  }, [])

  function update(key) {
    return (e) => setForm({ ...form, [key]: e.target.value })
  }

  function startEdit(p) {
    setEditingId(p.id)
    setForm({
      name: p.name, price: p.price, unit: p.unit,
      quantity_available: p.quantity_available, location: p.location || '',
      category: p.category || '', description: p.description || '',
    })
    setTab('add')
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    const payload = {
      ...form,
      price: Number(form.price),
      quantity_available: Number(form.quantity_available),
      category: form.category || null,
    }
    try {
      if (editingId) await productApi.update(editingId, payload)
      else await productApi.create(payload)
      setForm(EMPTY)
      setEditingId(null)
      setTab('products')
      loadProducts()
    } catch (err) {
      const data = err.response?.data
      setError(data ? Object.entries(data).map(([k, v]) => `${k}: ${v}`).join(' ') : 'Could not save product.')
    }
  }

  async function remove(id) {
    if (!confirm('Delete this listing?')) return
    await productApi.remove(id)
    loadProducts()
  }

  return (
    <div className="section">
      <div className="page-head">
        <div>
          <h1>Seller Dashboard</h1>
          <p className="muted">Welcome, {user.full_name}. Manage your listings and track sales.</p>
        </div>
        <button className="btn btn-primary" onClick={() => { setForm(EMPTY); setEditingId(null); setTab('add') }}>
          + New listing
        </button>
      </div>

      <div className="stat-row">
        <Stat label="My listings" value={products.length} />
        <Stat label="Items sold" value={sales.reduce((s, i) => s + i.quantity, 0)} />
        <Stat label="Sales revenue" value={`KES ${sales.reduce((s, i) => s + Number(i.subtotal), 0).toLocaleString()}`} />
        <Stat label="Platform fees" value={`KES ${Number(commissions.summary?.platform_fees || 0).toLocaleString()}`} />
      </div>

      <div className="tabs">
        <button className={tab === 'products' ? 'active' : ''} onClick={() => setTab('products')}>My Products</button>
        <button className={tab === 'sales' ? 'active' : ''} onClick={() => setTab('sales')}>Incoming Sales</button>
        <button className={tab === 'add' ? 'active' : ''} onClick={() => setTab('add')}>
          {editingId ? 'Edit Listing' : 'Add Listing'}
        </button>
      </div>

      {tab === 'products' && (
        <table className="table">
          <thead>
            <tr><th>Product</th><th>Price</th><th>Stock</th><th>Status</th><th></th></tr>
          </thead>
          <tbody>
            {products.length === 0 && <tr><td colSpan="5" className="muted center">No listings yet.</td></tr>}
            {products.map((p) => (
              <tr key={p.id}>
                <td>{p.name}</td>
                <td>KES {Number(p.price).toLocaleString()} / {p.unit_display}</td>
                <td>{p.quantity_available}</td>
                <td>{p.is_active ? <span className="badge badge-paid">Active</span> : <span className="badge badge-out">Hidden</span>}</td>
                <td className="row-actions">
                  <button className="link" onClick={() => startEdit(p)}>Edit</button>
                  <button className="link-danger" onClick={() => remove(p.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {tab === 'sales' && (
        <table className="table">
          <thead>
            <tr><th>Product</th><th>Qty</th><th>Unit price</th><th>Subtotal</th></tr>
          </thead>
          <tbody>
            {sales.length === 0 && <tr><td colSpan="4" className="muted center">No sales yet.</td></tr>}
            {sales.map((s) => (
              <tr key={s.id}>
                <td>{s.product_name}</td>
                <td>{s.quantity}</td>
                <td>KES {Number(s.unit_price).toLocaleString()}</td>
                <td>KES {Number(s.subtotal).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {tab === 'add' && (
        <form className="card-form" onSubmit={handleSubmit}>
          {error && <div className="alert alert-error">{error}</div>}
          <div className="grid-2">
            <label>Product name<input required value={form.name} onChange={update('name')} /></label>
            <label>Category
              <select value={form.category} onChange={update('category')}>
                <option value="">— none —</option>
                {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </label>
            <label>Price (KES)<input type="number" min="0" step="0.01" required value={form.price} onChange={update('price')} /></label>
            <label>Unit
              <select value={form.unit} onChange={update('unit')}>
                {UNITS.map((u) => <option key={u} value={u}>{u}</option>)}
              </select>
            </label>
            <label>Quantity available<input type="number" min="0" required value={form.quantity_available} onChange={update('quantity_available')} /></label>
            <label>Location<input value={form.location} onChange={update('location')} /></label>
            <label className="span-2">Description<textarea rows="3" value={form.description} onChange={update('description')} /></label>
          </div>
          <button className="btn btn-primary">{editingId ? 'Update listing' : 'Publish listing'}</button>
        </form>
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
