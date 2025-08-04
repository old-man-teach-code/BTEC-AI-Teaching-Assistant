<template>
  <aside class="sidebar">
    <!-- Header with collapse icon (placeholder) -->
    

    <!-- Top Menu -->
    <ul class="menu">
      <li
        v-for="item in sidebarItemsTop"
        :key="item.label"
        @click="handleSidebar(item)"
      >
        <v-icon>{{ item.icon }}</v-icon>
        <span>{{ item.label }}</span>
      </li>
    </ul>

    <!-- Bottom Menu -->
    <ul class="menu menu-bottom">
      <li
        v-for="item in sidebarItemsBottom"
        :key="item.label"
        @click="handleSidebar(item)"
      >
        <v-icon>{{ item.icon }}</v-icon>
        <span>{{ item.label }}</span>
      </li>
    </ul>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const sidebarItemsTop = [
  { label: 'Home', icon: 'mdi-home-outline', route: 'dashboardhome' },
  { label: 'Document', icon: 'mdi-file-document-outline', route: '/documents' },
  { label: 'Calendar', icon: 'mdi-calendar-clock-outline', route: '/calendar' },
  { label: 'Class', icon: 'mdi-account-group-outline', route: '/class' },
  { label: 'Statistical', icon: 'mdi-chart-line', route: '/stats' },
]

const sidebarItemsBottom = [
  { label: 'Trash', icon: 'mdi-delete-clock-outline', route: '/trash' },
  { label: 'Help Centre', icon: 'mdi-help-circle-outline', route: '/help' },
  { label: 'Setting', icon: 'mdi-cog-outline', action: 'setting' },
  { label: 'Return', icon: 'mdi-logout', action: 'logout', route: '/login' },
]

const handleSidebar = (item) => {
  if (item.route) {
    router.push(item.route)
  } else if (item.action === 'logout') {
    // Thực hiện hành động logout
    console.log('🔒 Logging out...')
    localStorage.removeItem('token')
    router.push('/login')
  } else if (item.action === 'setting') {
    console.log('⚙️ Open setting dialog')
    
  }
}
</script>

<style scoped>.sidebar {
  width: 220px;
  height: 100vh;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e5e7eb;
  padding: 16px 12px;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.04);
}

.sidebar-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding-bottom: 8px;
  margin-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}



.menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu li {
  display: flex;
  align-items: center;
  padding: 10px 8px;
  font-size: 15px;
  color: #1f2937;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  border-radius: 6px;
}

.menu li:hover {
  background-color: #f3f4f6;
  color: #111827;
}

.menu li v-icon {
  padding: 10px;
  margin-right: 12px;
  font-size: 20px;
  color: #4b5563;
}

.menu li span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-left: 8px;
}

.menu-bottom {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

</style>