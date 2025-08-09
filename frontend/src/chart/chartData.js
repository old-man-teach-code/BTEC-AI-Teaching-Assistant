// chartData.js
import { getDocumentCounts, getEventsSelectedPeriodDates, getSelectedPeriodDates } from './chartUtils.js'

// Generate Events Chart Data
export const generateEventsChartData = (eventsData, eventsTimeType, availablePeriods, selectedPeriod, visibleDatasets) => {
  const currentDate = new Date()
  const labels = []
  const occurredData = []
  const upcomingData = []

  // Get date range based on selected period
  const { startDate, endDate } = getEventsSelectedPeriodDates(availablePeriods, selectedPeriod, eventsTimeType)

  if (eventsTimeType === 'week') {
    // Generate 7 days from Monday to Sunday
    for (let i = 0; i < 7; i++) {
      const currentDay = new Date(startDate)
      currentDay.setDate(startDate.getDate() + i)
      labels.push(currentDay.toISOString().split('T')[0])

      // Count events for this day
      let occurred = 0
      let upcoming = 0

      const dayStr = currentDay.toISOString().split('T')[0]
      
      if (eventsData.length > 0) {
        eventsData.forEach((event) => {
          const eventDate = new Date(event.start_time)
          const eventDateStr = eventDate.toISOString().split('T')[0]
          
          if (eventDateStr === dayStr) {
            if (eventDate < currentDate) {
              occurred++
            } else {
              upcoming++
            }
          }
        })
      } else {
        // Demo data for week view
        occurred = Math.floor(Math.random() * 3)
        upcoming = Math.floor(Math.random() * 3)
      }

      occurredData.push(occurred)
      upcomingData.push(upcoming)
    }
  } else {
    // Monthly view - generate all days in the selected month
    const totalDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1

    for (let i = 0; i < totalDays; i++) {
      const currentDay = new Date(startDate)
      currentDay.setDate(startDate.getDate() + i)
      labels.push(currentDay.toISOString().split('T')[0])

      // Count events for this day
      let occurred = 0
      let upcoming = 0

      const dayStr = currentDay.toISOString().split('T')[0]
      
      if (eventsData.length > 0) {
        eventsData.forEach((event) => {
          const eventDate = new Date(event.start_time)
          const eventDateStr = eventDate.toISOString().split('T')[0]
          
          if (eventDateStr === dayStr) {
            if (eventDate < currentDate) {
              occurred++
            } else {
              upcoming++
            }
          }
        })
      } else {
        // Demo data for month view
        occurred = Math.floor(Math.random() * 5)
        upcoming = Math.floor(Math.random() * 4)
      }

      occurredData.push(occurred)
      upcomingData.push(upcoming)
    }
  }

  return {
    labels,
    datasets: [
      {
        label: 'Actual Results',
        data: occurredData,
        backgroundColor: '#2563EB',
        borderColor: '#2563EB',
        borderWidth: 1,
        hidden: !visibleDatasets.occurred,
      },
      {
        label: 'Predicted Results',
        data: upcomingData,
        backgroundColor: '#93C5FD',
        borderColor: '#93C5FD',
        borderWidth: 1,
        hidden: !visibleDatasets.upcoming,
      },
    ],
  }
}

// Generate Response Chart Data
export const generateResponseChartData = () => {
  return {
    labels: ['Responded', 'Pending', 'Read'],
    datasets: [
      {
        data: [45, 25, 30],
        backgroundColor: [
          '#7789EC',
          '#91D4F6',
          '#F387AF',
        ],
        borderWidth: 2,
        hoverBackgroundColor: ['#A2B0F3', '#B9E4FA', '#F8BFD3'],
        spacing: 8,
        hoverOffset: 15,
      },
    ],
  }
}

