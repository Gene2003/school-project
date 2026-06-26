import { Link } from 'react-router-dom'

const FEATURES = [
  { icon: '🧑‍🌾', title: 'Direct from farmers', text: 'Buy produce straight from smallholder farmers and wholesalers — no middlemen eroding value.' },
  { icon: '💳', title: 'Secure payments', text: 'Pay securely with Paystack. Funds are split automatically to the right sellers.' },
  { icon: '🔔', title: 'Instant notifications', text: 'Order confirmations delivered by SMS (Africa\'s Talking) and email (SendGrid).' },
  { icon: '🤝', title: 'Referral rewards', text: 'Community promoters earn commission for every buyer they bring on board.' },
]

const ROLES = [
  { role: 'Farmers', text: 'List produce, set prices and manage stock.' },
  { role: 'Wholesalers', text: 'Supply in bulk and reach more retailers.' },
  { role: 'Retailers', text: 'Source fresh stock at competitive prices.' },
  { role: 'Consumers', text: 'Buy fresh produce directly and pay online.' },
]

export default function Home() {
  return (
    <div>
      <section className="hero">
        <div className="hero-content">
          <span className="pill">Kenya · Agricultural Supply Chain</span>
          <h1>One platform connecting the entire farm-to-table supply chain.</h1>
          <p>
            AgriChain links farmers, wholesalers, retailers and consumers in a single
            digital marketplace — with secure payments, automated commission tracking
            and real-time SMS & email notifications.
          </p>
          <div className="hero-actions">
            <Link to="/products" className="btn btn-primary btn-lg">Browse marketplace</Link>
            <Link to="/register" className="btn btn-ghost btn-lg">Create an account</Link>
          </div>
        </div>
        <div className="hero-art" aria-hidden="true">🌾🥕🍅🥬🍌</div>
      </section>

      <section className="section">
        <h2 className="section-title">Why AgriChain?</h2>
        <div className="feature-grid">
          {FEATURES.map((f) => (
            <div className="feature-card" key={f.title}>
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p className="muted">{f.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section section-alt">
        <h2 className="section-title">Built for every actor in the chain</h2>
        <div className="role-grid">
          {ROLES.map((r) => (
            <div className="role-card" key={r.role}>
              <h3>{r.role}</h3>
              <p className="muted">{r.text}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
