import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL
})

const token = localStorage.getItem('jwt_token')
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// Request interceptor để luôn set token mới nhất
api.interceptors.request.use(
  config => {
    const currentToken = localStorage.getItem('jwt_token')
    if (currentToken) {
      config.headers.Authorization = `Bearer ${currentToken}`
    }
    return config
  },
  error => Promise.reject(error)
)

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('jwt_token')
      delete api.defaults.headers.common['Authorization']
      window.location = '/auth'
    }
    return Promise.reject(error)
  }
)

export default api