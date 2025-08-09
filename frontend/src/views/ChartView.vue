<template>
  <div class="page-wrapper">
    <SideBar />

    <main class="main-content">
      <div class="dashboard">
        <!-- Charts Grid Layout -->
        <div class="charts-grid">
          <!-- Top Row -->
          <div class="top-row">
            <!-- Chart 1 - Events (Top Left) -->
            <div class="chart-card chart-events">
              <div class="chart-card-header">
                <div class="chart-title-section">
                  <h3 class="chart-card-title">
                    <i class="mdi mdi-calendar"></i>
                    Events
                  </h3>
                </div>
                <div class="events-controls">
                  <div class="events-stats">
                    <span class="stat-item">
                      {{ eventsCurrentPeriodLabel }}
                    </span>
                  </div>
                  <div class="filter-controls">
                    <!-- Time Range Type Selector -->
                    <div class="filter-dropdown">
                      <select
                        v-model="eventsTimeType"
                        @change="onEventsTimeTypeChange"
                        class="time-type-select"
                      >
                        <option value="week">Week</option>
                        <option value="month">Month</option>
                      </select>
                      <i class="mdi mdi-chevron-down dropdown-icon"></i>
                    </div>

                    <!-- Specific Period Selector -->
                    <div class="filter-dropdown">
                      <select
                        v-model="eventsSelectedPeriod"
                        @change="updateEventsChart"
                        class="period-select"
                      >
                        <option
                          v-for="period in eventsAvailablePeriods"
                          :key="period.value"
                          :value="period.value"
                        >
                          {{ period.label }}
                        </option>
                      </select>
                      <i class="mdi mdi-chevron-down dropdown-icon"></i>
                    </div>
                  </div>
                </div>
              </div>
              <div class="chart-wrapper">
                <Bar
                  v-if="eventsChartData && eventsChartData.datasets"
                  :data="eventsChartData"
                  :options="eventsChartOptionsWithHandler"
                  ref="eventsChart"
                />
                <div v-else class="loading-state">
                  <i class="mdi mdi-loading mdi-spin"></i>
                  <p>Loading events data...</p>
                </div>
              </div>
            </div>

            <!-- Chart 2 - Response (Top Right) -->
            <div class="chart-card chart-response">
              <div class="chart-card-header">
                <h3 class="chart-card-title">
                  <i class="mdi mdi-message-reply"></i>
                  Response
                </h3>
              </div>
              <div class="chart-wrapper">
                <Doughnut
                  v-if="responseChartData && responseChartData.datasets"
                  :data="responseChartData"
                  :options="responseChartOptions"
                  ref="responseChart"
                />
                <div v-else class="loading-state">
                  <i class="mdi mdi-loading mdi-spin"></i>
                  <p>Loading response data...</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom Row -->
          <div class="bottom-row">
            <!-- Chart 3 - Documents (Bottom Left) -->
            <div class="chart-card chart-documents">
              <div class="chart-card-header">
                <h3 class="chart-card-title">
                  <i class="mdi mdi-file-document-outline"></i>
                  Documents
                </h3>
                <div class="documents-controls">
                  <div class="documents-stats">
                    <span class="stat-item">
                      Total: {{ documentStats.total }} | {{ currentPeriodLabel }}
                    </span>
                  </div>
                  <div class="filter-controls">
                    <!-- Time Range Type Selector -->
                    <div class="filter-dropdown">
                      <select
                        v-model="documentsTimeType"
                        @change="onTimeTypeChange"
                        class="time-type-select"
                      >
                        <option value="week">Week</option>
                        <option value="month">Month</option>
                      </select>
                      <i class="mdi mdi-chevron-down dropdown-icon"></i>
                    </div>

                    <!-- Specific Period Selector -->
                    <div class="filter-dropdown">
                      <select
                        v-model="selectedPeriod"
                        @change="updateDocumentsChart"
                        class="period-select"
                      >
                        <option
                          v-for="period in availablePeriods"
                          :key="period.value"
                          :value="period.value"
                        >
                          {{ period.label }}
                        </option>
                      </select>
                      <i class="mdi mdi-chevron-down dropdown-icon"></i>
                    </div>
                  </div>
                </div>
              </div>
              <div class="chart-wrapper">
                <Line
                  v-if="documentsChartData && documentsChartData.datasets"
                  :data="documentsChartData"
                  :options="documentsChartOptions"
                  ref="documentsChart"
                />
                <div v-else class="loading-state">
                  <i class="mdi mdi-loading mdi-spin"></i>
                  <p>Loading documents data...</p>
                </div>
              </div>
            </div>

            <!-- Active Document Stats (Bottom Right) -->
            <div class="stats-panel">
              <div class="stats-header">
                <h3 class="stats-title">Active Document</h3>
                <p class="stats-subtitle">Average {{ documentStats.averagePercentage }}% Document</p>
              </div>

              <div class="stats-content">
                <div class="stat-row">
                  <span class="stat-label">Upload</span>
                  <div class="stat-bar">
                    <div
                      class="stat-progress upload"
                      :style="{ width: documentStats.uploadPercentage + '%' }"
                    ></div>
                  </div>
                  <span class="stat-value">{{ documentStats.uploadPercentage }}%</span>
                </div>

                <div class="stat-row">
                  <span class="stat-label">Ready</span>
                  <div class="stat-bar">
                    <div
                      class="stat-progress ready"
                      :style="{ width: documentStats.readyPercentage + '%' }"
                    ></div>
                  </div>
                  <span class="stat-value">{{ documentStats.readyPercentage }}%</span>
                </div>

                <div class="stat-row">
                  <span class="stat-label">Delete</span>
                  <div class="stat-bar">
                    <div
                      class="stat-progress delete"
                      :style="{ width: documentStats.deletePercentage + '%' }"
                    ></div>
                  </div>
                  <span class="stat-value">{{ documentStats.deletePercentage }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Refresh Button -->
        <div class="chart-actions">
          <button @click="refreshData" class="refresh-btn" :disabled="loading">
            <i class="mdi mdi-refresh" :class="{ 'mdi-spin': loading }"></i>
            {{ loading ? 'Loading...' : 'Refresh Data' }}
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { Bar, Doughnut, Line } from 'vue-chartjs'
import SideBar from '@/views/SideBar.vue'

// Import our separated modules
import { eventsChartOptions, responseChartOptions, documentsChartOptions } from '../chart/chartConfig.js'
import { generatePeriods, generateEventsPeriods } from '../chart/chartUtils.js'
import { 
  generateEventsChartData, 
  generateResponseChartData, 
  generateDocumentsChartData,
  calculateDocumentStats 
} from '../chart/chartData.js'
import { refreshAllData } from '../chart/chartApi.js'
import { ChartEventHandler, createChartUpdateHandlers } from '../chart/chartEvents.js'

// Register Chart.js components (done in chartConfig.js)

// Reactive data
const loading = ref(false)
const eventsData = ref([])
const documentsData = ref([])

// Filter states
const documentsTimeType = ref('week')
const selectedPeriod = ref('current')
const eventsTimeType = ref('week')
const eventsSelectedPeriod = ref('week-0')
const visibleDatasets = ref({
  occurred: true,
  upcoming: true
})

// Charts refs
const eventsChart = ref(null)
const responseChart = ref(null)
const documentsChart = ref(null)

// Computed: Available periods
const availablePeriods = computed(() => generatePeriods(documentsTimeType.value))
const eventsAvailablePeriods = computed(() => generateEventsPeriods(eventsTimeType.value))

// Computed: Current period labels
const currentPeriodLabel = computed(() => {
  const period = availablePeriods.value.find((p) => p.value === selectedPeriod.value)
  return period ? period.label : documentsTimeType.value === 'week' ? 'This Week' : 'This Month'
})

const eventsCurrentPeriodLabel = computed(() => {
  const period = eventsAvailablePeriods.value.find((p) => p.value === eventsSelectedPeriod.value)
  return period ? period.label : eventsTimeType.value === 'week' ? 'This Week' : 'This Month'
})

// Computed: Chart Data
const eventsChartData = computed(() => 
  generateEventsChartData(
    eventsData.value, 
    eventsTimeType.value, 
    eventsAvailablePeriods.value, 
    eventsSelectedPeriod.value, 
    visibleDatasets.value
  )
)

const responseChartData = computed(() => generateResponseChartData())

const documentsChartData = computed(() => 
  generateDocumentsChartData(
    documentsData.value,
    documentsTimeType.value,
    availablePeriods.value,
    selectedPeriod.value
  )
)

// Computed: Document Statistics
const documentStats = computed(() => 
  calculateDocumentStats(
    documentsData.value,
    availablePeriods.value,
    selectedPeriod.value,
    documentsTimeType.value
  )
)

// Events chart options with legend click handler
const eventsChartOptionsWithHandler = computed(() => ({
  ...eventsChartOptions,
  plugins: {
    ...eventsChartOptions.plugins,
    legend: {
      ...eventsChartOptions.plugins.legend,
      onClick: function(e, legendItem) {
        const index = legendItem.datasetIndex
        const chart = this.chart
        const meta = chart.getDatasetMeta(index)
        
        // Toggle dataset visibility
        meta.hidden = meta.hidden === null ? !chart.data.datasets[index].hidden : null
        
        // Update visibleDatasets ref
        const datasetKeys = ['occurred', 'upcoming']
        visibleDatasets.value[datasetKeys[index]] = !meta.hidden
        
        chart.update()
      }
    }
  }
}))

// Main refresh function
const refreshData = async () => {
  loading.value = true
  try {
    const { eventsData: newEventsData, documentsData: newDocumentsData } = await refreshAllData()
    eventsData.value = newEventsData
    documentsData.value = newDocumentsData
  } catch (error) {
    console.error('Failed to refresh data:', error)
  } finally {
    loading.value = false
  }
}

// Create chart update handlers
const chartsRefs = { eventsChart, responseChart, documentsChart }
const {
  onEventsTimeTypeChange: handleEventsTimeTypeChange,
  updateEventsChart: handleUpdateEventsChart,
  onTimeTypeChange: handleTimeTypeChange,
  updateDocumentsChart: handleUpdateDocumentsChart
} = createChartUpdateHandlers(chartsRefs, availablePeriods, eventsAvailablePeriods)

// Method handlers
const onEventsTimeTypeChange = () => {
  handleEventsTimeTypeChange(eventsTimeType.value, (period) => {
    eventsSelectedPeriod.value = period
  })
}

const updateEventsChart = () => {
  handleUpdateEventsChart(eventsSelectedPeriod.value)
}

const onTimeTypeChange = () => {
  handleTimeTypeChange(documentsTimeType.value, (period) => {
    selectedPeriod.value = period
  })
}

const updateDocumentsChart = () => {
  handleUpdateDocumentsChart(selectedPeriod.value)
}

// Event handler instance
let eventHandler = null

// Lifecycle
onMounted(async () => {
  console.log('ChartView mounted - Loading data...')
  
  // Initialize event handler
  eventHandler = new ChartEventHandler(refreshData)
  eventHandler.registerEventListeners()
  
  // Load initial data
  await refreshData()
  
  // Set initial selected periods
  selectedPeriod.value = documentsTimeType.value === 'week' ? 'week-0' : 'month-0'
  eventsSelectedPeriod.value = eventsTimeType.value === 'week' ? 'week-0' : 'month-0'
})

onUnmounted(() => {
  // Clean up event listeners
  if (eventHandler) {
    eventHandler.unregisterEventListeners()
    eventHandler = null
  }
})
</script>

<style scoped src="../assets/chart.css"></style>