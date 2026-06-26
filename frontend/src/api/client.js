import axios from 'axios'

// Single axios instance. The Vite dev server proxies /api to Django.
const client = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

const ACCESS_KEY = 'agric_access'
const REFRESH_KEY = 'agric_refresh'

export const tokenStore = {
  get access() {
    return localStorage.getItem(ACCESS_KEY)
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY)
  },
  set({ access, refresh }) {
    if (access) localStorage.setItem(ACCESS_KEY, access)
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

// Attach the bearer token to every request.
client.interceptors.request.use((config) => {
  const token = tokenStore.access
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Transparently refresh an expired access token once, then retry.
let refreshing = null
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry && tokenStore.refresh) {
      original._retry = true
      try {
        refreshing =
          refreshing ||
          axios.post('/api/auth/refresh/', { refresh: tokenStore.refresh })
        const { data } = await refreshing
        refreshing = null
        tokenStore.set({ access: data.access })
        original.headers.Authorization = `Bearer ${data.access}`
        return client(original)
      } catch (e) {
        refreshing = null
        tokenStore.clear()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default client
