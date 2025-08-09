import { ref } from 'vue'
import api from '../api/http'

export function useStats() {
  const stats = ref({
    documents: 0,
    questionsAnswered: 0,
    announcements: 0,
    missedDeadlines: 0,
    scheduledToday: 0,

    announcementMessage: 'No upcoming events',
    documentGrowth: 0,
    thisWeekDocs: 0,
    lastWeekDocs: 0

  })

  const recentActivities = ref([])
  const documents = ref([])
  const notificationCount = ref(0)
  const tomorrowEvents = ref([])

  // Helper function để format thời gian
  const getTimeAgo = (date) => {
    const now = new Date()
    const diffMs = now - date
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    
    if (diffDays > 0) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
    if (diffHours > 0) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    return 'just now'
  }

  // Fetch dữ liệu thật từ API
  const fetchStats = async (events = []) => {
    try {
      // Fetch documents
      const documentsRes = await api.get('/api/documents')
      const allDocuments = documentsRes.data.items.filter(doc => 
        doc.status === 'uploaded' || doc.status === 'ready'
      )
      
      // Lưu documents cho chart
      documents.value = allDocuments
      
      // Tính documents trong 7 ngày gần đây (tuần này)
      const now = new Date()
      const thisWeekDocs = allDocuments.filter(doc => {
        const createdDate = new Date(doc.created_at)
        const diffDays = (now - createdDate) / (1000 * 60 * 60 * 24)
        return diffDays <= 7
      })
      
      // Tính documents từ 8-14 ngày trước (tuần trước)
      const lastWeekDocs = allDocuments.filter(doc => {
        const createdDate = new Date(doc.created_at)
        const diffDays = (now - createdDate) / (1000 * 60 * 60 * 24)
        return diffDays > 7 && diffDays <= 14
      })
      
      // Tính % tăng trưởng
      const calculateGrowth = (current, previous) => {
        if (previous === 0) return current > 0 ? 100 : 0
        return Math.round(((current - previous) / previous) * 100)
      }
      
      const documentGrowth = calculateGrowth(thisWeekDocs.length, lastWeekDocs.length)
      
      // Update notification count dựa trên documents mới
      notificationCount.value = thisWeekDocs.length
      
      // Get tomorrow's events using local timezone
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      const tomorrowDateStr = tomorrow.getFullYear() + '-' + 
                             String(tomorrow.getMonth() + 1).padStart(2, '0') + '-' + 
                             String(tomorrow.getDate()).padStart(2, '0')
      
      const today = new Date()
      const todayStr = today.getFullYear() + '-' + 
                      String(today.getMonth() + 1).padStart(2, '0') + '-' + 
                      String(today.getDate()).padStart(2, '0')
      
      console.log('🔍 [useStats] Debug tomorrow events (LOCAL TIMEZONE):')
      console.log('  Current date:', todayStr)
      console.log('  Tomorrow date:', tomorrowDateStr)
      console.log('  Total events:', events.length)
      
      const tomorrowEventsList = events.filter(e => {
        const eventDateObj = new Date(e.start)
        const eventDate = eventDateObj.getFullYear() + '-' + 
                         String(eventDateObj.getMonth() + 1).padStart(2, '0') + '-' + 
                         String(eventDateObj.getDate()).padStart(2, '0')
        
        const matches = eventDate === tomorrowDateStr
        console.log(`  Event "${e.title}": ${e.start} -> ${eventDate} (matches tomorrow: ${matches})`)
        return matches
      })
      
      console.log('  Tomorrow events found:', tomorrowEventsList.length, tomorrowEventsList.map(e => e.title))
      
      // Store tomorrow events for modal display
      tomorrowEvents.value = tomorrowEventsList
      
      // Create announcement message for tomorrow's events
      const getAnnouncementMessage = () => {
        if (tomorrowEventsList.length === 0) {
          return 'No events tomorrow'
        }
        
        if (tomorrowEventsList.length === 1) {
          const event = tomorrowEventsList[0]
          const time = new Date(event.start).toLocaleTimeString('vi-VN', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false 
          })
          return `Tomorrow: ${event.title} at ${time}`
        }
        
        return `Tomorrow: ${tomorrowEventsList.length} events scheduled`
      }
      
      // Get tomorrow's events using local timezone
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      const tomorrowDateStr = tomorrow.getFullYear() + '-' + 
                             String(tomorrow.getMonth() + 1).padStart(2, '0') + '-' + 
                             String(tomorrow.getDate()).padStart(2, '0')
      
      const today = new Date()
      const todayStr = today.getFullYear() + '-' + 
                      String(today.getMonth() + 1).padStart(2, '0') + '-' + 
                      String(today.getDate()).padStart(2, '0')
      
      console.log('🔍 [useStats] Debug tomorrow events (LOCAL TIMEZONE):')
      console.log('  Current date:', todayStr)
      console.log('  Tomorrow date:', tomorrowDateStr)
      console.log('  Total events:', events.length)
      
      const tomorrowEventsList = events.filter(e => {
        const eventDateObj = new Date(e.start)
        const eventDate = eventDateObj.getFullYear() + '-' + 
                         String(eventDateObj.getMonth() + 1).padStart(2, '0') + '-' + 
                         String(eventDateObj.getDate()).padStart(2, '0')
        
        const matches = eventDate === tomorrowDateStr
        console.log(`  Event "${e.title}": ${e.start} -> ${eventDate} (matches tomorrow: ${matches})`)
        return matches
      })
      
      console.log('  Tomorrow events found:', tomorrowEventsList.length, tomorrowEventsList.map(e => e.title))
      
      // Store tomorrow events for modal display
      tomorrowEvents.value = tomorrowEventsList
      
      // Create announcement message for tomorrow's events
      const getAnnouncementMessage = () => {
        if (tomorrowEventsList.length === 0) {
          return 'No events tomorrow'
        }
        
        if (tomorrowEventsList.length === 1) {
          const event = tomorrowEventsList[0]
          const time = new Date(event.start).toLocaleTimeString('vi-VN', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false 
          })
          return `Tomorrow: ${event.title} at ${time}`
        }
        
        return `Tomorrow: ${tomorrowEventsList.length} events scheduled`
      }
      
      // Update stats với dữ liệu thật
      stats.value = {
        documents: allDocuments.length,
        questionsAnswered: 0, // Chưa có dữ liệu thật
        announcements: tomorrowEventsList.length,
        missedDeadlines: 0, // Chưa có dữ liệu thật
        scheduledToday: events.filter(e => {
          const eventDateObj = new Date(e.start)
          const eventDate = eventDateObj.getFullYear() + '-' + 
                           String(eventDateObj.getMonth() + 1).padStart(2, '0') + '-' + 
                           String(eventDateObj.getDate()).padStart(2, '0')
          return eventDate === todayStr
        }).length,

        announcementMessage: getAnnouncementMessage(),
        documentGrowth: documentGrowth,
        thisWeekDocs: thisWeekDocs.length,
        lastWeekDocs: lastWeekDocs.length

      }
      
      // Update recent activities với dữ liệu thật
      recentActivities.value = allDocuments
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 5)
        .map(doc => {
          // Lấy extension từ tên file
          const extension = doc.original_name.split('.').pop().toUpperCase()
          
          return {
            id: doc.id,

            title: `${doc.original_name}`,
            type: extension, // Hiển thị extension thực
            status: doc.status === 'ready' ? 'RESTORE' : 'UPLOAD',

            priority: 'MEDIUM',
            timeAgo: getTimeAgo(new Date(doc.created_at))
          }
        })
        
    } catch (error) {
      console.error('Failed to fetch stats:', error)
      // Fallback values nếu API lỗi
      documents.value = []
      tomorrowEvents.value = []
      stats.value = {
        documents: 0,
        questionsAnswered: 0,
        announcements: 0,
        missedDeadlines: 0,
        scheduledToday: 0,

        announcementMessage: 'No upcoming events',
        documentGrowth: 0,
        thisWeekDocs: 0,
        lastWeekDocs: 0

      }
      notificationCount.value = 0
    }
  }

  return {
    stats,
    recentActivities,
    documents,
    notificationCount,
    tomorrowEvents,
    fetchStats,
    getTimeAgo
  }
}
