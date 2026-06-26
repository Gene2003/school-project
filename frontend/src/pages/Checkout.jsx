import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../context/CartContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { orderApi, paymentApi } from '../api/services'

export default function Checkout() {
  const { items, total, clear } = useCart()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    phone_number: user?.phone_number || '',
    delivery_address: user?.location || '',
  })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  function update(key) {
    return (e) => setForm({ ...form, [key]: e.target.value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      // 1. Create the order with snapshot line items.
      const { data: order } = await orderApi.checkout({
        ...form,
        items: items.map((i) => ({ product: i.product.id, quantity: i.quantity })),
      })
      // 2. Initialize payment (Paystack, or simulation).
      const { data: payment } = await paymentApi.initialize(order.id)
      clear()

      if (payment.simulated) {
        navigate(`/pay/simulate?reference=${payment.reference}`)
      } else {
        // Live Paystack hosted checkout.
        window.location.href = payment.authorization_url
      }
    } catch (err) {
      const data = err.response?.data
      setError(
        data?.detail ||
          (data ? Object.values(data).flat().join(' ') : 'Checkout failed. Please try again.')
      )
      setBusy(false)
    }
  }

  if (items.length === 0) {
    return <div className="section empty">Your cart is empty.</div>
  }

  return (
    <div className="section">
      <h1>Checkout</h1>
      <div className="checkout-layout">
        <form className="checkout-form" onSubmit={handleSubmit}>
          <h3>Delivery & contact details</h3>
          {error && <div className="alert alert-error">{error}</div>}
          <label>Full name
            <input required value={form.full_name} onChange={update('full_name')} />
          </label>
          <label>Email (for confirmation)
            <input type="email" required value={form.email} onChange={update('email')} />
          </label>
          <label>Phone (for SMS confirmation)
            <input value={form.phone_number} onChange={update('phone_number')} placeholder="07XXXXXXXX" />
          </label>
          <label>Delivery address
            <input value={form.delivery_address} onChange={update('delivery_address')} />
          </label>
          <button className="btn btn-primary btn-block" disabled={busy}>
            {busy ? 'Processing…' : `Pay KES ${total.toLocaleString()}`}
          </button>
        </form>

        <aside className="cart-summary">
          <h3>Order summary</h3>
          {items.map(({ product, quantity }) => (
            <div className="summary-row" key={product.id}>
              <span>{quantity} × {product.name}</span>
              <span>KES {(Number(product.price) * quantity).toLocaleString()}</span>
            </div>
          ))}
          <hr />
          <div className="summary-row">
            <span>Total</span>
            <strong>KES {total.toLocaleString()}</strong>
          </div>
        </aside>
      </div>
    </div>
  )
}
