import { ref } from 'vue'
import api from '../api/http'

export function useStats() {
  const stats = ref({
    documents: 0,
    questionsAnswered: 0,
    announcements: 0,
    missedDeadlines: 0,
    scheduledToday: 0
  })

  const recentActivities = ref([])
  const documents = ref([])
  const notificationCount = ref(0)

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
      
      // Update notification count dựa trên documents mới
      const recentDocs = allDocuments.filter(doc => {
        const createdDate = new Date(doc.created_at)
        const now = new Date()
        const diffDays = (now - createdDate) / (1000 * 60 * 60 * 24)
        return diffDays <= 7 // Documents trong 7 ngày qua
      })
      notificationCount.value = recentDocs.length
      
      // Update stats với dữ liệu thật
      stats.value = {
        documents: allDocuments.length,
        questionsAnswered: 0, // Chưa có dữ liệu thật
        announcements: 0, // Chưa có dữ liệu thật
        missedDeadlines: 0, // Chưa có dữ liệu thật
        scheduledToday: events.filter(e => {
          const today = new Date().toISOString().split('T')[0]
          const eventDate = new Date(e.start).toISOString().split('T')[0]
          return eventDate === today
        }).length
      }
      
      // Update recent activities với dữ liệu thật
      recentActivities.value = allDocuments
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 6)
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
      stats.value = {
        documents: 0,
        questionsAnswered: 0,
        announcements: 0,
        missedDeadlines: 0,
        scheduledToday: 0
      }
      notificationCount.value = 0
    }
  }

  return {
    stats,
    recentActivities,
    documents,
    notificationCount,
    fetchStats,
    getTimeAgo
  }
}
