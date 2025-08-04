<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="collapse-icon">«</div>
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
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const sidebarItemsTop = [
  { label: 'Home', icon: 'mdi-home-outline', route: '/dashboardhome' },
  { label: 'Document', icon: 'mdi-file-document-outline', route: '/documents' },
  { label: 'Calendar', icon: 'mdi-calendar-clock-outline', route: '/calendar' },
  { label: 'Notifications', icon: 'mdi-bell-outline' },
  { label: 'Statistical', icon: 'mdi-chart-line' },
]

const sidebarItemsBottom = [
  { label: 'Trash', icon: 'mdi-delete-clock-outline', route: '/trash' },
  { label: 'Help Centre', icon: 'mdi-help-circle-outline' },
  { label: 'Setting', icon: 'mdi-cog-outline', action: 'setting' },
  { label: 'Return', icon: 'mdi-logout', action: 'logout' },
]

const handleSidebar = (item) => {
  if (item.route) {
    router.push(item.route)
  } else if (item.action === 'logout') {
    router.push({ path: '/home' })
  } else if (item.action === 'setting') {
    // Xử lý setting
    console.log('Setting clicked')
  }
}
</script>
<style scoped src="../assets/documents.css"></style>