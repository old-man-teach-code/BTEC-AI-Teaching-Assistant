<template>
  <div class="page-wrapper">
    <SideBar />
    
    <main class="main-content">
      <div class="dashboard">
        <!-- Header with Search -->

        <DashboardHeader 
          :username="username"
          :notification-count="notificationCount"
          :show-dropdown="showDropdown"
          @toggle-dropdown="toggleDropdown"
          @logout="handleLogout"
        />

        <!-- Stats Cards -->
        <StatsGrid 
          :stats="stats"
          @show-tomorrow-events="showTomorrowEventsModal = true"
        />


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
          <DashboardCalendar
            :current-month-year="currentMonthYear"
            :weekdays="weekdays"
            :calendar-days="calendarDays"
            :todays-events="todaysEvents"
            :format-event-time="formatEventTime"
            @previous-month="previousMonth"
            @next-month="nextMonth"
            @select-date="selectDate"
          />
        </div>

        <!-- Recent Activities -->
        <RecentActivities
          :recent-activities="recentActivities"
          :get-type-color="getTypeColor"
          :get-status-color="getStatusColor"
          :get-priority-color="getPriorityColor"
        />
      </div>
    </main>
    
    <!-- Tomorrow Events Modal -->

    <TomorrowEventsModal
      v-model="showTomorrowEventsModal"
      :tomorrow-events="tomorrowEvents"
      :format-event-time="formatEventTime"
    />
  </div>
</template>


<script setup>
import { onMounted } from 'vue'
import SideBar from '@/views/SideBar.vue'
import DocumentUploadChart from '@/components/DocumentUploadChart.vue'

import DashboardHeader from '@/components/DashboardHeader.vue'
import StatsGrid from '@/components/StatsGrid.vue'
import DashboardCalendar from '@/components/DashboardCalendar.vue'
import RecentActivities from '@/components/RecentActivities.vue'
import TomorrowEventsModal from '@/components/TomorrowEventsModal.vue'

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
