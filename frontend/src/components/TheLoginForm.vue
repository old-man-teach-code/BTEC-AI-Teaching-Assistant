<template>
  <div class="form-section">
    <h2>Login</h2>
    <div v-if="error" class="error-message">{{ error }}</div>
    
    <!-- Email -->
    <div class="form-input">
      <div class="form-input-wrapper">
        <input type="email" v-model="form.email" placeholder="Email" />
        <i class="fas fa-envelope"></i>
      </div>
    </div>

    
    <!-- Password -->
    <div class="form-input">
      <div class="form-input-wrapper">
        <input type="password" v-model="form.password" placeholder="Password" />
        <i class="fas fa-lock"></i>
      </div>
    </div>
    
    <button class="login-btn" @click="handleLogin" :disabled="loading">
      <span v-if="loading" class="spinner"></span>
      <span v-else>Login</span>
    </button>
    
    <div class="options">
      <label class="remember">
        <input type="checkbox" />
        Remember me
      </label>
      <a href="#" class="forgot">Forgot Password?</a>
    </div>
    
    <div class="social"><span>Or Sign-up with social platform</span></div>
    <div class="social-icons">
      <i class="fab fa-facebook"></i>
      <i class="fab fa-github"></i>
      <i class="fab fa-google" @click="loginWithGoogle"></i>
      <i class="fab fa-twitter"></i>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'LoginForm',
  data() {
    return {
      form: {
        email: '',
        password: ''
      },
      loading: false,
      error: ''
    }
  },
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()

    return { authStore, router }
  },
  methods: {
    async handleLogin() {
      this.error = ''
      // Validate trước khi gọi API
      if (!this.form.email || !this.form.password) {
        this.error = 'Email and password are required.'
        return
      }
      this.loading = true
      try {
        await this.authStore.login({
          username: this.form.email, // ->>  dùng 'username' nếu backend dùng OAuth2PasswordRequestForm
          password: this.form.password
        })
        // JWT sẽ được lưu trong store (auth.js) và localStorage
        console.log('JWT:', this.authStore.jwt)
        console.log('JWT in localStorage:', localStorage.getItem('jwt_token'))
        this.loading = false
        this.router.push({ path: '/dashboard' }) // ->> Chuyển hướng sau khi đăng nhập
      } catch (err) {
        this.error = err?.response?.data?.detail || 'Login failed. Please try again.'
        this.loading = false
      }
    },
    loginWithGoogle() {
      // Placeholder cho đăng nhập Google nếu có
    }
  }
}
</script>
