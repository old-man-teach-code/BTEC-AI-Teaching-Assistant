import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL
})

const token = localStorage.getItem('jwt_token')
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('jwt_token')
      window.location = '/login'
    }
    return Promise.reject(error)
  }
)

export default api