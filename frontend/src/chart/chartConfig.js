// chartConfig.js
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
)

// Chart Options Configuration
export const eventsChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  aspectRatio: 4,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: {
      position: 'top',
      labels: {
        usePointStyle: true,
        padding: 15,
        font: { size: 11 },
        generateLabels: function(chart) {
          const datasets = chart.data.datasets
          return datasets.map((dataset, i) => ({
            text: dataset.label,
            fillStyle: dataset.backgroundColor,
            strokeStyle: dataset.backgroundColor,
            lineWidth: 0,
            pointStyle: 'rect',
            hidden: dataset.hidden,
            datasetIndex: i
          }))
        }
      },
      onClick: function(e, legendItem) {
        const index = legendItem.datasetIndex
        const chart = this.chart
        const meta = chart.getDatasetMeta(index)
        
        meta.hidden = meta.hidden === null ? !chart.data.datasets[index].hidden : null
        
        const datasetKeys = ['occurred', 'upcoming']
        // This needs to be handled in the component
        chart.update()
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: 'white',
      bodyColor: 'white',
      borderColor: 'rgba(255, 255, 255, 0.3)',
      borderWidth: 1,
      callbacks: {
        title: function(context) {
          const date = new Date(context[0].label)
          return date.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })
        },
        label: function(context) {
          return `${context.dataset.label}: ${context.parsed.y} events`
        }
      }
    },
  },
  scales: {
    x: { 
      stacked: true,
      grid: { display: false },
      ticks: {
        callback: function(value, index) {
          const date = new Date(this.getLabelForValue(value))
          const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
          const dayName = daysOfWeek[date.getDay()]
          return `${dayName} ${date.getDate()}`
        },
        maxRotation: 45,
        minRotation: 0
      }
    },
    y: { 
      stacked: true,
      beginAtZero: true, 
      ticks: { 
        stepSize: 1,
        callback: function(value) {
          return value + ' events'
        }
      },
    },
  },
}

export const responseChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right',
      align: 'center',
      labels: {
        usePointStyle: true,
        padding: 20,
        font: { size: 12 },
        generateLabels: function(chart) {
          const data = chart.data;
          if (data.labels.length && data.datasets.length) {
            const dataset = data.datasets[0];
            const total = dataset.data.reduce((sum, val) => sum + val, 0);
            return data.labels.map((label, i) => {
              const value = dataset.data[i];
              const percentage = Math.round((value / total) * 100);
              return {
                text: `${label} ${percentage}%`,
                fillStyle: dataset.backgroundColor[i],
                strokeStyle: dataset.backgroundColor[i],
                lineWidth: 0,
                pointStyle: 'circle'
              };
            });
          }
          return [];
        }
      },
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: 'white',
      bodyColor: 'white',
      borderColor: 'rgba(255, 255, 255, 0.3)',
      borderWidth: 1,
      callbacks: {
        label: function(context) {
          const total = context.dataset.data.reduce((sum, val) => sum + val, 0)
          const percentage = Math.round((context.parsed / total) * 100)
          return `${context.label}: ${context.parsed} (${percentage}%)`
        }
      }
    },
  },
  cutout: '50%',
  radius: '90%',
  elements: {
    arc: {
      borderWidth: 3,
      borderColor: '#ffffff',
    }
  },
}

export const documentsChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      labels: {
        usePointStyle: true,
        padding: 15,
        font: { size: 12 },
        generateLabels: function(chart) {
          const datasets = chart.data.datasets;
          return datasets.map((dataset) => ({
            text: dataset.label,
            fillStyle: dataset.borderColor,
            strokeStyle: dataset.borderColor,
            lineWidth: 0,
            pointStyle: 'circle'
          }));
        }
      },
    },
    tooltip: {
      mode: 'index',
      intersect: false,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: 'white',
      bodyColor: 'white',
      borderColor: 'rgba(255, 255, 255, 0.3)',
      borderWidth: 1,
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: {
        font: { size: 11 },
      },
    },
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 1,
        font: { size: 11 },
      },
      grid: {
        color: 'rgba(0, 0, 0, 0.1)',
      },
    },
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false,
  },
}