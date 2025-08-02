<template>
     <aside class="sidebar">
      <div class="sidebar-header">
        <div class="collapse-icon">«</div>
      </div>
      <ul class="menu">
        <li v-for="item in sidebarItemsTop" :key="item.label">
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
  const sidebarItemsTop = [
    { label: 'Home', icon: 'mdi-home-outline' },
    { label: 'Document', icon: 'mdi-file-document-outline', route: '/documents' },
    { label: 'Calendar', icon: 'mdi-calendar-clock-outline' },
    { label: 'Class', icon: 'mdi-account-group-outline' },
    { label: 'Statistical', icon: 'mdi-chart-line' },
  ]

  const sidebarItemsBottom = [
    { label: 'Trash', icon: 'mdi-delete-clock-outline', route: '/trash'},
    { label: 'Help Centre', icon: 'mdi-help-circle-outline' },
    { label: 'Setting', icon: 'mdi-cog-outline', action: 'setting' },
    { label: 'Return', icon: 'mdi-logout', action: 'logout' },
  ]
</script>