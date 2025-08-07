import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  useAuth,
  useCalendar,
  useStats,
  useEvents,
  useColors,
  useUI
} from '@/composables'

export function useHomeDashboard() {
  const router = useRouter()
  const authStore = useAuthStore()

  // Modal state
  const showTomorrowEventsModal = ref(false)

  // Auth composable
  const { username, loadUserProfile } = useAuth()

  // Calendar composable
  const {
    events,
    weekdays,
    currentMonthYear,
    calendarDays,
    todaysEvents,
    formatEventTime,
    previousMonth,
    nextMonth,
    selectDate
  } = useCalendar()

  // Stats composable
  const {
    stats,
    recentActivities,
    documents,
    notificationCount,
    tomorrowEvents,
    fetchStats
  } = useStats()

  // Events composable
  const { fetchCalendarEvents } = useEvents()

  // Colors composable
  const {
    getTypeColor,
    getStatusColor,
    getPriorityColor
  } = useColors()

  // UI composable
  const {
    showDropdown,
    timeFilter,
    toggleDropdown,
    setVisible
  } = useUI()

  // Main data loading function
  const loadDashboardData = async () => {
    // Load user profile trước
    await loadUserProfile()
    
    // Fetch calendar events
    const calendarEvents = await fetchCalendarEvents()
    events.value = calendarEvents
    
    // Fetch stats với events data
    await fetchStats(calendarEvents)
  }

  // Logout function
  const handleLogout = async (event) => {
    event.preventDefault()
    
    // Close dropdown
    showDropdown.value = false
    
    // Confirm logout
    if (!confirm('Are you sure you want to logout?')) {
      return
    }
    
    try {
      console.log('Logging out...')
      
      // Clear authentication data
      await authStore.logout()
      
      console.log('Logout successful, redirecting to auth...')
    } catch (error) {
      console.error('Logout error:', error)
      // Even if logout fails, still redirect
      router.push('/auth')
    }
  }

  // Initialize dashboard
  const initDashboard = async () => {
    await loadDashboardData()
    
    // Animation cho welcome card
    setTimeout(() => {
      setVisible(true)
    }, 300)
  }

  return {
    // State
    showTomorrowEventsModal,
    username,
    events,
    weekdays,
    currentMonthYear,
    calendarDays,
    todaysEvents,
    stats,
    recentActivities,
    documents,
    notificationCount,
    tomorrowEvents,
    showDropdown,
    timeFilter,

    // Methods
    formatEventTime,
    previousMonth,
    nextMonth,
    selectDate,
    getTypeColor,
    getStatusColor,
    getPriorityColor,
    toggleDropdown,
    handleLogout,
    loadDashboardData,
    initDashboard
  }
}