// Generate Documents Chart Data
export const generateDocumentsChartData = (documentsData, documentsTimeType, availablePeriods, selectedPeriod) => {
  if (!documentsData.length) return null

  let labels = []
  let uploadData = []
  let readyData = []
  let deleteData = []

  if (documentsTimeType === 'week') {
    // Weekly view
    const { startDate } = getSelectedPeriodDates(availablePeriods, selectedPeriod, documentsTimeType)
    const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    // Generate data for each day of the selected week
    for (let i = 0; i < 7; i++) {
      const currentDay = new Date(startDate)
      currentDay.setDate(startDate.getDate() + i)

      const dayName = daysOfWeek[i]
      const dayNumber = currentDay.getDate()
      labels.push(`${dayName} ${dayNumber}`)

      // Count documents by status for this day
      const dayStr = currentDay.toISOString().split('T')[0]
      const dayDocs = documentsData.filter((doc) => {
        const docDate = new Date(doc.created_at).toISOString().split('T')[0]
        return docDate === dayStr
      })

      const counts = getDocumentCounts(dayDocs)

      uploadData.push(counts.uploaded)
      readyData.push(counts.ready)
      deleteData.push(counts.deleted)
    }
  } else {
    // Monthly view
    const { startDate, endDate } = getSelectedPeriodDates(availablePeriods, selectedPeriod, documentsTimeType)
    const totalDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24))

    for (let i = 0; i < totalDays; i++) {
      const currentDay = new Date(startDate)
      currentDay.setDate(startDate.getDate() + i)

      const dateStr = currentDay.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      labels.push(dateStr)

      // Count documents by status for this day
      const dayStr = currentDay.toISOString().split('T')[0]
      const dayDocs = documentsData.filter((doc) => {
        const docDate = new Date(doc.created_at).toISOString().split('T')[0]
        return docDate === dayStr
      })

      const counts = getDocumentCounts(dayDocs)

      uploadData.push(counts.uploaded)
      readyData.push(counts.ready)
      deleteData.push(counts.deleted)
    }
  }

  // Add demo data if no real data exists
  const hasData =
    uploadData.some((val) => val > 0) ||
    readyData.some((val) => val > 0) ||
    deleteData.some((val) => val > 0)

  // Only add demo data for current period if no real data exists
  if (!hasData && selectedPeriod.endsWith('-0')) {
    if (documentsTimeType === 'week') {
      uploadData.splice(0, 7, 3, 5, 2, 8, 4, 6, 1)
      readyData.splice(0, 7, 2, 3, 4, 5, 3, 4, 2)
      deleteData.splice(0, 7, 1, 1, 0, 2, 1, 1, 0)
    } else {
      const days = uploadData.length
      uploadData.splice(
        0,
        days,
        ...Array.from({ length: days }, () => Math.floor(Math.random() * 8) + 1),
      )
      readyData.splice(
        0,
        days,
        ...Array.from({ length: days }, () => Math.floor(Math.random() * 6) + 1),
      )
      deleteData.splice(
        0,
        days,
        ...Array.from({ length: days }, () => Math.floor(Math.random() * 3)),
      )
    }
  }

  return {
    labels,
    datasets: [
      {
        label: 'Uploaded',
        data: uploadData,
        borderColor: '#42A5F5',
        tension: 0,
        fill: false,
        pointRadius: documentsTimeType === 'week' ? 4 : 2,
        pointHoverRadius: documentsTimeType === 'week' ? 6 : 4,
        borderWidth: 3,
      },
      {
        label: 'Ready',
        data: readyData,
        borderColor: '#B748D2',
        tension: 0,
        fill: false,
        pointRadius: documentsTimeType === 'week' ? 4 : 2,
        pointHoverRadius: documentsTimeType === 'week' ? 6 : 4,
        borderWidth: 3,
      },
      {
        label: 'Deleted',
        data: deleteData,
        borderColor: '#FF0000',
        tension: 0,
        fill: false,
        pointRadius: documentsTimeType === 'week' ? 4 : 2,
        pointHoverRadius: documentsTimeType === 'week' ? 6 : 4,
        borderWidth: 3,
      },
    ],
  }
}

// Calculate Document Statistics
export const calculateDocumentStats = (documentsData, availablePeriods, selectedPeriod, timeType) => {
  if (!documentsData.length) {
    return {
      total: 0,
      uploadPercentage: 0,
      readyPercentage: 0,
      deletePercentage: 0,
      averagePercentage: 0
    }
  }

  // Filter documents based on selected period
  const { startDate, endDate } = getSelectedPeriodDates(availablePeriods, selectedPeriod, timeType)
  const filteredDocs = documentsData.filter((doc) => {
    const docDate = new Date(doc.created_at)
    return docDate >= startDate && docDate <= endDate
  })

  if (filteredDocs.length === 0) {
    return {
      total: 0,
      uploadPercentage: 0,
      readyPercentage: 0,
      deletePercentage: 0,
      averagePercentage: 0
    }
  }

  const counts = getDocumentCounts(filteredDocs)
  const uploadPercentage = Math.round((counts.uploaded / filteredDocs.length) * 100)
  const readyPercentage = Math.round((counts.ready / filteredDocs.length) * 100)
  const deletePercentage = Math.round((counts.deleted / filteredDocs.length) * 100)
  const averagePercentage = Math.round((uploadPercentage + readyPercentage + deletePercentage) / 3)

  return {
    total: filteredDocs.length,
    uploadPercentage,
    readyPercentage,
    deletePercentage,
    averagePercentage
  }
}