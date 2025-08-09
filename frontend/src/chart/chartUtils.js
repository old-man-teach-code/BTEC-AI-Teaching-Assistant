// chartUtils.js
// Helper function to count documents by status
export const getDocumentCounts = (docs) => {
  return {
    uploaded: docs.filter((doc) => doc.status === 'uploaded').length,
    ready: docs.filter((doc) => 
      doc.status === 'ready' || 
      doc.status === 'completed' || 
      doc.status === 'processed'
    ).length,
    deleted: docs.filter((doc) => 
      doc.status === 'deleted' || 
      doc.status === 'removed' || 
      doc.is_deleted === true
    ).length
  }
}

// Helper function to get available periods based on time type
export const generatePeriods = (timeType) => {
  const today = new Date()
  
  if (timeType === 'week') {
    // Generate last 8 weeks
    const weeks = []
    
    for (let i = 0; i < 8; i++) {
      const weekStart = new Date(today)
      weekStart.setDate(today.getDate() - (today.getDay() + i * 7))
      weekStart.setHours(0, 0, 0, 0)

      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)

      const startDay = weekStart.getDate()
      const endDay = weekEnd.getDate()
      const month = weekStart.toLocaleDateString('en-US', { month: 'short' })

      weeks.push({
        value: `week-${i}`,
        label: i === 0 ? 'This Week' : i === 1 ? 'Last Week' : `${month} ${startDay}-${endDay}`,
        startDate: new Date(weekStart),
        endDate: new Date(weekEnd),
      })
    }
    return weeks
  } else {
    // Generate last 12 months
    const months = []
    
    for (let i = 0; i < 12; i++) {
      const monthDate = new Date(today.getFullYear(), today.getMonth() - i, 1)
      const monthName = monthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
      const monthStart = new Date(monthDate.getFullYear(), monthDate.getMonth(), 1)
      const monthEnd = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0)

      months.push({
        value: `month-${i}`,
        label: i === 0 ? 'This Month' : i === 1 ? 'Last Month' : monthName,
        startDate: monthStart,
        endDate: monthEnd,
      })
    }
    return months
  }
}

// Helper function to generate Events periods (Monday to Sunday)
export const generateEventsPeriods = (timeType) => {
  const today = new Date()
  
  if (timeType === 'week') {
    // Generate last 8 weeks (Monday to Sunday)
    const weeks = []
    
    for (let i = 0; i < 8; i++) {
      // Calculate Monday of the week (Monday = 1, Sunday = 0)
      const monday = new Date(today)
      const dayOfWeek = today.getDay()
      const daysFromMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1
      monday.setDate(today.getDate() - daysFromMonday - (i * 7))
      monday.setHours(0, 0, 0, 0)

      const sunday = new Date(monday)
      sunday.setDate(monday.getDate() + 6)

      const startDay = monday.getDate()
      const endDay = sunday.getDate()
      const month = monday.toLocaleDateString('en-US', { month: 'short' })

      weeks.push({
        value: `week-${i}`,
        label: i === 0 ? 'This Week' : i === 1 ? 'Last Week' : `${month} ${startDay}-${endDay}`,
        startDate: new Date(monday),
        endDate: new Date(sunday),
      })
    }
    return weeks
  } else {
    // Generate last 12 months
    const months = []
    
    for (let i = 0; i < 12; i++) {
      const monthDate = new Date(today.getFullYear(), today.getMonth() - i, 1)
      const monthName = monthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
      const monthStart = new Date(monthDate.getFullYear(), monthDate.getMonth(), 1)
      const monthEnd = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0)

      months.push({
        value: `month-${i}`,
        label: i === 0 ? 'This Month' : i === 1 ? 'Last Month' : monthName,
        startDate: monthStart,
        endDate: monthEnd,
      })
    }
    return months
  }
}

// Helper function to get selected period dates
export const getSelectedPeriodDates = (availablePeriods, selectedPeriod, timeType) => {
  const period = availablePeriods.find((p) => p.value === selectedPeriod)
  if (period) {
    return {
      startDate: period.startDate,
      endDate: period.endDate,
    }
  }

  // Fallback to current period
  const today = new Date()
  if (timeType === 'week') {
    const startOfWeek = new Date(today)
    startOfWeek.setDate(today.getDate() - today.getDay())
    startOfWeek.setHours(0, 0, 0, 0)
    const endOfWeek = new Date(startOfWeek)
    endOfWeek.setDate(startOfWeek.getDate() + 6)
    return { startDate: startOfWeek, endDate: endOfWeek }
  } else {
    const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
    const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)
    return { startDate: startOfMonth, endDate: endOfMonth }
  }
}

// Helper function to get Events selected period dates (Monday to Sunday)
export const getEventsSelectedPeriodDates = (availablePeriods, selectedPeriod, timeType) => {
  const period = availablePeriods.find((p) => p.value === selectedPeriod)
  if (period) {
    return {
      startDate: period.startDate,
      endDate: period.endDate,
    }
  }

  // Fallback to current period (Monday to Sunday)
  const today = new Date()
  if (timeType === 'week') {
    const dayOfWeek = today.getDay()
    const daysFromMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1
    const monday = new Date(today)
    monday.setDate(today.getDate() - daysFromMonday)
    monday.setHours(0, 0, 0, 0)
    const sunday = new Date(monday)
    sunday.setDate(monday.getDate() + 6)
    return { startDate: monday, endDate: sunday }
  } else {
    const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
    const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)
    return { startDate: startOfMonth, endDate: endOfMonth }
  }
}

// Debounce utility
export const createDebounce = () => {
  let timeout = null
  
  return (callback, delay = 1000, reason = 'unknown') => {
    console.log(`[Debounce] Request: ${reason}`)
    if (timeout) {
      console.log('[Debounce] Clearing previous timeout')
      clearTimeout(timeout)
    }
    timeout = setTimeout(() => {
      console.log(`🔄 [Debounce] Executing: ${reason}`)
      callback()
      timeout = null
    }, delay)
  }
}