<template>
  <div class="chart-container">
    <Line
      :data="chartData"
      :options="chartOptions"
      :height="300"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  documents: {
    type: Array,
    default: () => []
  },
  timeFilter: {
    type: String,
    default: 'weekly'
  }
})

// Process data based on time filter
const chartData = computed(() => {
  const now = new Date()
  let labels = []
  let data = []
  
  if (props.timeFilter === 'daily') {
    // Last 7 days
    for (let i = 6; i >= 0; i--) {
      const date = new Date(now)
      date.setDate(date.getDate() - i)
      const dateStr = date.toISOString().split('T')[0]
      labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }))
      
      const count = props.documents.filter(doc => {
        const docDate = new Date(doc.created_at).toISOString().split('T')[0]
        return docDate === dateStr
      }).length
      
      data.push(count)
    }
  } else if (props.timeFilter === 'weekly') {
    // Last 8 weeks
    for (let i = 7; i >= 0; i--) {
      const startOfWeek = new Date(now)
      startOfWeek.setDate(startOfWeek.getDate() - (startOfWeek.getDay() + i * 7))
      const endOfWeek = new Date(startOfWeek)
      endOfWeek.setDate(endOfWeek.getDate() + 6)
      
      labels.push(`Week ${Math.ceil((now.getTime() - startOfWeek.getTime()) / (1000 * 60 * 60 * 24 * 7))}`)
      
      const count = props.documents.filter(doc => {
        const docDate = new Date(doc.created_at)
        return docDate >= startOfWeek && docDate <= endOfWeek
      }).length
      
      data.push(count)
    }
  } else if (props.timeFilter === 'monthly') {
    // Last 6 months
    for (let i = 5; i >= 0; i--) {
      const monthStart = new Date(now.getFullYear(), now.getMonth() - i, 1)
      const monthEnd = new Date(now.getFullYear(), now.getMonth() - i + 1, 0)
      
      labels.push(monthStart.toLocaleDateString('en-US', { month: 'short' }))
      
      const count = props.documents.filter(doc => {
        const docDate = new Date(doc.created_at)
        return docDate >= monthStart && docDate <= monthEnd
      }).length
      
      data.push(count)
    }
  }
  
  return {
    labels,
    datasets: [
      {
        label: 'Documents Uploaded',
        data,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#3b82f6',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
        pointHoverBackgroundColor: '#1d4ed8',
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 3
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#ffffff',
      bodyColor: '#ffffff',
      borderColor: '#3b82f6',
      borderWidth: 1,
      cornerRadius: 8,
      displayColors: false,
      callbacks: {
        title: (context) => {
          return `${context[0].label}`
        },
        label: (context) => {
          const count = context.parsed.y
          return `${count} document${count !== 1 ? 's' : ''} uploaded`
        }
      }
    }
  },
  scales: {
    x: {
      grid: {
        display: false
      },
      border: {
        display: false
      },
      ticks: {
        color: '#6b7280',
        font: {
          size: 12,
          weight: '500'
        }
      }
    },
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(107, 114, 128, 0.1)',
        borderDash: [5, 5]
      },
      border: {
        display: false
      },
      ticks: {
        color: '#6b7280',
        font: {
          size: 12,
          weight: '500'
        },
        callback: function(value) {
          return Number.isInteger(value) ? value : ''
        }
      }
    }
  },
  elements: {
    point: {
      hoverBackgroundColor: '#1d4ed8'
    }
  },
  interaction: {
    intersect: false,
    mode: 'index'
  }
}))
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 300px;
}
</style>
