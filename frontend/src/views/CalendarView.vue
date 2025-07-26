<template>
  <div>
    <v-btn class="my-4" color="primary" @click="handleCreate">Thêm sự kiện mới</v-btn>
    <ScheduleXCalendar :calendar-app="calendarApp" />

    <!-- Dialog sự kiện -->
    <EventModal
      v-model="showDialog"
      :eventData="editEvent"
      :typeColorMap="typeColorMap"
      @save="saveEdit"
      @delete="deleteEvent"
    />
  </div>
</template>

<script setup>
import { ref, watch, reactive } from 'vue'
import { ScheduleXCalendar } from '@schedule-x/vue'
import {
  createCalendar,
  createViewDay,
  createViewWeek,
  createViewMonthAgenda,
  createViewMonthGrid,
} from '@schedule-x/calendar'
import '@schedule-x/theme-default/dist/index.css'
import EventModal from '@/components/EventModal.vue'

const LOCAL_STORAGE_KEY = 'calendar_events'

// Bản đồ màu loại sự kiện
const typeColorMap = reactive({
  Học: '#1E88E5',
  Họp: '#43A047',
  'Cá nhân': '#FB8C00',
  Khác: '#8E24AA',
})

const events = ref([])

// Load từ localStorage
const stored = localStorage.getItem(LOCAL_STORAGE_KEY)
if (stored) {
  const parsed = JSON.parse(stored)
  parsed.forEach((e) => {
    if (e.type && !e.color) {
      if (!typeColorMap[e.type]) {
        typeColorMap[e.type] = generateUniqueColor(Object.values(typeColorMap))
      }
      e.color = typeColorMap[e.type]
    }
  })
  events.value = parsed
} else {
  // Dữ liệu mẫu
  events.value = [
    {
      id: 1,
      title: 'Họp nhóm đồ án',
      type: 'Họp',
      start: '2025-07-24 09:00',
      end: '2025-07-24 10:00',
      startTime: '2025-07-24 09:00',
      endTime: '2025-07-24 10:00',
      location: 'Phòng 101',
      remind: 15,
      color: typeColorMap['Họp'],
    },
  ]
}

// Đồng bộ localStorage
watch(
  events,
  (val) => localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(val)),
  { deep: true }
)

const showDialog = ref(false)
const editEvent = ref({})
const today = new Date().toISOString().slice(0, 10)
const calendarApp = createCalendar({
  selectedDate: today,
  views: [createViewDay(), createViewWeek(), createViewMonthGrid(), createViewMonthAgenda()],
  events: events.value,
  callbacks: {
    onEventClick: handleEventClick,
  },
  eventRenderer: {
    customEventRenderer: (event, defaultElement) => {
      if (event.color) {
        defaultElement.style.backgroundColor = event.color
        defaultElement.style.borderColor = event.color
        defaultElement.style.color = '#fff' // trắng chữ nếu nền đậm
      }
      return defaultElement
    },
  },
})


function handleEventClick(event) {
  console.log('🟢 Clicked event:', event)
  editEvent.value = { ...event }
  showDialog.value = true
}

function handleCreate() {
  const now = new Date()
  const start = new Date(now)
  const end = new Date(now)
  end.setHours(end.getHours() + 1)

  const format = (d) => d.toISOString().slice(0, 16).replace('T', ' ')
  editEvent.value = {
    title: '',
    type: '',
    startTime: format(start),
    endTime: format(end),
    location: '',
    remind: 10,
  }
  showDialog.value = true
}

function generateUniqueColor(existingColors) {
  let color
  do {
    color = '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')
  } while (existingColors.includes(color))
  return color
}

function saveEdit(updated) {
  const type = updated.type

  // Gán màu nếu loại mới
  if (!typeColorMap[type]) {
    typeColorMap[type] = generateUniqueColor(Object.values(typeColorMap))
  }
  updated.color = typeColorMap[type]

  // Đảm bảo start/end đúng format
  updated.start = updated.startTime
  updated.end = updated.endTime

  const index = events.value.findIndex((e) => e.id === updated.id)
  if (index !== -1) {
    events.value[index] = updated
    console.log('✅ Sửa sự kiện:', updated)
  } else {
    updated.id = Date.now()
    events.value.push(updated)
    console.log('🆕 Thêm sự kiện mới:', updated)
  }

  showDialog.value = false
}

function deleteEvent(id) {
  if (!confirm('Bạn có chắc chắn muốn xoá?')) return
  events.value = events.value.filter((e) => e.id !== id)
  showDialog.value = false
}
</script>

<style scoped>
.sx-vue-calendar-wrapper {
  width: 1200px;
  max-width: 100vw;
  height: 800px;
  max-height: 90vh;
}
</style>
