<script setup>
import HeaderForm from '@/components/HeaderForm.vue'
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { fetchStats } from '@/api/stats' //


const authStore = useAuthStore()


const username = computed(() => authStore.user?.name || 'Người dùng')

const stats = ref({
  documents: 0,
  questionsAnswered: 30,
  usersJoined: 0,
})

onMounted(async () => {
  // Fetch user nếu chưa có
  if (authStore.isAuthenticated && !authStore.user) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      console.error('Failed to fetch user:', error)
    }
  }

 
  try {
    const data = await fetchStats()
    Object.assign(stats.value, data)
  } catch (error) {
    console.error('Lỗi khi fetch stats:', error)
  }
})
</script>

<template>
  <HeaderForm>
    <!-- Lời chào -->
    <v-container class="pt-10 pa-4 pa-sm-6 pa-md-10">
      <v-row justify="center">
        <v-col cols="12" class="text-center">
          <h1 class="text-h6 text-sm-h5 text-md-h4 font-weight-bold">
            Welcome back, {{ username }}!
          </h1>
          <p class="text-body-2 text-sm-subtitle-2 text-md-subtitle-1">
            Chúc bạn một ngày tuyệt vời và năng suất!
          </p>
        </v-col>
      </v-row>
    </v-container>


    <v-container fluid class="py-6">
      <v-row justify="center" align="center">
        <v-col cols="12" sm="4">
          <v-card elevation="3" class="pa-6 text-center rounded-xl">
            <i class="fas fa-file-alt" style="font-size:36px; color: #1976d2;"></i>
            <div class="text-h5 font-weight-bold mt-2">{{ stats.documents }}</div>
            <div class="text-subtitle-2">Tài liệu đã đăng</div>

          </v-card>
        </v-col>
      </v-row>
    </v-container>


        <v-col cols="12" sm="4">
          <v-card elevation="3" class="pa-6 text-center rounded-xl">
            <i class="fas fa-question-circle" style="font-size:36px; color: #2e7d32;"></i>
            <div class="text-h5 font-weight-bold mt-2">{{ stats.questionsAnswered }}</div>
            <div class="text-subtitle-2">Câu hỏi đã trả lời</div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="4">
          <v-card elevation="3" class="pa-6 text-center rounded-xl">
            <i class="fas fa-users" style="font-size:36px; color: #3f51b5;"></i>
            <div class="text-h5 font-weight-bold mt-2">{{ stats.usersJoined }}</div>
            <span class="text-subtitle-2">Người dùng tham gia</span>
          </v-card>

        </v-col>
      </v-row>
    </v-container>
  </HeaderForm>
</template>
