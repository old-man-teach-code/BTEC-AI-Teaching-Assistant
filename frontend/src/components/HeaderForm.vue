<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useDisplay } from 'vuetify'
import { useRoute } from 'vue-router'

const authStore = useAuthStore()
const drawer = ref(true)

const { mobile } = useDisplay()
const route = useRoute()

const notifications = ref([])
const unreadCount = computed(() => notifications.value.length)
const userId = computed(() => authStore.currentUser?.id || '')

async function fetchNotifications() {
  if (!userId.value) return
  try {
    const response = await axios.get(`/api/notifications/${userId.value}`)
    notifications.value = response.data
  } catch (error) {
    console.error('Lỗi lấy thông báo:', error)
  }
}

async function markAllAsRead() {
  try {
    await axios.post(`http://localhost:5000/api/notifications/${userId.value}/mark-all-read`)
    notifications.value = []
  } catch (error) {
    console.error('Lỗi cập nhật thông báo:', error)
  }
}

function logout() {
  authStore.logout()
}

onMounted(() => {
  if (!authStore.isAuthenticated) {
    authStore.logout()
  }
  drawer.value = !mobile.value
  fetchNotifications()
})

watch(mobile, (newVal) => {
  drawer.value = !newVal
})

const items = [
  { title: 'Trang chủ', icon: 'mdi-home', to: '/' },
  { title: 'Tài liệu', icon: 'mdi-file-document', to: '/about' },
  { title: 'Mẫu phản hồi', icon: 'mdi-bell', to: '/feedback' },
  { title: 'Lịch', icon: 'mdi-calendar', to: '/calendar' },
  { title: 'Chattest', icon: 'mdi-chat', to: '/chat' },
  { title: 'Cài đặt', icon: 'mdi-cog', to: '/settings' },
  { divider: true },
]
</script>

<template>
  <v-app>
    <v-app-bar color="primary" app>
      <!-- Chỉ hiển thị nav icon khi ở mobile -->
      <v-app-bar-nav-icon v-if="mobile" @click.stop="drawer = !drawer" />

      <v-toolbar-title class="me-4">Logo</v-toolbar-title>

      <v-spacer />

      <!-- Các nút điều hướng -->

      <v-toolbar-items class="nav-links" v-show="!mobile">
        <v-btn to="/" text class="nav-btn">HOME</v-btn>
        <v-btn to="/about" text class="nav-btn">ABOUT</v-btn>
        <v-btn to="/contact" text class="nav-btn">CONTACT US</v-btn>
      </v-toolbar-items>

      <v-spacer />

      <!-- Actions: Notification + Account -->
      <div class="header-actions">
        <!-- Notifications -->
        <v-menu offset-y>
          <template #activator="{ props }">
            <v-badge :content="unreadCount" color="red" v-if="unreadCount > 0" overlap>
              <v-btn icon v-bind="props">
                <v-icon color="orange">mdi-bell-alert</v-icon>
              </v-btn>
            </v-badge>
            <v-btn v-else icon v-bind="props">
              <v-icon>mdi-bell</v-icon>
            </v-btn>
          </template>

          <v-card width="300">
            <v-card-title>
              Notifications
              <v-chip class="ms-2" color="grey-lighten-2" label>{{ unreadCount }}</v-chip>
            </v-card-title>
            <v-divider />
            <v-card-text style="max-height: 300px; overflow-y: auto">
              <div v-if="notifications.length === 0">Không có thông báo mới.</div>
              <v-list v-else>
                <v-list-item
                  v-for="(n, i) in notifications"
                  :key="i"
                  :title="n.message"
                  prepend-icon="mdi-bell-ring-outline"
                />
              </v-list>
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" @click="markAllAsRead">Đánh dấu đã đọc</v-btn>
            </v-card-actions>
          </v-card>
        </v-menu>

        <!-- User Menu -->
        <v-menu>
          <template #activator="{ props }">
            <v-btn icon v-bind="props"><v-icon>mdi-account</v-icon></v-btn>
          </template>
          <v-list>
            <v-list-item
              title="Thông tin cá nhân"
              prepend-icon="mdi-account-circle"
              @click="home"
            />
            <v-list-item title="Đổi mật khẩu" prepend-icon="mdi-lock-reset" @click="home" />
            <v-list-item title="Đăng xuất" prepend-icon="mdi-logout" @click="logout" />
          </v-list>
        </v-menu>
      </div>
    </v-app-bar>

    <!-- Sidebar -->
    <v-navigation-drawer
      v-if="mobile"
      @click.stop="drawer = !drawer"
      v-model="drawer"
      :location="mobile ? 'bottom' : 'left'"
      :temporary="mobile"
      :permanent="!mobile"
      app
    >
      <v-list dense nav>
        <template v-for="(item, index) in items">
          <v-divider v-if="item.divider" :key="'divider-' + index" />
          <v-list-item
            v-else
            :key="'item-' + index"
            :title="item.title"
            :prepend-icon="item.icon"
            :to="item.to"
            :active="route.path === item.to"
            active-class="v-list-item--active"
            exact
          />
        </template>
      </v-list>
    </v-navigation-drawer>

    <!-- Main content -->
    <v-main>
      <slot />
    </v-main>
  </v-app>
</template>

<style scoped>
.nav-links {
  display: flex;
  align-items: center;
  gap: 20px;
}
.nav-btn {
  width: 120px;
  justify-content: center; /* Căn giữa nội dung */
}
.header-actions {
  display: flex;
  align-items: center;
}
</style>
