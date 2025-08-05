import { fetchEvents } from '@/api/events.js'

export function useEvents() {
  const fetchCalendarEvents = async () => {
    try {
      const rawEvents = await fetchEvents()
      return rawEvents.map(e => ({
        id: e.id,
        title: e.title,
        start: e.start_time,
        end: e.end_time,
        description: e.description,
        location: e.location,
        type: e.event_type || 'meeting'
      }))
    } catch (error) {
      console.error('Failed to fetch events:', error)
      return []
    }
  }

  return {
    fetchCalendarEvents
  }
}
