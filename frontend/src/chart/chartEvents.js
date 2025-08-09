// chartEvents.js
import { createDebounce } from './chartUtils.js'

// Create event handler class for better organization
export class ChartEventHandler {
  constructor(refreshCallback) {
    this.refreshCallback = refreshCallback
    this.debouncedRefresh = createDebounce()
    
    // Bind methods to preserve 'this' context
    this.handleDocumentDeleted = this.handleDocumentDeleted.bind(this)
    this.handleDocumentRestored = this.handleDocumentRestored.bind(this)
    this.handleEventsUpdated = this.handleEventsUpdated.bind(this)
  }

  // Event handler for document deletion
  handleDocumentDeleted(event) {
    const eventId = `deleted-${event.detail?.id}-${Date.now()}`
    console.log('🗑️ [ChartView] Document deleted event received:', event.detail, `[${eventId}]`)
    this.debouncedRefresh(
      this.refreshCallback,
      1000,
      `document-deleted-${event.detail?.id}`
    )
  }

  // Event handler for document restoration
  handleDocumentRestored(event) {
    const eventId = `restored-${event.detail?.id}-${Date.now()}`
    console.log('🔄 [ChartView] Document restored event received:', event.detail, `[${eventId}]`)
    this.debouncedRefresh(
      this.refreshCallback,
      1000,
      `document-restored-${event.detail?.id}`
    )
  }

  // Event handler for events updates
  handleEventsUpdated(event) {
    const eventId = `events-${Date.now()}`
    console.log('📅 [ChartView] Events updated event received:', event.detail, `[${eventId}]`)
    this.debouncedRefresh(
      this.refreshCallback,
      1000,
      'events-updated'
    )
  }

  // Register all event listeners
  registerEventListeners() {
    console.log('📡 [ChartView] Registering event listeners...')
    
    window.addEventListener('document-deleted', this.handleDocumentDeleted)
    window.addEventListener('document-restored', this.handleDocumentRestored)
    window.addEventListener('events-updated', this.handleEventsUpdated)
    
    console.log('✅ Event listeners registered for chart-calendar sync')
  }

  // Clean up event listeners
  unregisterEventListeners() {
    console.log('🧹 [ChartView] Cleaning up event listeners...')
    
    window.removeEventListener('document-deleted', this.handleDocumentDeleted)
    window.removeEventListener('document-restored', this.handleDocumentRestored)
    window.removeEventListener('events-updated', this.handleEventsUpdated)
    
    console.log('Chart event listeners cleaned up')
  }
}

// Chart update handlers
export const createChartUpdateHandlers = (chartsRefs, availablePeriods, eventsAvailablePeriods) => {
  
  // Handle events time type change
  const onEventsTimeTypeChange = (eventsTimeType, setEventsSelectedPeriod) => {
    // Reset to current period when changing time type
    const newPeriod = eventsTimeType === 'week' ? 'week-0' : 'month-0'
    setEventsSelectedPeriod(newPeriod)
    console.log('Events time type changed to:', eventsTimeType)
    
    // Force chart update
    if (chartsRefs.eventsChart?.value) {
      chartsRefs.eventsChart.value.update()
    }
  }

  // Handle events chart update
  const updateEventsChart = (eventsSelectedPeriod) => {
    console.log('Events chart updated to:', eventsSelectedPeriod)
    
    // Log the selected period details for debugging
    const period = eventsAvailablePeriods.value?.find((p) => p.value === eventsSelectedPeriod)
    if (period) {
      console.log('Events period details:', {
        label: period.label,
        startDate: period.startDate.toISOString().split('T')[0],
        endDate: period.endDate.toISOString().split('T')[0],
        isCurrentPeriod: eventsSelectedPeriod.endsWith('-0'),
      })
    }
    
    // Force chart update
    if (chartsRefs.eventsChart?.value) {
      chartsRefs.eventsChart.value.update()
    }
  }

  // Handle documents time type change
  const onTimeTypeChange = (documentsTimeType, setSelectedPeriod) => {
    // Reset to current period when changing time type
    const newPeriod = documentsTimeType === 'week' ? 'week-0' : 'month-0'
    setSelectedPeriod(newPeriod)
    console.log('Time type changed to:', documentsTimeType)
  }

  // Handle documents chart update
  const updateDocumentsChart = (selectedPeriod) => {
    console.log('Documents chart updated to:', selectedPeriod)

    // Log the selected period details for debugging
    const period = availablePeriods.value?.find((p) => p.value === selectedPeriod)
    if (period) {
      console.log('Period details:', {
        label: period.label,
        startDate: period.startDate.toISOString().split('T')[0],
        endDate: period.endDate.toISOString().split('T')[0],
        isCurrentPeriod: selectedPeriod.endsWith('-0'),
      })
    }
  }

  return {
    onEventsTimeTypeChange,
    updateEventsChart,
    onTimeTypeChange,
    updateDocumentsChart
  }
}