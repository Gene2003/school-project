import client from './client'

// Grouped API service calls, mirroring the backend apps.

export const authApi = {
  register: (payload) => client.post('/auth/register/', payload),
  login: (payload) => client.post('/auth/login/', payload),
  me: () => client.get('/auth/me/'),
  updateMe: (payload) => client.patch('/auth/me/', payload),
  stats: () => client.get('/auth/stats/'),
  users: (params) => client.get('/auth/users/', { params }),
  updateUser: (id, payload) => client.patch(`/auth/users/${id}/`, payload),
  deleteUser: (id) => client.delete(`/auth/users/${id}/`),
}

export const productApi = {
  list: (params) => client.get('/products/', { params }),
  mine: () => client.get('/products/', { params: { mine: 1 } }),
  get: (id) => client.get(`/products/${id}/`),
  create: (payload) => client.post('/products/', payload),
  update: (id, payload) => client.patch(`/products/${id}/`, payload),
  remove: (id) => client.delete(`/products/${id}/`),
  categories: () => client.get('/products/categories/'),
}

export const orderApi = {
  list: () => client.get('/orders/'),
  get: (id) => client.get(`/orders/${id}/`),
  checkout: (payload) => client.post('/orders/', payload),
  sales: () => client.get('/orders/sales/'),
}

export const paymentApi = {
  initialize: (orderId) => client.post('/payments/initialize/', { order_id: orderId }),
  verify: (reference) => client.post('/payments/verify/', { reference }),
  history: () => client.get('/payments/'),
}

export const commissionApi = {
  list: () => client.get('/commissions/'),
}

export const notificationApi = {
  list: () => client.get('/notifications/'),
}
