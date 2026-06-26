import { createContext, useContext, useEffect, useState } from 'react'
import { authApi } from '../api/services'
import { tokenStore } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Restore session on first load if a token is present.
  useEffect(() => {
    async function bootstrap() {
      if (tokenStore.access) {
        try {
          const { data } = await authApi.me()
          setUser(data)
        } catch {
          tokenStore.clear()
        }
      }
      setLoading(false)
    }
    bootstrap()
  }, [])

  async function login(email, password) {
    const { data } = await authApi.login({ email, password })
    tokenStore.set({ access: data.access, refresh: data.refresh })
    setUser(data.user)
    return data.user
  }

  async function register(payload) {
    await authApi.register(payload)
    return login(payload.email, payload.password)
  }

  function logout() {
    tokenStore.clear()
    setUser(null)
  }

  async function refreshUser() {
    const { data } = await authApi.me()
    setUser(data)
    return data
  }

  const value = { user, loading, login, register, logout, refreshUser, setUser }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
