<script setup>
import HeaderForm from '@/components/HeaderForm.vue'
import { ref, computed, onMounted } from 'vue'
import { fetchStats } from '@/api/stats' //
import { useAuthStore } from '@/stores/auth'
import api from '../api/http'

const authStore = useAuthStore()

const username = computed(() => authStore.user?.name || 'Người dùng')

const stats = ref({
  documents: 0,
  questionsAnswered: 30,
  usersJoined: 0,
})

onMounted(async () => {
  // Fetch user
  if (authStore.isAuthenticated && !authStore.user) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      console.error('Failed to fetch user:', error)
    }
  }

  // Fetch stats
  try {
       const data = await fetchStats()
    Object.assign(stats.value, data)
  } catch (error) {
     console.error('Lỗi khi fetch stats:', error)
  }
})

const fetchDocumentStats = async () => {
  try {
    const res = await api.get('/api/documents')
    stats.value.documents = res.data.items.filter(doc => doc.status === 'uploaded').length
  } catch (e) {
    console.error('Failed to fetch documents', e)
    stats.value.documents = 0
  }
}

onMounted(fetchDocumentStats)
</script>

<template>
  <HeaderForm>
    <v-container class="pt-10">
      <v-row justify="center">
        <v-col cols="12" class="text-center">
          <h1 class="text-h4 font-weight-bold">Welcome back, {{ username }}!</h1>
          <p class="text-subtitle-1">Have a wonderful and productive day!</p>
        </v-col>
      </v-row>
    </v-container>

    <v-container fluid class="py-6">
      <v-row justify="center" align="center">
        <v-col cols="12" sm="4">
          <v-card elevation="3" class="pa-6 text-center rounded-xl">
            <i class="fas fa-file-alt" style="font-size:36px; color: #1976d2;"></i>
            <div class="text-h5 font-weight-bold mt-2">{{ stats.documents }}</div>
            <div class="text-subtitle-2">Posted Documents</div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="4">
          <v-card elevation="3" class="pa-6 text-center rounded-xl">
            <i class="fas fa-question-circle" style="font-size:36px; color: #2e7d32;"></i>
            <div class="text-h5 font-weight-bold mt-2">{{ stats.questionsAnswered }}</div>
            <div class="text-subtitle-2">Answered Questions</div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="4">
          <v-card elevation="3" class="pa-6 text-center rounded-xl">
            <i class="fas fa-users" style="font-size:36px; color: #3f51b5;"></i>
            <div class="text-h5 font-weight-bold mt-2">{{ stats.usersJoined }}</div>
            <span class="text-subtitle-2">Joined Users</span>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

  <v-container fluid class="py-10" style="background-color: #fff8f1;">
    <v-row align="center" justify="space-between">
      <!-- Cột ảnh -->
      <v-col cols="12" md="5" class="text-center">
        <v-img
 src="https://www.jobsterritory.com/images/raas-hero.png"
          max-width="600"
          contain
        ></v-img>
      </v-col>

      <!-- Cột nội dung -->
      <v-col cols="12" md="6">
        <blockquote style="font-size: 26px; font-weight: 600; line-height: 1.4;">
          “However difficult life may seem, there is
          <strong style="color: #ff7300;">always something you can do</strong>
          and <strong>succeed at.</strong>”
        </blockquote>
        <div class="text-right text-grey-darken-2 mt-2 font-weight-medium">– STEVEN HAWKING</div>
      </v-col>
    </v-row>
  </v-container>
  </HeaderForm>
</template> 
<script>
</script>