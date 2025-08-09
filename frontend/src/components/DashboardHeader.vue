<template>
  <div class="dashboard-header">
    <h1>Welcome back, {{ username }}!</h1>
    <div class="search-bar">
      <v-text-field
        variant="outlined"
        placeholder="Enter your search request..."
        prepend-inner-icon="mdi-magnify"
        hide-details
        density="compact"
        class="search-input"
      />
    </div>
    <div class="header-actions">
      <v-badge :content="notificationCount" color="red" v-if="notificationCount > 0">
        <v-btn icon size="small" class="action-btn">
          <v-icon>mdi-bell-outline</v-icon>
        </v-btn>
      </v-badge>
      <v-btn v-else icon size="small" class="action-btn">
        <v-icon>mdi-bell-outline</v-icon>
      </v-btn>
      <div class="profile-menu" @click="toggleDropdown">
        <v-avatar size="40" class="profile-avatar">
          <v-icon size="large">mdi-account-circle</v-icon>
        </v-avatar>
        <div v-if="showDropdown" class="dropdown">
          <a href="#" @click.prevent="handleLogout">
            <v-icon small>mdi-logout</v-icon> Logout
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

defineProps({
  username: String,
  notificationCount: Number,
  showDropdown: Boolean
})

const emit = defineEmits(['toggle-dropdown', 'logout'])

const toggleDropdown = () => {
  emit('toggle-dropdown')
}

const handleLogout = async (event) => {
  event.preventDefault()
  
  // Close dropdown first
  emit('toggle-dropdown')
  
  // Confirm logout
  if (!confirm('Are you sure you want to logout?')) {
    return
  }
  
  try {
    console.log('Logging out...')
    
    // Clear authentication data using auth store
    await authStore.logout()
    
    console.log('Logout successful, redirecting to auth...')
    
    // Redirect to auth page
    router.push('/auth')
    
    // Also emit logout event for parent component
    emit('logout')
  } catch (error) {
    console.error('Logout error:', error)
    // Even if logout fails, still redirect
    router.push('/auth')
  }
}
</script>
