<template>
  <div class="form-section">
    <div v-if="successMessage" class="alert-success">{{ successMessage }}</div>
    <h2>Sign-up</h2>
    <form @submit.prevent="handleRegister">
      <!-- Không render lỗi tổng trên form nữa -->
      <div class="form-input">
        <div class="form-input-wrapper">
          <input
            type="text"
            v-model="form.fullName"
            placeholder="Full Name"
            :class="{ 'input-error-border': fullNameError }"
            @input="fullNameError = false"
          >
          <i class="fas fa-user" :style="fullNameError ? 'color:#e74c3c' : ''"></i>
        </div>
      </div>
      <div class="form-input">
        <div class="form-input-wrapper">
          <input
            type="email"
            v-model="form.email"
            placeholder="Email"
            :class="{ 'input-error-border': emailError }"
            @input="emailError = false"
          >
          <i class="fas fa-envelope" :style="emailError ? 'color:#e74c3c' : ''"></i>
        </div>
      </div>
      <div class="form-input">
        <div class="form-input-wrapper">
          <input
            type="password"
            v-model="form.password"
            placeholder="Password"
            :class="{ 'input-error-border': passwordError }"
            @input="passwordError = false"
          >
          <i class="fas fa-lock" :style="passwordError ? 'color:#e74c3c' : ''"></i>
        </div>
      </div>
      <div class="form-input">
        <div class="form-input-wrapper">
          <input
            type="password"
            v-model="form.confirmPassword"
            placeholder="Confirm Password"
            :class="{ 'input-error-border': confirmPasswordError }"
            @input="confirmPasswordError = false"
          >
          <i class="fas fa-lock" :style="confirmPasswordError ? 'color:#e74c3c' : ''"></i>
        </div>
      </div>
      <button class="signup-btn" :disabled="loading">
        <span v-if="loading" class="spinner"></span>
        <span v-else>Sign-Up</span>
      </button>
    </form>
    <div class="social"><span>Or Sign-up with social platform</span></div>
    <div class="social-icons">
      <i class="fab fa-facebook" @click="loginWithFacebook"></i>
      <i class="fab fa-github"></i>
      <i class="fab fa-google" @click="loginWithGoogle"></i>
      <i class="fab fa-twitter"></i>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'sign-up',
  data() {
    return {
      form: {
        fullName: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      loading: false,
      error: '',
      successMessage: '',
      fullNameError: false,
      emailError: false,
      passwordError: false,
      confirmPasswordError: false
    };
  },
  methods: {
    async handleRegister() {
      this.error = '';
      this.successMessage = '';
      this.fullNameError = false;
      this.emailError = false;
      this.passwordError = false;
      this.confirmPasswordError = false;
      let hasError = false;
      if (!this.form.fullName) {
        this.fullNameError = true;
        hasError = true;
      }
      if (!this.form.email) {
        this.emailError = true;
        hasError = true;
      } else {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(this.form.email)) {
          this.emailError = true;
          hasError = true;
        }
      }
      if (!this.form.password) {
        this.passwordError = true;
        hasError = true;
      }
      if (!this.form.confirmPassword) {
        this.confirmPasswordError = true;
        hasError = true;
      } else if (this.form.password && this.form.password !== this.form.confirmPassword) {
        this.confirmPasswordError = true;
        hasError = true;
      }
      if (hasError) {
        alert('Please fill in all required fields correctly.');
        return;
        
      }
      this.loading = true;
      try {
        // Gọi API đăng ký
        await axios.post('http://localhost:8000/auth/create', {
          name: this.form.fullName, 
          email: this.form.email,
          password: this.form.password
        });
        // Hiện thông báo thành công bằng alert
        alert('Sign-up successfully, please login...!');
        // Emit event để parent chuyển panel sang login
        this.$emit('switch-to-login', this.form.email);
        // Reset form
        this.form.fullName = '';
        this.form.email = '';
        this.form.password = '';
        this.form.confirmPassword = '';
        this.loading = false;
      } catch (err) {
        alert(err.response?.data?.message || 'Sign-up failed. Please try again later.');
        this.loading = false;
      }
    },
    loginWithFacebook() {},
    loginWithGoogle() {},
  }
}
</script>

