<template>
  <div>
    <!-- Nút thêm sự kiện -->
    <v-btn color="primary" class="mb-4" @click="handleCreate">Thêm sự kiện</v-btn>

    <!-- Lịch -->
    <ScheduleXCalendar :calendar-app="calendarApp" />

    <!-- Dialog thêm/sửa sự kiện -->
    <EventModal
      v-model="showDialog"
      :eventData="editEvent"
      @save="saveEvent"
      @delete="handleDelete"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ScheduleXCalendar } from '@schedule-x/vue'
import {
  createCalendar,
  viewDay,
  viewWeek,
  viewMonthAgenda,
  viewMonthGrid,
} from '@schedule-x/calendar'
import '@schedule-x/theme-default/dist/index.css'

import EventModal from '@/components/EventModal.vue'
import { fetchEvents, createEvent, updateEvent, deleteEvent } from '@/api/events.js'

const typeColors = reactive({})
const getColorByType = (type) => {
  if (!typeColors[type]) {
    const randomColor = '#' + Math.floor(Math.random() * 16777215).toString(16)
    typeColors[type] = randomColor
  }
  return typeColors[type]
}

const events = ref([])
const showDialog = ref(false)
const editEvent = ref(null)

// Khởi tạo lịch 1 lần duy nhất
const calendarApp = createCalendar({
  selectedDate: new Date().toISOString().split('T')[0],
  views: [viewMonthGrid, viewMonthAgenda, viewWeek, viewDay],
  defaultView: viewMonthAgenda.name,
  onViewChange: (newView) => {
    console.log('View vừa chuyển thành:', newView)
    // Nếu bạn cần xử lý gì đặc biệt khi đổi view (VD: load thêm dữ liệu), thêm ở đây
  },
  events: [],

  callbacks: {
    onEventClick: handleEventClick,
  },
})

function handleEventClick(event) {
  console.log('Clicked event:', event)
  editEvent.value = { ...event }
  showDialog.value = true
}
// Load danh sách sự kiện từ backend
const loadEvents = async () => {
  try {
    console.log('Đang tải sự kiện từ backend...')
    const raw = await fetchEvents()

    events.value = raw.map((e) => ({
      id: e.id,
      title: e.title,
     
      start: new Date(e.start_time).toISOString().replace("T"," ").slice(0,16), 
      end: new Date(e.end_time).toISOString().replace("T"," ").slice(0,16),
      description: e.description,
      location: e.location,
      type: e.event_type,
      remind: e.reminder_minutes,
      calendarId: e.event_type,
      color: getColorByType(e.event_type),
    }))
    console.log('Sự kiện đã tải:')
    console.log(events.value)

    calendarApp.events.set(events.value)
    console.log('Sự kiện đã tải:', events.value)
  } catch (e) {
    console.error('Lỗi tải sự kiện:', e)
  }
}

const handleCreate = () => {
  const now = new Date()
  const oneHourLater = new Date(now.getTime() + 60 * 60 * 1000)

  editEvent.value = {
    title: '',
    type: '',
    start: now,
    end: oneHourLater,
    description: '',
    location: '',
    remind: 15,
  }
  showDialog.value = true
}

const saveEvent = async (eventData) => {
  try {
    const payload = {
      title: eventData.title,
      event_type: eventData.type,
      start_time: eventData.start,
      end_time: eventData.end,
      description: eventData.description,
      location: eventData.location,
      reminder_minutes: eventData.remind,
    }

    if (eventData.id) {
      await updateEvent(eventData.id, payload)
      console.log('Updated')
    } else {
      await createEvent(payload)
      console.log('Created')
    }

    showDialog.value = false
    await loadEvents()
  } catch (e) {
    console.error('Lỗi lưu sự kiện:', e)
  }
}

// 🗑️ Xoá
const handleDelete = async (eventId) => {
  try {
    if (eventId) {
      await deleteEvent(eventId)
      console.log(' Deleted:', eventId)
      showDialog.value = false
      await loadEvents()
    }
  } catch (e) {
    console.error(' Lỗi xoá:', e)
  }
}

onMounted(() => {
  loadEvents()
})
</script>

<style scoped>
.sx-vue-calendar-wrapper {
  width: 1200px;
  max-width: 100vw;
  height: 800px;
  max-height: 90vh;
}
</style>
