import api from './http'

/**
 * Lấy danh sách sự kiện
 */
export const fetchEvents = async () => {
  try {
    console.log('[fetchEvents] Đang lấy danh sách sự kiện...')
    const response = await api.get('/api/calendar/events')
    return response.data.items 
  } catch (err) {
    console.error('[fetchEvents] Lỗi:', err.response?.data || err.message)
    throw err
  }
}

/**
 * Thêm sự kiện mới
 */
export const createEvent = async (data) => {
  try {
    const response = await api.post('/api/calendar/events', data)
    return response.data
  } catch (err) {
    console.error('[createEvent] Lỗi:', err.response?.data || err.message)
    throw err
  }
}

/**
 * Cập nhật sự kiện
 */
export const updateEvent = async (id, data) => {
  try {
    const response = await api.put(`/api/calendar/events/${id}`, data)
    return response.data
  } catch (err) {
    console.error('[updateEvent]  Lỗi:', err.response?.data || err.message)
    throw err
  }
}

/**
 * Xóa sự kiện
 */
export const deleteEvent = async (id) => {
  try {
   const response = await api.delete(`/api/calendar/events/${id}`)
    return response.data
  } catch (err) {
    console.error('[deleteEvent] Lỗi:', err.response?.data || err.message)
    throw err
  }
}