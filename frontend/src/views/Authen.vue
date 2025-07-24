<template>
  <div class="auth-bg">
    <div class="container" :class="{ active: !isSignin }">
      <div class="form-box login">
        <login />
      </div>
      <div class="form-box register">
        <signup />
      </div>
      <div class="toggle-box">
        <div class="toggle-panel toggle-left">
          <h1>Welcome Back! </h1>
          <p>Don't have an account? Register here.</p>
          <button class="btn" @click="isSignin = false">Register</button>
        </div>
        <div class="toggle-panel toggle-right">
          <h1>Nice to see you!</h1>
          <p>Already have an account? Login here.</p>
          <button class="btn" @click="isSignin = true">Login</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import signup from '../components/Signup.vue';
import login from '../components/TheLoginForm.vue';
import '../assets/auth.css';
export default {
  name: 'App',
  components: { signup, login },
  data() {
    return {
      isSignin: true,
      transitionName: 'slide-right' // mặc định
    };
  },
  methods: {
    toggleForm() {
      this.transitionName = this.isSignin ? 'slide-left' : 'slide-right';
      this.isSignin = !this.isSignin;
    },
}
}

</script>
