<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" md="4">
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/auth'

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const router = useRouter()
const formRef = ref(null)

const onSubmit = async () => {
  error.value = ''
  loading.value = true
  try {
    await login(username.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err?.response?.data?.detail || 'Đăng nhập thất bại'
  } finally {
    loading.value = false
  }
}
</script>