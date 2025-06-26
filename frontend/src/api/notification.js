
import api from './http'


 
export const fetchNotifications = async (userId) => {
  if (!userId) {
    console.warn('[fetchNotifications] Không có userId')
    return []
  }

  try {
    const response = await api.get(`/api/notifications/${userId}`)
     console.log('🔔 Gọi fetchNotifications với userId:', userId)
    console.log('[fetchNotifications] Dữ liệu trả về:', response.data)
    return response.data
  } catch (error) {
    console.error('[fetchNotifications] Lỗi:', error)
    throw error
  }
}


export const markAllAsRead = async (userId) => {
  if (!userId) return

  try {
    await api.post(`/api/notifications/${userId}/mark-all-read`)
  } catch (error) {
    console.error('Lỗi cập nhật thông báo:', error)
    throw error
  }
}

