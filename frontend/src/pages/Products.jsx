import { useEffect, useState } from 'react'
import { productApi } from '../api/services'
import ProductCard from '../components/ProductCard.jsx'

export default function Products() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [filters, setFilters] = useState({ search: '', category: '', ordering: '' })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    productApi.categories().then((r) => setCategories(r.data.results || r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    const params = {}
    if (filters.search) params.search = filters.search
    if (filters.category) params.category = filters.category
    if (filters.ordering) params.ordering = filters.ordering
    const t = setTimeout(() => {
      productApi.list(params)
        .then((r) => setProducts(r.data.results || r.data))
        .finally(() => setLoading(false))
    }, 250)
    return () => clearTimeout(t)
  }, [filters])

  return (
    <div className="section">
      <div className="page-head">
        <div>
          <h1>Marketplace</h1>
          <p className="muted">Fresh produce direct from farmers and wholesalers.</p>
        </div>
      </div>

      <div className="filters">
        <input
          placeholder="Search produce, location…"
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
        />
        <select value={filters.category}
          onChange={(e) => setFilters({ ...filters, category: e.target.value })}>
          <option value="">All categories</option>
          {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select value={filters.ordering}
          onChange={(e) => setFilters({ ...filters, ordering: e.target.value })}>
          <option value="">Newest first</option>
          <option value="price">Price: low to high</option>
          <option value="-price">Price: high to low</option>
        </select>
      </div>

      {loading ? (
        <div className="muted center pad">Loading produce…</div>
      ) : products.length === 0 ? (
        <div className="empty">No products match your search.</div>
      ) : (
        <div className="product-grid">
          {products.map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
      )}
    </div>
  )
}
