<template>
  <div class="about">
    <h1>This is an about page</h1>
    <br>
    <v-btn @click="goToHomePage" color="primary" class="mt-4">
      <v-icon left>mdi-home</v-icon>
      <span @click="goToHomePage">Go to Home Page</span>
    </v-btn>
  </div>
</template>

<script setup>
import router from '@/router';

function goToHomePage() {
  router.push({ name: 'home' });
}
</script>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>
