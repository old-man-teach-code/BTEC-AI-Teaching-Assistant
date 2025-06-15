import api from './http'

export const login = async (username, password) => {
  const res = await api.post('/auth/login', { username, password },
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }
  )
  return res.data
}
