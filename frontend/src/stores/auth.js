import { defineStore } from 'pinia'
import api from '../api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    jwt: localStorage.getItem('jwt_token') || null,
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.jwt,
  },
  actions: {
    async login(credentials) {
      try {
        const params = new URLSearchParams()
        params.append('username', credentials.username)
        params.append('password', credentials.password)
        const response = await api.post(
          '/auth/login',
          params,
          {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            }
          }
        )
        this.jwt = response.data.token
        localStorage.setItem('jwt_token', this.jwt)
        api.defaults.headers.common['Authorization'] = `Bearer ${this.jwt}`
        // Optionally fetch user info here
        await this.fetchUser()
        return this.jwt
      } catch (error) {
        console.error('Login failed:', error)
        throw error // Re-throw the error to handle it in the component
      }
    },
    logout() {
      this.jwt = null
      this.user = null
      localStorage.removeItem('jwt_token')
      delete api.defaults.headers.common['Authorization']
    },
    setUser(user) {
      this.user = user
    },
    async fetchUser() {
      if (this.isAuthenticated) {
        try {
          const response = await api.get('/auth/me')
          this.setUser(response.data)
        } catch (error) {
          console.error('Failed to fetch user:', error)
          this.logout() // Logout if fetching user fails
        }
      }else {
        this.user = null
      }
    }
  }
})
