import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useAuth() {
  const authStore = useAuthStore()
  
  const username = computed(() => {
    console.log('Auth Store User:', authStore.user) // Debug log
    return authStore.user?.name || 'Người dùng'
  })

  const loadUserProfile = async () => {
    try {
      if (!authStore.user && authStore.isAuthenticated) {
        console.log('Loading user profile...')
        await authStore.fetchUser()
        console.log('User profile loaded:', authStore.user)
      }
    } catch (error) {
      console.error('Failed to load user profile:', error)
    }
  }

  return {
    authStore,
    username,
    loadUserProfile
  }
}
