import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { productApi } from '../api/services'
import { useCart } from '../context/CartContext.jsx'

const PLACEHOLDER =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="420">
      <rect width="100%" height="100%" fill="#e8f3ea"/>
      <text x="50%" y="50%" font-size="120" text-anchor="middle" dominant-baseline="middle">🥬</text>
    </svg>`
  )

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { addItem } = useCart()
  const [product, setProduct] = useState(null)
  const [qty, setQty] = useState(1)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    productApi.get(id)
      .then((r) => setProduct(r.data))
      .catch(() => setNotFound(true))
  }, [id])

  if (notFound) return <div className="section empty">Product not found.</div>
  if (!product) return <div className="section muted center pad">Loading…</div>

  return (
    <div className="section detail">
      <Link to="/products" className="back-link">← Back to marketplace</Link>
      <div className="detail-grid">
        <div className="detail-image">
          <img src={product.image || PLACEHOLDER} alt={product.name} />
        </div>
        <div className="detail-info">
          <h1>{product.name}</h1>
          <div className="detail-price">
            KES {Number(product.price).toLocaleString()}
            <span className="muted"> / {product.unit_display}</span>
          </div>
          <p>{product.description || 'No description provided.'}</p>
          <ul className="detail-meta">
            <li><strong>Seller:</strong> {product.seller_name} ({product.seller_role})</li>
            <li><strong>Location:</strong> {product.location || '—'}</li>
            <li><strong>Category:</strong> {product.category_name || '—'}</li>
            <li><strong>In stock:</strong> {product.quantity_available} {product.unit_display}(s)</li>
          </ul>

          {product.in_stock ? (
            <div className="detail-actions">
              <input type="number" min={1} max={product.quantity_available}
                value={qty}
                onChange={(e) => setQty(Math.max(1, Math.min(Number(e.target.value), product.quantity_available)))}
              />
              <button className="btn btn-primary"
                onClick={() => { addItem(product, qty); navigate('/cart') }}>
                Add to cart
              </button>
            </div>
          ) : (
            <div className="alert alert-error">This item is currently out of stock.</div>
          )}
        </div>
      </div>
    </div>
  )
}
