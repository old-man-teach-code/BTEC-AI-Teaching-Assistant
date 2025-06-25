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

    <!-- Thống kê -->
    <v-container fluid class="py-6 px-4 px-sm-6">
      <v-row justify="center" align="stretch" dense>
        <v-col
          v-for="(stat, index) in [
            { icon: 'mdi-file-document-outline', value: stats.documents, label: 'Tài liệu đã đăng', color: 'primary' },
            { icon: 'mdi-help-circle-outline', value: stats.questionsAnswered, label: 'Câu hỏi đã trả lời', color: 'success' },
            { icon: 'mdi-account-group-outline', value: stats.usersJoined, label: 'Người dùng tham gia', color: 'indigo' },
          ]"
          :key="index"
          cols="12"
          sm="6"
          md="4"
          class="d-flex"
        >
          <v-card
            elevation="3"
            class="pa-4 text-center rounded-xl flex-grow-1 d-flex flex-column align-center justify-space-evenly"
            style="min-height: 150px;"
          >
            <v-icon :color="stat.color" size="32">{{ stat.icon }}</v-icon>
            <div class="text-subtitle-1 font-weight-bold mt-2">{{ stat.value }}</div>
            <div class="text-caption text-grey-darken-1">{{ stat.label }}</div>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-container fluid class="py-10 px-4 px-sm-6" style="background-color: #fff8f1;">
      <v-row
        class="d-flex flex-column-reverse flex-md-row"
        align="center"
        justify="center"
      >
        <!-- Blockquote text -->
        <v-col
          cols="12"
          md="6"
          class="text-center text-md-left"
        >
          <blockquote
            class="text-body-1 text-md-h6 font-weight-medium mx-auto"
            style="line-height: 1.6; max-width: 500px;"
          >
            “However difficult life may seem, there is
            <strong class="text-orange-darken-2"> always something you can do </strong>
            and <strong> succeed at. </strong>”
          </blockquote>
          <div class="text-center text-md-right text-grey-darken-2 mt-2 font-weight-medium">
            – STEVEN HAWKING
          </div>
        </v-col>

        <!-- Image -->
        <v-col cols="12" md="6" class="text-center mb-6 mb-md-0">
          <v-img
            src="https://www.jobsterritory.com/images/raas-hero.png"
           
            class="mx-auto rounded"
            alt="Inspiration Image"
            cover
          />
        </v-col>
      </v-row>
    </v-container>
  </HeaderForm>
</template>
