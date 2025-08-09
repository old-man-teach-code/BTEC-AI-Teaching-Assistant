<template>
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
</template>

<script setup>
defineProps({
  recentActivities: Array,
  getTypeColor: Function,
  getStatusColor: Function,
  getPriorityColor: Function
})
</script>
