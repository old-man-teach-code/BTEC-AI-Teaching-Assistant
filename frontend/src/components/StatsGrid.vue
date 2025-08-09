<template>
  <div class="stats-grid">
    <div class="stat-card blue">
      <div class="stat-icon">
        <v-icon>mdi-file-document</v-icon>
      </div>
      <div class="stat-content">
        <div class="stat-label">Total Documents</div>
        <div class="stat-number">{{ stats.documents }}</div>
        <div class="stat-change" :class="(stats.documentGrowth || 0) >= 0 ? 'positive' : 'negative'">
          {{ (stats.documentGrowth || 0) >= 0 ? '+' : '' }}{{ stats.documentGrowth || 0 }}% from last week
        </div>
      </div>
    </div>

    <div class="stat-card green">
      <div class="stat-icon">
        <v-icon>mdi-chat-question</v-icon>
      </div>
      <div class="stat-content">
        <div class="stat-label">Questions Answered</div>
        <div class="stat-number">{{ stats.questionsAnswered }}</div>
        <div class="stat-change positive">Ready to answer questions</div>
      </div>
    </div>

    <div class="stat-card orange" @click="$emit('show-tomorrow-events')" style="cursor: pointer;">
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
</template>

<script setup>
defineProps({
  stats: Object
})

defineEmits(['show-tomorrow-events'])
</script>
