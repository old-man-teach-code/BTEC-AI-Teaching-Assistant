import { defineStore } from 'pinia'
import api from '../api/http'
import * as authApi from '../api/auth'
import * as userApi from '../api/user'
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
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      } else {
        localStorage.removeItem('jwt_token')
        delete api.defaults.headers.common['Authorization']
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
      this.setJwt(null) // Clear JWT token
      this.$patch({ isAuthenticated: false })
      router.push('/auth') // Redirect to login page
    },
    setUser(user) {
      this.user = user
    },
    async fetchUser() {
      if (this.isAuthenticated) {
        try {
          const response = await userApi.fetchUser()
          this.setUser(response.data) 
          return response.data
        } catch (error) {
          
          this.logout()
          throw error
        }
      } else {
        this.user = null
      }
    }
  }
})
