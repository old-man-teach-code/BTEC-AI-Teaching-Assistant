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
                <a href="#" @click.prevent="handleLogout"><v-icon small>mdi-logout</v-icon> Logout</a>
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

          <div class="stat-card orange" @click="showTomorrowEventsModal = true" style="cursor: pointer;">
            <div class="stat-icon">
              <v-icon>mdi-bullhorn</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Upcoming Announcements</div>
              <div class="stat-number">{{ stats.announcements }}</div>
              <div class="stat-meta">{{ stats.announcementMessage }}</div>
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
    
    <!-- Tomorrow Events Modal -->
    <v-dialog v-model="showTomorrowEventsModal" max-width="600px">
      <v-card>
        <v-card-title class="text-h5 pa-4 d-flex justify-center align-center">
          <v-icon class="mr-2">mdi-calendar-tomorrow</v-icon>
          Tomorrow's Events
        </v-card-title>
        
        <v-divider></v-divider>
        
        <v-card-text class="pa-4">
          <div v-if="tomorrowEvents.length === 0" class="text-center py-8">
            <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-calendar-blank</v-icon>
            <p class="text-h6 text-grey">No events scheduled for tomorrow</p>
          </div>
          
          <div v-else class="events-list">
            <div
              v-for="event in tomorrowEvents"
              :key="event.id"
              class="event-item-modal mb-3"
            >
              <div class="d-flex align-center">
                <v-icon class="mr-3" color="primary">mdi-clock-outline</v-icon>
                <div class="flex-grow-1">
                  <div class="text-h6">{{ event.title }}</div>
                  <div class="text-body-2 text-grey">
                    {{ formatEventTime(event.start) }}
                    <span v-if="event.location" class="ml-2">
                      <v-icon size="small">mdi-map-marker</v-icon>
                      {{ event.location }}
                    </span>
                  </div>
                  <div v-if="event.description" class="text-body-2 mt-1">
                    {{ event.description }}
                  </div>
                </div>
              </div>
              <v-divider v-if="event !== tomorrowEvents[tomorrowEvents.length - 1]" class="mt-3"></v-divider>
            </div>
          </div>
        </v-card-text>
        
        <v-divider></v-divider>
        
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            variant="text"
            @click="showTomorrowEventsModal = false"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>


<script setup>
import { onMounted } from 'vue'
import SideBar from '@/views/SideBar.vue'
import DocumentUploadChart from '@/components/DocumentUploadChart.vue'
import { useHomeDashboard } from '@/composables'

// Use the HomeDashboard composable
const {
  // State
  showTomorrowEventsModal,
  username,
  weekdays,
  currentMonthYear,
  calendarDays,
  todaysEvents,
  stats,
  recentActivities,
  documents,
  notificationCount,
  tomorrowEvents,
  showDropdown,
  timeFilter,

  // Methods
  formatEventTime,
  previousMonth,
  nextMonth,
  selectDate,
  getTypeColor,
  getStatusColor,
  getPriorityColor,
  toggleDropdown,
  handleLogout,
  initDashboard
} = useHomeDashboard()

onMounted(async () => {
  await initDashboard()
})
</script>

<style>
@import '../assets/db.css';
@import '../assets/home-dashboard.css';
</style>
