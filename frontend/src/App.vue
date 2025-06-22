<script setup>
import { useAuthStore } from './stores/auth'
import { computed } from 'vue'

const auth = useAuthStore()
const isAuthenticated = computed(() => auth.isAuthenticated)
const logout = () => auth.logout()
</script>

<template>
  <div>
    <nav v-if="isAuthenticated" class="navbar">
      <button @click="logout">Logout</button>
    </nav>
    <RouterView />
  </div>
</template>

<style scoped>
.navbar {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 32px 0 0;
}
button {
  background: #7494ec;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 8px 18px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
button:hover {
  background: #4a6ed6;
}
</style>
