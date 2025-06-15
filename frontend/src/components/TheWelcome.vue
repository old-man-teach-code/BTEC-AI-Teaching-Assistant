<script setup>

import { useAuthStore } from '../stores/auth'
const authStore = useAuthStore()
function logout() {
  authStore.logout()
}
</script>

<template>
  <main>
    <v-container class="text-center">
      <v-row justify="center" class="mb-4">
        <v-col cols="12" md="8">
          <h1 class="display-1">Chào mừng đến với hệ thống quản lý học tập</h1>
          <p class="subtitle-1">Hệ thống giúp bạn quản lý việc học tập một cách hiệu quả.</p>
          <v-btn @click="logout" color="error" class="mb-4">
            Logout
          </v-btn>
        </v-col>
      </v-row>
      <v-row justify="center">
        <v-col cols="8">

        </v-col>
      </v-row>
    </v-container>
  </main>
</template>
