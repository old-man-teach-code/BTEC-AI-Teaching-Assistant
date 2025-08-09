import api from './http'



/**
 * Gọi API lấy danh sách thông báo
 * @param {Object} params - Các filter: notification_type, event_status, respond_status, general_status, user_id, skip, limit
 * @returns {Promise<{ items: Array, total: number, unread_count: number }>}
 */
export const fetchNotifications = async (params = {}) => {
  try {
    console.log('[fetchNotifications] 🔄 Params gửi:', params)

    const useFilterByStatus =
      params.notification_type &&
      (params.event_status || params.respond_status || params.general_status)

    const endpoint = useFilterByStatus
      ? 'api/notifications/filter-by-status'
      : 'api/notifications'

    // Map status → status chung (API yêu cầu là `status`, không phải event_status...)
    const queryParams = { ...params }

    if (params.event_status) {
      queryParams.status = params.event_status
      delete queryParams.event_status
    } else if (params.respond_status) {
      queryParams.status = params.respond_status
      delete queryParams.respond_status
    } else if (params.general_status) {
      queryParams.status = params.general_status
      delete queryParams.general_status
    }

    const response = await api.get(endpoint, { params: queryParams })
    console.log('[fetchNotifications]  Dữ liệu nhận:', response.data)

    const { notifications: items, total, unread_count } = response.data

    // Debug từng dòng
    items.forEach(item => {
      console.log(`🧾 ${item.title} | type: ${item.notification_type}, status: ${item.status}`)
    })

    return { items, total, unread_count }
  } catch (error) {
    console.error('[fetchNotifications]  Lỗi gọi API:', error)
    throw error
  }
}
/**
 * Gọi API cập nhật thông báo
 * @param {number} id - ID thông báo
 * @param {object} data - Dữ liệu cập nhật (ví dụ: { event_status: 'read' })
 */
export const updateNotification = async (id, data) => {
  try {
    const response = await api.put(`/api/notifications/${id}`, data)
    console.log(`[updateNotification] ✅ Đã cập nhật ID ${id}`, response.data)
    return response.data
  } catch (error) {
    console.error(`[updateNotification] ❌ Lỗi cập nhật thông báo ID ${id}:`, error)
    throw error
  }
}