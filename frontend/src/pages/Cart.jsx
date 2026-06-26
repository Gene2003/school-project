import { Link, useNavigate } from 'react-router-dom'
import { useCart } from '../context/CartContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'

export default function Cart() {
  const { items, updateQuantity, removeItem, total } = useCart()
  const { user } = useAuth()
  const navigate = useNavigate()

  if (items.length === 0) {
    return (
      <div className="section">
        <h1>Your cart</h1>
        <div className="empty">
          Your cart is empty. <Link to="/products">Browse the marketplace →</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="section">
      <h1>Your cart</h1>
      <div className="cart-layout">
        <div className="cart-items">
          {items.map(({ product, quantity }) => (
            <div className="cart-row" key={product.id}>
              <div className="cart-row-main">
                <Link to={`/products/${product.id}`} className="cart-name">{product.name}</Link>
                <span className="muted">
                  KES {Number(product.price).toLocaleString()} / {product.unit_display} · {product.seller_name}
                </span>
              </div>
              <input type="number" min={1} max={product.quantity_available}
                value={quantity}
                onChange={(e) =>
                  updateQuantity(product.id, Math.max(1, Math.min(Number(e.target.value), product.quantity_available)))
                }
              />
              <div className="cart-subtotal">
                KES {(Number(product.price) * quantity).toLocaleString()}
              </div>
              <button className="link-danger" onClick={() => removeItem(product.id)}>Remove</button>
            </div>
          ))}
        </div>

        <aside className="cart-summary">
          <h3>Order summary</h3>
          <div className="summary-row">
            <span>Total</span>
            <strong>KES {total.toLocaleString()}</strong>
          </div>
          <button className="btn btn-primary btn-block"
            onClick={() => navigate(user ? '/checkout' : '/login', { state: { from: { pathname: '/checkout' } } })}>
            {user ? 'Proceed to checkout' : 'Log in to checkout'}
          </button>
          <Link to="/products" className="muted center block">Continue shopping</Link>
        </aside>
      </div>
    </div>
  )
}
