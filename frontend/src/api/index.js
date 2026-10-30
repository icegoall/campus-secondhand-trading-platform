import request from './request'

export const authApi = {
  register: (data) => request.post('/register', data),
  login: (account, password) => request.post('/login', { account, password }),
  logout: () => request.post('/logout'),
  me: () => request.get('/me')
}

export const productApi = {
  list: (params) => request.get('/products', { params }),
  detail: (id) => request.get(`/products/${id}`),
  create: (data) => request.post('/products', data),
  update: (id, data) => request.put(`/products/${id}`, data),
  remove: (id) => request.delete(`/products/${id}`),
  mine: () => request.get('/my/products')
}

export const orderApi = {
  create: (productId) => request.post('/orders', { product_id: productId }),
  list: (mine) => request.get('/orders', { params: mine ? { mine } : {} }),
  updateStatus: (id, status) => request.put(`/orders/${id}/status`, { status })
}

export const commentApi = {
  list: (productId) => request.get(`/products/${productId}/comments`),
  add: (productId, content) => request.post(`/products/${productId}/comments`, { content })
}

export const uploadApi = {
  upload: (file) => {
    const fd = new FormData()
    fd.append('file', file)
    return request.post('/upload', fd)
  }
}
