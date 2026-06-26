import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { orderApi } from '../api/services'

const STATUS_CLASS = {
  paid: 'badge-paid',
  pending: 'badge-pending',
  fulfilled: 'badge-paid',
  cancelled: 'badge-out',
}

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [params] = useSearchParams()
  const justPaid = params.get('paid')

  useEffect(() => {
    orderApi.list()
      .then((r) => setOrders(r.data.results || r.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="section muted center pad">Loading orders…</div>

  return (
    <div className="section">
      <h1>My Orders</h1>
      {justPaid && (
        <div className="alert alert-success">
          🎉 Payment received! A confirmation has been sent by SMS and email.
        </div>
      )}

      {orders.length === 0 ? (
        <div className="empty">
          You have no orders yet. <Link to="/products">Start shopping →</Link>
        </div>
      ) : (
        <div className="order-list">
          {orders.map((o) => (
            <div className="order-card" key={o.id}>
              <div className="order-head">
                <div>
                  <strong>Order #{String(o.reference).slice(0, 8)}</strong>
                  <span className="muted"> · {new Date(o.created_at).toLocaleString()}</span>
                </div>
                <span className={`badge ${STATUS_CLASS[o.status] || ''}`}>{o.status_display}</span>
              </div>
              <ul className="order-items">
                {o.items.map((i) => (
                  <li key={i.id}>
                    {i.quantity} × {i.product_name}
                    <span className="muted"> — {i.seller_name}</span>
                    <span className="order-item-price">KES {Number(i.subtotal).toLocaleString()}</span>
                  </li>
                ))}
              </ul>
              <div className="order-foot">
                <span className="muted">{o.delivery_address}</span>
                <strong>Total: KES {Number(o.total_amount).toLocaleString()}</strong>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
