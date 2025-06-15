<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="justify-center">Đăng nhập</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="onSubmit" ref="formRef">
              <v-text-field
                label="Tên đăng nhập"
                v-model="username"
                :disabled="loading"
                prepend-inner-icon="mdi-account"
                required
              />
              <v-text-field
                label="Mật khẩu"
                v-model="password"
                type="password"
                :disabled="loading"
                prepend-inner-icon="mdi-lock"
                required
              />
              <v-btn
                type="submit"
                color="primary"
                block
                class="mt-3"
                :loading="loading"
              >Đăng nhập</v-btn>
              <v-alert
                v-if="error"
                type="error"
                class="mt-3"
                dense
                border="start"
                border-color="red"
              >{{ error }}</v-alert>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { nextTick, ref } from 'vue'
// import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import router from '../router'

const username = ref('linhhn13@fpt.edu.vn') // Mặc định tên đăng nhập
const password = ref('12345678')
const error = ref('')
const loading = ref(false)

const formRef = ref(null)
const authStore = useAuthStore()


const onSubmit = async () => {
  error.value = ''
  loading.value = true
  try {
    await authStore.login({ username: username.value, password: password.value })
    loading.value = false
    await nextTick();
    router.push({ name: 'home' }) // Chuyển hướng đến trang chính sau khi đăng nhập thành công
  } catch (err) {
    error.value = err?.response?.data?.detail || 'Đăng nhập thất bại'
    loading.value = false
    throw new Error(error.value)
  }
}
</script>
