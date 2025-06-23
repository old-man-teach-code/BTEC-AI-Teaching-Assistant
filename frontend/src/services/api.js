// services/api.js
import axios from 'axios'

// ->>>Tạo instance
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
})

// ->>>> Request Interceptor: tự động thêm token vào headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ->>>> Response Interceptor: xử lý lỗi 401 (Unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Ví dụ: logout người dùng hoặc chuyển về trang login
      console.warn('Unauthorized, redirecting to login...')
      localStorage.removeItem('token')
      window.location.href = '/auth'
    }
    return Promise.reject(error)
  }
)

// 4. Export instance
export default api
