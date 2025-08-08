<template>
  <v-menu v-model="menu" location="bottom end" offset-y :close-on-content-click="false">
    <template #activator="{ props }">
      <v-btn
        icon
        variant="text"
        density="compact"
        style="min-width: 32px; height: 32px; padding: 0; background: transparent"
        v-bind="props"
      >
        <v-badge
          :content="Count"
          color="red"
          overlap
          location="top end"
          style="--v-badge-font-size: 10px; --v-badge-height: 16px; --v-badge-min-width: 16px"
        >
          <v-icon style="font-size: 20px">mdi-bell</v-icon>
        </v-badge>
      </v-btn>
    </template>

    <v-card style="width: 400px">
      <v-card-title class="d-flex align-center gap-2">
        Notifications
        <v-spacer />
        <v-select
          v-model="typeFilter"
          :items="typeOptions"
          item-title="title"
          item-value="value"
          label="Type"
          dense
          hide-details
          style="width: 160px"
        />
        <v-select
          v-model="statusFilter"
          :items="statusOptions"
          label="Status"
          dense
          hide-details
          style="width: 160px"
        />
      </v-card-title>

      <v-card-text style="max-height: 600px; overflow-y: auto">
        <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-2" />

        <v-list v-else-if="filteredNotifications.length">
          <v-list-item
            v-for="n in filteredNotifications"
            :key="n.id"
            @click="markAsRead(n)"
            :class="{ 'bg-grey-lighten-4': isUnread(n) }"
            class="rounded-lg mb-2"
          >
            <v-list-item-title class="font-weight-bold">{{ n.title }}</v-list-item-title>
            <v-list-item-subtitle>{{ n.message }}</v-list-item-subtitle>
            <v-list-item-subtitle class="text-grey text-caption">
              {{ formatTimeAgo(n.created_at) }}
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>

        <div v-else class="text-center text-grey">No notifications</div>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchNotifications, updateNotification } from '@/api/notification.js'

const menu = ref(false)
const notifications = ref([])
const typeFilter = ref('All')
const statusFilter = ref('All')
const loading = ref(false)

const typeOptions = [
  { title: 'All', value: 'All' },
  { title: 'Event', value: 'event' },
  { title: 'Repond', value: 'respond' },
  { title: 'General', value: 'general' },
]

const statusMap = {
  event: ['unread', 'read'],
  respond: ['pending_response', 'responded'],
  general: ['pending', 'sent'],
}

const unreadStatusMap = {
  event: ['unread'],
  respond: ['pending_response'],
  general: ['pending'],
}

const statusOptions = computed(() => {
  if (typeFilter.value === 'All') {
    const allStatuses = Object.values(statusMap).flat()
    return ['All', ...Array.from(new Set(allStatuses))]
  }
  return ['All', ...(statusMap[typeFilter.value] || [])]
})

const fetchAllNotifications = async () => {
  loading.value = true
  try {
    const res = await fetchNotifications({})
    notifications.value = res.items.map((item) => ({
      ...item,
      status: item.status || item.event_status || item.respond_status || item.general_status || 'unknown',
    }))
  } catch (error) {
    console.error('[fetchAllNotifications] Lỗi:', error)
  } finally {
    loading.value = false
  }
}

const fetchFilteredNotifications = async () => {
  loading.value = true
  try {
    const params = {}
    const type = typeFilter.value
    const status = statusFilter.value

    if (type !== 'All') {
      params.notification_type = type
      const validStatusList = statusMap[type] || []
      if (status !== 'All' && validStatusList.includes(status)) {
        if (type === 'event') params.event_status = status
        else if (type === 'respond') params.respond_status = status
        else if (type === 'general') params.general_status = status
      }
    }

    const res = await fetchNotifications(params)
    notifications.value = res.items.map((item) => ({
      ...item,
      status: item.status || item.event_status || item.respond_status || item.general_status || 'unknown',
    }))
  } catch (error) {
    console.error('[fetchFilteredNotifications]  Lỗi:', error)
  } finally {
    loading.value = false
  }
}

watch(menu, (val) => {
  if (val) fetchFilteredNotifications()
})

watch([typeFilter, statusFilter], () => {
  if (menu.value) fetchFilteredNotifications()
})

onMounted(() => {
  fetchAllNotifications()
})

const filteredNotifications = computed(() => {
  return notifications.value.filter((n) => {
    const matchType = typeFilter.value === 'All' || n.notification_type === typeFilter.value
    const matchStatus = statusFilter.value === 'All' || n.status === statusFilter.value
    return matchType && matchStatus
  })
})

const Count = computed(() => {
  return notifications.value.filter((n) => {
    const list = unreadStatusMap[n.notification_type] || []
    return list.includes(n.status)
  }).length
})

const isUnread = (n) => {
  const list = unreadStatusMap[n.notification_type] || []
  return list.includes(n.status)
}

const markAsRead = async (n) => {
  if (!isUnread(n)) return

  const newStatus = getReadStatusForType(n.notification_type)
  const payload = {}

  if (n.notification_type === 'event') payload.event_status = newStatus
 

  try {
    await updateNotification(n.id, payload)
    n.status = newStatus
    console.log(`✅ Đã cập nhật và đánh dấu đã đọc ID:`, n.id)
  } catch (error) {
    console.error(`❌ Không thể đánh dấu đã đọc ID: ${n.id}`, error)
  }
}

const getReadStatusForType = (type) => {
  if (type === 'event') return 'read'
  if (type === 'respond') return 'responded'
  if (type === 'general') return 'sent'
  return 'read'
}

function formatTimeAgo(input) {
  const date = new Date(input)
  if (isNaN(date)) return 'Invalid time'
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)
  if (diff < 60) return `${diff} seconds ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}minutes ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`
  return date.toLocaleString('vi-VN')
}
</script>

<style scoped src="../assets/notification.css"></style>
