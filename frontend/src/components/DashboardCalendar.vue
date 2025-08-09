<template>
  <div class="calendar-section">
    <div class="section-header">
      <h3>Calendar</h3>
      <div class="calendar-nav">
        <v-btn icon size="small" @click="$emit('previous-month')">
          <v-icon>mdi-chevron-left</v-icon>
        </v-btn>
        <span class="calendar-month">{{ currentMonthYear }}</span>
        <v-btn icon size="small" @click="$emit('next-month')">
          <v-icon>mdi-chevron-right</v-icon>
        </v-btn>
      </div>
    </div>
    <div class="calendar-grid">
      <div class="calendar-weekdays">
        <div v-for="day in weekdays" :key="day" class="weekday">{{ day }}</div>
      </div>
      <div class="calendar-days">
        <div
          v-for="date in calendarDays"
          :key="date.date"
          :class="['calendar-day', {
            'other-month': !date.isCurrentMonth,
            'today': date.isToday,
            'has-events': date.events.length > 0
          }]"
          @click="$emit('select-date', date)"
        >
          <span class="day-number">{{ date.day }}</span>
          <div v-if="date.events.length > 0" class="event-indicators">
            <div
              v-for="event in date.events.slice(0, 3)"
              :key="event.id"
              :class="['event-dot', event.type]"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Today's Events -->
    <div class="todays-events">
      <h4>Today's Events</h4>
      <div v-if="todaysEvents.length === 0" class="no-events">
        No events scheduled for today
      </div>
      <div v-else class="event-list">
        <div
          v-for="event in todaysEvents"
          :key="event.id"
          class="event-item"
        >
          <div class="event-time">{{ formatEventTime(event.start) }}</div>
          <div class="event-details">
            <div class="event-title">{{ event.title }}</div>
            <div class="event-location" v-if="event.location">{{ event.location }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  currentMonthYear: String,
  weekdays: Array,
  calendarDays: Array,
  todaysEvents: Array,
  formatEventTime: Function
})

defineEmits(['previous-month', 'next-month', 'select-date'])
</script>
