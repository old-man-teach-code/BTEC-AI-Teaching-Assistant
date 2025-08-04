<template>
  <div>
    <v-btn color="primary" class="mb-4" @click="handleCreate">Thêm sự kiện</v-btn>
    <div class="sx-vue-calendar-wrapper">
  <ScheduleXCalendar :calendar-app="calendarApp" />
</div>


    <EventModal
      v-model="showDialog"
      :eventData="editEvent"
      :typeColorMap="typeColorMap"
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

// 🎨 Danh sách màu và mapping type -> color
const colorList = [
  '#f94144', '#f3722c', '#f9c74f', '#90be6d',
  '#43aa8b', '#577590', '#277da1', '#9b5de5',
  '#ff006e', '#fb5607', '#ffbe0b'
]
const typeColorMap = reactive({})

function getColorForType(type) {
  if (!typeColorMap[type]) {
    const available = colorList.filter(c => !Object.values(typeColorMap).includes(c))
    const random = available.length > 0
      ? available[Math.floor(Math.random() * available.length)]
      : colorList[Math.floor(Math.random() * colorList.length)]
    typeColorMap[type] = random
  }
  return typeColorMap[type]
}

// 📅 Sự kiện và calendar
const events = ref([])
const showDialog = ref(false)
const editEvent = ref(null)

const calendarApp = createCalendar({
  selectedDate: new Date().toISOString().split('T')[0],
  views: [viewMonthGrid, viewMonthAgenda, viewWeek, viewDay],
  defaultView: viewMonthAgenda.name,
  events: [],
  callbacks: {
    onEventClick: handleEventClick,
  },
 config: {
  eventDisplay: {
    colorSource: 'event.color'  // ✅ Đảm bảo dùng màu từ event
  }
}
})

function handleEventClick(event) {
  console.log('🟢 Sự kiện được nhấp:', event)
  editEvent.value = {
    ...event,
    startTime: event.start.replace(' ', 'T'),
    endTime: event.end.replace(' ', 'T'),
  }
  showDialog.value = true
}

function formatDatetimeLocal(input) {
  const date = new Date(input)
  const yyyy = date.getFullYear()
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const dd = String(date.getDate()).padStart(2, '0')
  const hh = String(date.getHours()).padStart(2, '0')
  const mi = String(date.getMinutes()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}`
}

const loadEvents = async () => {
  try {
    const raw = await fetchEvents()
    events.value = raw.map((e) => {
      const type = e.event_type
      return {
        id: e.id,
        title: e.title,
        start: formatDatetimeLocal(e.start_time),
        end: formatDatetimeLocal(e.end_time),
        description: e.description,
        location: e.location,
        type,
        remind: e.reminder_minutes,
     
        color: getColorForType(type), 
      }
    })

    console.log('🎨 Events mapped:', events.value)
    calendarApp.events.set(events.value)
  } catch (e) {
    console.error('❌ Lỗi tải sự kiện:', e)
  }
}

const handleCreate = () => {
  const now = new Date()
  const oneHourLater = new Date(now.getTime() + 60 * 60 * 1000)

  editEvent.value = {
    title: '',
    type: '',
    startTime: now.toISOString().slice(0, 16),
    endTime: oneHourLater.toISOString().slice(0, 16),
    description: '',
    location: '',
    color: '',
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
    } else {
      await createEvent(payload)
    }

    showDialog.value = false
    await loadEvents()
  } catch (e) {
    console.error('❌ Lỗi lưu sự kiện:', e)
  }
}

const handleDelete = async (eventId) => {
  try {
    await deleteEvent(eventId)
    showDialog.value = false
    await loadEvents()
  } catch (e) {
    console.error('❌ Lỗi xoá sự kiện:', e)
  }
}

onMounted(loadEvents)
</script>

<style scoped>
.sx-vue-calendar-wrapper {
  width: 1200px;
  max-width: 100vw;
  height: 800px;
  max-height: 90vh;
}
.sx-vue-calendar-wrapper .event {
  border: 1px solid black;
}
</style>