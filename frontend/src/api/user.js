import api from './http'
import { useAuthStore } from '../stores/auth'

export const fetchUser = async () => {
  const authStore = useAuthStore()
  if (authStore.isAuthenticated) {
    try {
      const response = await api.get('/api/users/me')
      
 return response 
    } catch (error) {
      authStore.logout() // Logout if fetching user fails
      throw error // Re-throw the error to handle it in the component
    }
  } else {
    authStore.setUser(null)
  }
}

export const getUserById = async (userId) => {
  
  try {
    const response = await api.get(`/api/users/${userId}`)
    return response.data
  } catch (error) {
    throw error // Re-throw the error to handle it in the component
  }
}


