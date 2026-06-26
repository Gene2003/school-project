import { Link } from 'react-router-dom'
import { useCart } from '../context/CartContext.jsx'

const PLACEHOLDER =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="260">
      <rect width="100%" height="100%" fill="#e8f3ea"/>
      <text x="50%" y="50%" font-size="64" text-anchor="middle" dominant-baseline="middle">🥬</text>
    </svg>`
  )

export default function ProductCard({ product }) {
  const { addItem } = useCart()

  return (
    <div className="product-card">
      <Link to={`/products/${product.id}`} className="product-image">
        <img src={product.image || PLACEHOLDER} alt={product.name} />
        {!product.in_stock && <span className="badge badge-out">Out of stock</span>}
      </Link>
      <div className="product-body">
        <Link to={`/products/${product.id}`} className="product-name">
          {product.name}
        </Link>
        <div className="product-meta">
          <span className="price">KES {Number(product.price).toLocaleString()}</span>
          <span className="muted">/ {product.unit_display}</span>
        </div>
        <div className="product-seller muted">
          {product.seller_name} · {product.location || '—'}
        </div>
        <button
          className="btn btn-primary btn-block"
          disabled={!product.in_stock}
          onClick={() => addItem(product, 1)}
        >
          {product.in_stock ? 'Add to cart' : 'Unavailable'}
        </button>
      </div>
    </div>
  )
}
