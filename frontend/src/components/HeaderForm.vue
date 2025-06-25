<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { fetchNotifications, markAllAsRead } from '@/api/notification'
import { useDisplay } from 'vuetify'
import { useRoute } from 'vue-router'

const authStore = useAuthStore()
const drawer = ref(true)
const { mobile } = useDisplay()
const route = useRoute()

const notifications = ref([])
const unreadCount = computed(() => notifications.value.length)
const userId = computed(() => authStore.user?.id || '')


async function handleMarkAllAsRead() {
  try {
    await markAllAsRead(userId.value)
    notifications.value = []
  } catch (e) {
    console.error('❌ Lỗi khi đánh dấu đã đọc:', e)
  }
}

function logout() {
  authStore.logout()
}

// Load thông báo sau khi đăng nhập
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    authStore.logout()
    return
  }

  drawer.value = !mobile.value

  if (userId.value) {
    try {
      const data = await fetchNotifications(userId.value)
      notifications.value = data
    } catch (e) {
      console.error('❌ Lỗi khi fetch thông báo trong onMounted:', e)
    }
  }
})

// Nếu user thay đổi (sau login), load lại thông báo
watch(
  () => authStore.currentUser,
  async (user) => {
    if (user?.id) {
      try {
        const data = await fetchNotifications(user.id)
        notifications.value = data
      } catch (e) {
        console.error('❌ Lỗi khi fetch thông báo khi user thay đổi:', e)
      }
    }
  },
  { immediate: true }
)

// Responsive drawer
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
      <v-app-bar-nav-icon v-if="mobile" @click.stop="drawer = !drawer" />
      <v-toolbar-title class="me-4">Logo</v-toolbar-title>
      <v-spacer />
      <v-toolbar-items class="nav-links" v-show="!mobile">
        <v-btn to="/" text class="nav-btn">HOME</v-btn>
        <v-btn to="/about" text class="nav-btn">ABOUT</v-btn>
        <v-btn to="/contact" text class="nav-btn">CONTACT US</v-btn>
      </v-toolbar-items>
      <v-spacer />

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
              <v-btn color="primary" @click="handleMarkAllAsRead">Đánh dấu đã đọc</v-btn>
            </v-card-actions>
          </v-card>
        </v-menu>

        <!-- User -->
        <v-menu>
          <template #activator="{ props }">
            <v-btn icon v-bind="props"><v-icon>mdi-account</v-icon></v-btn>
          </template>
          <v-list>
            <v-list-item title="Thông tin cá nhân" prepend-icon="mdi-account-circle" />
            <v-list-item title="Đổi mật khẩu" prepend-icon="mdi-lock-reset" />
            <v-list-item title="Đăng xuất" prepend-icon="mdi-logout" @click="logout" />
          </v-list>
        </v-menu>
      </div>
    </v-app-bar>

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
  justify-content: center;
}
.header-actions {
  display: flex;
  align-items: center;
}
</style>
