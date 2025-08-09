// chartApi.js
import api from '../api/http'

// Fetch Events Data
export const fetchEventsData = async () => {
  try {
    const response = await api.get('/api/calendar/events')
    const events = response.data.items || []
    console.log('Events data loaded:', events.length, 'events')
    
    if (events.length > 0) {
      console.log('Events sample:', events[0])
      console.log('Chart-Calendar sync: Data structure matches calendar')
    }
    
    return events
  } catch (error) {
    console.error('Failed to fetch events:', error)
    return []
  }
}

// Fetch Documents Data
export const fetchDocumentsData = async () => {
  try {
    console.log('[fetchDocumentsData] Fetching documents data...')

    // Fetch both active and deleted documents
    const [activeResponse, trashResponse] = await Promise.all([
      api.get('/api/documents'),
      api.get('/api/documents/trash'),
    ])

    console.log('[fetchDocumentsData] Active documents response:', activeResponse.data)
    console.log('[fetchDocumentsData] Trash documents response:', trashResponse.data)

    // Combine active and trash documents
    const activeDocuments = activeResponse.data?.items || []
    const trashDocuments = trashResponse.data?.items || []

    // Mark trash documents with proper status
    const markedTrashDocs = trashDocuments.map((doc) => ({
      ...doc,
      status: 'deleted',
      is_deleted: true,
    }))

    const allDocuments = [...activeDocuments, ...markedTrashDocs]

    console.log('Documents data loaded:', allDocuments.length, 'total documents')
    console.log('Active documents:', activeDocuments.length)
    console.log('Deleted documents:', trashDocuments.length)

    if (allDocuments.length > 0) {
      console.log('Sample document:', allDocuments[0])

      // Debug: Log status distribution
      const statusCount = allDocuments.reduce((acc, doc) => {
        const status = doc.is_deleted ? 'deleted' : doc.status || 'unknown'
        acc[status] = (acc[status] || 0) + 1
        return acc
      }, {})
      console.log('Status distribution:', statusCount)
    }

    return allDocuments
  } catch (error) {
    console.error('Failed to fetch documents:', error)
    return []
  }
}

// Refresh All Data
export const refreshAllData = async () => {
  console.log('🔄 Starting data refresh...')
  
  try {
    const [eventsData, documentsData] = await Promise.all([
      fetchEventsData(),
      fetchDocumentsData()
    ])

    console.log('Charts data refreshed successfully')
    console.log(`✅ Events: ${eventsData.length}, Documents: ${documentsData.length}`)
    
    // Emit event to notify other components about data update
    window.dispatchEvent(new CustomEvent('charts-data-updated', {
      detail: {
        eventsCount: eventsData.length,
        documentsCount: documentsData.length,
        timestamp: new Date().toISOString()
      }
    }))

    return {
      eventsData,
      documentsData
    }
  } catch (error) {
    console.error('Failed to refresh data:', error)
    throw error
  }
}