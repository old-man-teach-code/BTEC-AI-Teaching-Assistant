
import api from './http' 

export const fetchStats = async () => {
  try {
    const response = await api.get('/api/stats')
    return response.data
  } catch (error) {
    console.error('[fetchStats]  Lỗi lấy thống kê:', error)
    throw error
  }
}
