<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import router from '@/router'
const authStore = useAuthStore()

function logout() {
  authStore.logout()
}

function goToAboutPage() {
  router.push({ name: 'about' })
}

onMounted(() => {
  if (!authStore.isAuthenticated) {
    authStore.logout()
  }
})


</script>

<template>
  
  <v-container class="text-center">
    <v-row justify="center" class="mb-4">
      <v-col cols="12" md="12">
        <h1 class="display-1">Chào mừng đến với hệ thống quản lý học tập</h1>
        <p class="subtitle-1">Hệ thống giúp bạn quản lý việc học tập một cách hiệu quả.</p>
        <v-btn @click="logout" color="error" class="mb-4">
          Logout
        </v-btn>
        <v-btn @click="goToAboutPage" color="primary" class="mb-4">
          Về trang giới thiệu
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>
