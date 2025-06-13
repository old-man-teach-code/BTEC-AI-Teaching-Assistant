import api from './http'

export const login = async (username, password) => {
  const res = await api.post('/auth/login', { username, password })
  if (res.data && res.data.access_token) {
    localStorage.setItem('jwt_token', res.data.access_token)
    api.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`
  }
  return res.data
}

export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    localStorage.setItem('jwt_token', token)
  } else {
    delete api.defaults.headers.common['Authorization']
    localStorage.removeItem('jwt_token')
  }
}

export const logout = () => {
  setAuthToken(null)
  window.location = '/login'
}