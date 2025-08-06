<template>
  <div class="page-wrapper">
    <SideBar />
    
    <main class="main-content">
      <div class="dashboard">
        <!-- Header with Search -->
        <div class="dashboard-header">
          <h1>Welcome back, {{ username }}!</h1>
          <div class="search-bar">
            <v-text-field
              variant="outlined"

              placeholder="Enter your search request..."
              prepend-inner-icon="mdi-magnify"
              hide-details
              density="compact"
              class="search-input"

            />
          </div>
          <div class="header-actions">
            <v-badge :content="notificationCount" color="red" v-if="notificationCount > 0">

              <v-btn icon size="small" class="action-btn">
                <v-icon>mdi-bell-outline</v-icon>
              </v-btn>
            </v-badge>
            <v-btn v-else icon size="small" class="action-btn">
              <v-icon>mdi-bell-outline</v-icon>
            </v-btn>
            <div class="profile-menu" @click="toggleDropdown">
              <v-avatar size="40" class="profile-avatar">
                <v-icon size="large">mdi-account-circle</v-icon>

              </v-avatar>
              <div v-if="showDropdown" class="dropdown">
                <a href="#"><v-icon small>mdi-account</v-icon> Profile</a>
                <a href="#"><v-icon small>mdi-logout</v-icon> Logout</a>
              </div>
            </div>
          </div>
        </div>

        <!-- Stats Cards -->
        <div class="stats-grid">
          <div class="stat-card blue">
            <div class="stat-icon">
              <v-icon>mdi-file-document</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Total Documents</div>
              <div class="stat-number">{{ stats.documents }}</div>
              <div class="stat-change positive">+15% from last week</div>
            </div>
          </div>

          <div class="stat-card green">
            <div class="stat-icon">
              <v-icon>mdi-chat-question</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Questions Answered</div>
              <div class="stat-number">{{ stats.questionsAnswered }}</div>
              <div class="stat-change positive">+8% from last week</div>
            </div>
          </div>

          <div class="stat-card orange">
            <div class="stat-icon">
              <v-icon>mdi-bullhorn</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Upcoming Announcements</div>
              <div class="stat-number">{{ stats.announcements }}</div>
              <div class="stat-meta">{{ stats.scheduledToday }} scheduled today</div>
            </div>
          </div>

          <div class="stat-card red">
            <div class="stat-icon">
              <v-icon>mdi-alert-triangle</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Missed Deadlines</div>
              <div class="stat-number">{{ stats.missedDeadlines }}</div>
              <div class="stat-change negative">+2 from yesterday</div>
            </div>
          </div>
        </div>

        <!-- Main Content Grid -->
        <div class="content-grid">
          <!-- Activity Overview -->
          <div class="activity-section">
            <div class="section-header">
              <h3>Activity Overview</h3>
              <div class="time-filters">
                <v-btn-toggle v-model="timeFilter" mandatory>
                  <v-btn size="small" value="daily">Daily</v-btn>
                  <v-btn size="small" value="weekly">Weekly</v-btn>
                  <v-btn size="small" value="monthly">Monthly</v-btn>
                </v-btn-toggle>
              </div>
            </div>
            <div class="chart-container">
              <DocumentUploadChart 
                :documents="documents"
                :timeFilter="timeFilter"
              />
            </div>
          </div>

          <!-- Calendar -->
          <div class="calendar-section">
            <div class="section-header">
              <h3>Calendar</h3>
              <div class="calendar-nav">
                <v-btn icon size="small" @click="previousMonth">
                  <v-icon>mdi-chevron-left</v-icon>
                </v-btn>
                <span class="calendar-month">{{ currentMonthYear }}</span>
                <v-btn icon size="small" @click="nextMonth">
                  <v-icon>mdi-chevron-right</v-icon>
                </v-btn>
              </div>
            </div>
            <div class="calendar-grid">
              <div class="calendar-weekdays">
                <div v-for="day in weekdays" :key="day" class="weekday">{{ day }}</div>
              </div>
              <div class="calendar-days">
                <div
                  v-for="date in calendarDays"
                  :key="date.date"
                  :class="['calendar-day', {
                    'other-month': !date.isCurrentMonth,
                    'today': date.isToday,
                    'has-events': date.events.length > 0
                  }]"
                  @click="selectDate(date)"
                >
                  <span class="day-number">{{ date.day }}</span>
                  <div v-if="date.events.length > 0" class="event-indicators">
                    <div
                      v-for="event in date.events.slice(0, 3)"
                      :key="event.id"
                      :class="['event-dot', event.type]"
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Today's Events -->
            <div class="todays-events">
              <h4>Today's Events</h4>
              <div v-if="todaysEvents.length === 0" class="no-events">
                No events scheduled for today
              </div>
              <div v-else class="event-list">
                <div
                  v-for="event in todaysEvents"
                  :key="event.id"
                  class="event-item"
                >
                  <div class="event-time">{{ formatEventTime(event.start) }}</div>
                  <div class="event-details">
                    <div class="event-title">{{ event.title }}</div>
                    <div class="event-location" v-if="event.location">{{ event.location }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activities -->
        <div class="recent-activities-section">
          <div class="section-header">
            <h3>Recent Activities</h3>
            <v-btn text color="primary" size="small">View All</v-btn>
          </div>
          <div class="activities-table">
            <div class="table-header">
              <div>TASK/ACTIVITY</div>
              <div>TYPE</div>
              <div>STATUS</div>
              <div>PRIORITY</div>
            </div>
            <div class="table-body">
              <div v-for="activity in recentActivities" :key="activity.id" class="activity-row">
                <div class="activity-task">
                  <div class="task-title">{{ activity.title }}</div>
                  <div class="task-time">{{ activity.timeAgo }}</div>
                </div>
                <div class="activity-type">
                  <v-chip size="small" :color="getTypeColor(activity.type)">
                    {{ activity.type }}
                  </v-chip>
                </div>
                <div class="activity-status">
                  <v-chip size="small" :color="getStatusColor(activity.status)">
                    {{ activity.status }}
                  </v-chip>
                </div>
                <div class="activity-priority">
                  <v-chip size="small" :color="getPriorityColor(activity.priority)">
                    {{ activity.priority }}
                  </v-chip>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>


<script setup>
import { onMounted } from 'vue'
import SideBar from '@/views/SideBar.vue'
import DocumentUploadChart from '@/components/DocumentUploadChart.vue'

// Composables
import {
  useAuth,
  useCalendar,
  useStats,
  useEvents,
  useColors,
  useUI
} from '@/composables'

// Auth composable
const { username, loadUserProfile } = useAuth()

// Calendar composable
const {
  events,
  weekdays,
  currentMonthYear,
  calendarDays,
  todaysEvents,
  formatEventTime,
  previousMonth,
  nextMonth,
  selectDate
} = useCalendar()

// Stats composable
const {
  stats,
  recentActivities,
  documents,
  notificationCount,
  fetchStats
} = useStats()

// Events composable
const { fetchCalendarEvents } = useEvents()

// Colors composable
const {
  getTypeColor,
  getStatusColor,
  getPriorityColor
} = useColors()

// UI composable
const {
  showDropdown,
  timeFilter,
  toggleDropdown,
  setVisible
} = useUI()

// Main data loading function
const loadDashboardData = async () => {
  // Load user profile trước
  await loadUserProfile()
  
  // Fetch calendar events
  const calendarEvents = await fetchCalendarEvents()
  events.value = calendarEvents
  
  // Fetch stats với events data
  await fetchStats(calendarEvents)
}

onMounted(async () => {
  await loadDashboardData()
  
  // Animation cho welcome card
  setTimeout(() => {
    setVisible(true)
  }, 300)
})
</script>

<style>
@import '../assets/db.css';
</style>

<style scoped>

/* Styling cho search bar và header actions */
.search-input :deep(.v-field) {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
}

.search-input :deep(.v-field__input) {
  color: #6c757d;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Notification button với vòng bo tròn */
.action-btn {
  background: #f8f9fa !important;
  border: 1px solid #e9ecef;
  color: #6c757d !important;
  width: 40px;
  height: 40px;
  border-radius: 50% !important;
}

.action-btn:hover {
  background: #e9ecef !important;
  color: #495057 !important;
}

/* Profile avatar */
.profile-avatar {
  cursor: pointer;
  border: 2px solid #e9ecef;
}

.profile-avatar:hover {
  border-color: #3b82f6;
}

.dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  min-width: 150px;
  margin-top: 0.5rem;
}

.dropdown a {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  color: #495057;
  text-decoration: none;
  transition: background-color 0.2s;
}

.dropdown a:hover {
  background: #f8f9fa;
}

</style>
