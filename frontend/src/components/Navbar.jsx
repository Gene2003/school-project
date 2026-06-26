import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { useCart } from '../context/CartContext.jsx'

export default function Navbar() {
  const { user, logout } = useAuth()
  const { count } = useCart()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="brand">
          <span className="brand-mark">🌱</span>
          <span className="brand-text">AgriChain</span>
        </Link>

        <nav className="nav-links">
          <NavLink to="/products">Marketplace</NavLink>
          {user && <NavLink to="/orders">My Orders</NavLink>}
          {user && (user.role === 'farmer' || user.role === 'wholesaler') && (
            <NavLink to="/dashboard">Seller Dashboard</NavLink>
          )}
          {user && user.role === 'admin' && <NavLink to="/admin">Admin</NavLink>}
        </nav>

        <div className="nav-actions">
          <Link to="/cart" className="cart-link">
            🛒<span className="cart-count">{count}</span>
          </Link>
          {user ? (
            <div className="user-menu">
              <Link to="/profile" className="user-chip">
                {user.full_name || user.email}
                <span className="role-badge">{user.role}</span>
              </Link>
              <button className="btn btn-ghost" onClick={handleLogout}>
                Logout
              </button>
            </div>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost">Login</Link>
              <Link to="/register" className="btn btn-primary">Sign up</Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
