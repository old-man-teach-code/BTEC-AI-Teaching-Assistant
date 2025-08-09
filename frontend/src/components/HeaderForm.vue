<template>
  <v-app>
    <!-- Navigation Bar -->
    <v-app-bar app color="primary" dark>
      <v-toolbar-title>BTEC AI Teaching Assistant</v-toolbar-title>
      
      <v-spacer></v-spacer>
      
      <v-btn text to="/dashboardhome">Dashboard</v-btn>
      <v-btn text to="/documents">Documents</v-btn>
      <v-btn text to="/calendar">Calendar</v-btn>
      <v-btn text to="/settings">Settings</v-btn>
    </v-app-bar>

    <!-- Main Content -->
    <v-main>
      <slot></slot>
    </v-main>

    <!-- Footer -->
    <v-footer app color="grey lighten-3" class="text-center">
      <span>&copy; 2025 BTEC AI Teaching Assistant</span>
    </v-footer>
  </v-app>
</template>

<script setup>
// Simple layout component with header, main content slot, and footer
</script>

<style scoped>
.v-app-bar {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
