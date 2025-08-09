<template>
  <div class="sidebar-container">
    <!-- Mobile Hamburger Button -->
    <button 
      class="mobile-menu-btn" 
      @click="toggleSidebar"
      :class="{ active: isSidebarOpen }"
    >
      <span></span>
      <span></span>
      <span></span>
    </button>

    <!-- Mobile Overlay -->
    <div 
      v-if="isSidebarOpen" 
      class="mobile-overlay" 
      @click="closeSidebar"
    ></div>

    <aside class="sidebar" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="sidebar-header">
        <div class="collapse-icon" @click="toggleSidebar">«</div>
      </div>
      <ul class="menu">
        <li v-for="item in sidebarItemsTop" :key="item.label" @click="handleSidebar(item)">
          <v-icon>{{ item.icon }}</v-icon>
          <span>{{ item.label }}</span>
        </li>
      </ul>

      <ul class="menu menu-bottom">
        <li v-for="item in sidebarItemsBottom" :key="item.label" @click="handleSidebar(item)">
          <v-icon>{{ item.icon }}</v-icon>
          <span>{{ item.label }}</span>
        </li>
      </ul>
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isSidebarOpen = ref(false)

const sidebarItemsTop = [
  { label: 'Home', icon: 'mdi-home-outline', route: '/dashboardhome' },
  { label: 'Document', icon: 'mdi-file-document-outline', route: '/documents' },
  { label: 'Calendar', icon: 'mdi-calendar-clock-outline', route: '/calendar' },
  { label: 'Statistical', icon: 'mdi-chart-line', route: '/chart' },
]

const sidebarItemsBottom = [
  { label: 'Trash', icon: 'mdi-delete-clock-outline', route: '/trash' },
  { label: 'Help Centre', icon: 'mdi-help-circle-outline' },
  { label: 'Setting', icon: 'mdi-cog-outline', route: '/settings' },
  { label: 'Return', icon: 'mdi-logout', route: '/dashboardhome' },
]

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const closeSidebar = () => {
  isSidebarOpen.value = false
}

const handleSidebar = (item) => {
  if (item.route) {
    router.push(item.route)
    // Close sidebar on mobile after navigation
    if (window.innerWidth <= 768) {
      closeSidebar()
    }
  } else if (item.action === 'logout') {
    router.push({ path: '/home' })
    if (window.innerWidth <= 768) {
      closeSidebar()
    }
  } else if (item.action === 'setting') {
    console.log('Setting clicked')
  }
}

// Handle window resize
const handleResize = () => {
  if (window.innerWidth > 768) {
    isSidebarOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>
<style scoped src="../assets/documents.css"></style>