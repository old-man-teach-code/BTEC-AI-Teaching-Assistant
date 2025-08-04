import { ref, computed } from 'vue'

export function useCalendar() {
  const currentDate = ref(new Date())
  const events = ref([])
  const selectedDate = ref(new Date())
  
  const weekdays = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']

  const currentMonthYear = computed(() => {
    return currentDate.value.toLocaleDateString('en-US', { 
      month: 'long', 
      year: 'numeric' 
    })
  })

  const calendarDays = computed(() => {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth()
    
    // First day of month and how many days in month
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startingDayOfWeek = firstDay.getDay()
    
    const days = []
    const today = new Date()
    
    // Previous month days
    const prevMonth = new Date(year, month - 1, 0)
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
      const day = prevMonth.getDate() - i
      const date = new Date(year, month - 1, day)
      days.push({
        day,
        date: date.toISOString().split('T')[0],
        isCurrentMonth: false,
        isToday: false,
        events: getEventsForDate(date)
      })
    }
    
    // Current month days
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day)
      const isToday = date.toDateString() === today.toDateString()
      days.push({
        day,
        date: date.toISOString().split('T')[0],
        isCurrentMonth: true,
        isToday,
        events: getEventsForDate(date)
      })
    }
    
    // Next month days to fill the grid
    const totalCells = Math.ceil(days.length / 7) * 7
    const remainingCells = totalCells - days.length
    for (let day = 1; day <= remainingCells; day++) {
      const date = new Date(year, month + 1, day)
      days.push({
        day,
        date: date.toISOString().split('T')[0],
        isCurrentMonth: false,
        isToday: false,
        events: getEventsForDate(date)
      })
    }
    
    return days
  })

  const todaysEvents = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    return events.value.filter(event => {
      const eventDate = new Date(event.start).toISOString().split('T')[0]
      return eventDate === today
    })
  })

  // Helper functions
  const getEventsForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0]
    return events.value.filter(event => {
      const eventDate = new Date(event.start).toISOString().split('T')[0]
      return eventDate === dateStr
    })
  }

  const formatEventTime = (datetime) => {
    return new Date(datetime).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  }

  // Calendar navigation
  const previousMonth = () => {
    currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
  }

  const nextMonth = () => {
    currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
  }

  const selectDate = (date) => {
    selectedDate.value = new Date(date.date)
  }

  return {
    currentDate,
    events,
    selectedDate,
    weekdays,
    currentMonthYear,
    calendarDays,
    todaysEvents,
    getEventsForDate,
    formatEventTime,
    previousMonth,
    nextMonth,
    selectDate
  }
}
