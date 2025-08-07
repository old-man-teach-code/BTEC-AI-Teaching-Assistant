import { defineStore } from 'pinia'
import api from '../api/http'
import * as authApi from '../api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    jwt: localStorage.getItem('jwt_token') || null,
    user: null,
  }),
  persist: true, // Enable persistence to store the state in localStorage
  getters: {
    isAuthenticated: (state) => !!state.jwt,
  },
  actions: {
    setJwt(token) {
      this.jwt = token
      if (token) {
        localStorage.setItem('jwt_token', token)
        // Manually set header để đảm bảo
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        console.log('🔑 Token set:', token.substring(0, 20) + '...')
      } else {
        localStorage.removeItem('jwt_token')
        delete api.defaults.headers.common['Authorization']
        console.log('🗑️ Token cleared')
      }
    },
    async login(credentials) {
      try {
        const response_data = await authApi.login(credentials.username, credentials.password)
        this.setJwt(response_data.access_token)
        this.$patch({ isAuthenticated: true })
        await this.fetchUser()
        return this.jwt
      } catch (error) {
        throw error // Re-throw the error to handle it in the component
      }
    },
    logout() {
      this.jwt = null
      this.user = null
      localStorage.removeItem('jwt_token')
      // Redirect được xử lý bởi http.js interceptor khi 401
      router.push('/auth')
    },
    setUser(user) {
      this.user = user
    },
    async updateUser(userData) {
      try {
        const response = await api.put('/api/users/me', userData)
        this.setUser(response.data)
        return response.data
      } catch (error) {
        throw error
      }
    },
    async fetchUser() {
      if (this.isAuthenticated) {
        try {
          console.log('Fetching user with token:', this.jwt?.substring(0, 20) + '...')
          console.log('Authorization header:', api.defaults.headers.common['Authorization']?.substring(0, 30) + '...')
          
          const response = await api.get('/api/users/me')
          console.log('User fetched successfully:', response.data)
          this.setUser(response.data) 
          return response.data
        } catch (error) {
          console.error('Failed to fetch user:', error.response?.status, error.response?.data)
          this.logout()
          throw error
        }
      } else {
        this.user = null
      }
    }
  }
})
