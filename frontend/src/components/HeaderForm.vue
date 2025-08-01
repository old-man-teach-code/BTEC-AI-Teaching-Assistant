<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchNotifications, markAllAsRead } from '@/api/notification'
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



async function handleMarkAllAsRead() {
  try {
    await markAllAsRead(userId.value)
    notifications.value = []
  } catch (error) {
    console.error('Lỗi cập nhật thông báo:', error)
  }
}

function logout() {
  authStore.logout()
}

// Load thông báo sau khi đăng nhập
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

watch(mobile, (newVal) => {
  drawer.value = !newVal
})

const items = [

  { title: 'Home', icon: 'mdi-home', to: '/' },
  { title: 'Documents', icon: 'mdi-file-document', to: '/documents' },
  { title: 'Feedback Form', icon: 'mdi-bell', to: '/feedback' },
  { title: 'Calendar', icon: 'mdi-calendar', to: '/calendar' },
  { title: 'Chat Test', icon: 'mdi-chat', to: '/chat' },
  { title: 'Settings', icon: 'mdi-cog', to: '/settings' },

  { divider: true },
]
</script>

<template>
  <v-app>
    <v-app-bar color="primary" app>
      <!-- Chỉ hiển thị nav icon khi ở mobile -->
      <v-btn icon v-if="mobile" @click.stop="drawer = !drawer">
        <i class="fas fa-bars"></i>
      </v-btn>

      <v-toolbar-title class="me-4">Logo</v-toolbar-title>

      <v-spacer />

      <!-- Các nút điều hướng -->
      <v-toolbar-items class="nav-links" v-show="!mobile">
        <v-btn to="/" text class="nav-btn">HOME</v-btn>
        <v-btn to="/about" text class="nav-btn">ABOUT</v-btn>
        <v-btn to="/contact" text class="nav-btn">CONTACT US</v-btn>
      </v-toolbar-items>

      <v-spacer />

      <!-- Actions: Notification + Account + Logout -->
      <div class="header-actions">
        <!-- Notifications -->
        <v-menu offset-y>
          <template #activator="{ props }">
            <v-badge :content="unreadCount" color="red" v-if="unreadCount > 0" overlap>
              <v-btn icon v-bind="props">
                <i class="fas fa-bell"></i>
              </v-btn>
            </v-badge>
            <v-btn v-else icon v-bind="props">
              <i class="fas fa-bell"></i>
            </v-btn>
          </template>

          <v-card width="300">
            <v-card-title>
              Notifications
              <v-chip class="ms-2" color="grey-lighten-2" label>{{ unreadCount }}</v-chip>
            </v-card-title>
            <v-divider />
            <v-card-text style="max-height: 300px; overflow-y: auto">

              <div v-if="notifications.length === 0">No new notifications</div>

              <v-list v-else>
                <v-list-item
                  v-for="(n, i) in notifications"
                  :key="i"
                  :title="n.message"
                >
                  <template #prepend>
                    <i class="fas fa-bell"></i>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
            <v-card-actions>

              <v-btn color="primary" @click="handleMarkAllAsRead">Mask as read</v-btn>

            </v-card-actions>
          </v-card>
        </v-menu>

        <!-- User Menu -->
        <v-menu>
          <template #activator="{ props }">
            <v-btn icon v-bind="props"><i class="fas fa-user"></i></v-btn>
          </template>
          <v-list>
            <v-list-item

              title="Personal Information"
              @click="home"
             
            >
              <template #prepend><i class="fas fa-user-circle"></i></template>
            </v-list-item>
            <v-list-item title="Change Password" @click="home">
              <template #prepend><i class="fas fa-key"></i></template>
            </v-list-item>
            <v-list-item title="Logout" @click="logout">

              <template #prepend><i class="fas fa-sign-out-alt"></i></template>
            </v-list-item>
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
            :to="item.to"
            :active="route.path === item.to"
            active-class="v-list-item--active"
            exact
          >
            <template #prepend>
              <i v-if="item.icon === 'mdi-home'" class="fas fa-home"></i>
              <i v-else-if="item.icon === 'mdi-file-document'" class="fas fa-file-alt"></i>
              <i v-else-if="item.icon === 'mdi-bell'" class="fas fa-bell"></i>
              <i v-else-if="item.icon === 'mdi-calendar'" class="fas fa-calendar-alt"></i>
              <i v-else-if="item.icon === 'mdi-chat'" class="fas fa-comments"></i>
              <i v-else-if="item.icon === 'mdi-cog'" class="fas fa-cog"></i>
            </template>
          </v-list-item>
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

/* Fix icon and text alignment in sidebar */
.v-list-item__prepend {
  min-width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.v-list-item__content {
  margin-left: 0 !important;
}
.v-list-item .fas {
  font-size: 22px;
  min-width: 24px;
  margin-right: 10px;
}
.v-list-item {
  align-items: center;
}

.logout-btn {
  background: #7494ec;
  color: #fff;
  border-radius: 6px;
  margin-left: 12px;
  font-weight: 600;
  text-transform: none;
  transition: background 0.2s;
}
.logout-btn:hover {
  background: #4a6ed6;
}
</style>