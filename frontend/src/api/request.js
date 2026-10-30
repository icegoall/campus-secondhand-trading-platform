import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: '/api',
  timeout: 10000
})

service.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = token
  return config
})

service.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code !== 0) {
      ElMessage.error(res.message || 'Request failed')
      return Promise.reject(new Error(res.message || 'Error'))
    }
    return res
  },
  (error) => {
    const status = error.response?.status
    const msg = error.response?.data?.message
    if (status === 401) {
      ElMessage.error(msg || 'Not logged in or session expired')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (location.pathname !== '/login' && location.pathname !== '/register') {
        location.href = '/login'
      }
    } else {
      ElMessage.error(msg || error.message || 'Network error')
    }
    return Promise.reject(error)
  }
)

export default service
