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
    const today = new Date()
    const todayStr = today.getFullYear() + '-' + 
                   String(today.getMonth() + 1).padStart(2, '0') + '-' + 
                   String(today.getDate()).padStart(2, '0')
    
    console.log('🔍 [todaysEvents] Today local date:', todayStr)
    
    const filtered = events.value.filter(event => {
      const eventDateObj = new Date(event.start)
      const eventDate = eventDateObj.getFullYear() + '-' + 
                       String(eventDateObj.getMonth() + 1).padStart(2, '0') + '-' + 
                       String(eventDateObj.getDate()).padStart(2, '0')
      
      const matches = eventDate === todayStr
      console.log(`  Event "${event.title}": ${event.start} -> ${eventDate} (matches today: ${matches})`)
      return matches
    })
    
    console.log('  Today events found:', filtered.length, filtered.map(e => e.title))
    return filtered
  })

  // Helper functions  
  const getEventsForDate = (date) => {
    // Sử dụng local date string thay vì UTC để tránh timezone issues
    const dateStr = date.getFullYear() + '-' + 
                   String(date.getMonth() + 1).padStart(2, '0') + '-' + 
                   String(date.getDate()).padStart(2, '0')
    
    console.log(`🔍 [getEventsForDate] Looking for events on: ${dateStr}`)
    
    const matchedEvents = events.value.filter(event => {
      // Parse event date using local timezone
      const eventDateObj = new Date(event.start)
      const eventDate = eventDateObj.getFullYear() + '-' + 
                       String(eventDateObj.getMonth() + 1).padStart(2, '0') + '-' + 
                       String(eventDateObj.getDate()).padStart(2, '0')
      
      const matches = eventDate === dateStr
      console.log(`  Event "${event.title}": ${event.start} -> ${eventDate} (matches: ${matches})`)
      return matches
    })
    
    console.log(`  Found ${matchedEvents.length} events for ${dateStr}`)
    return matchedEvents
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
