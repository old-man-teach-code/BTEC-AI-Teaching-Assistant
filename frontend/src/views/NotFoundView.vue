<template>
  <v-container class="fill-height d-flex flex-column align-center justify-center">
    <v-row>
      <v-col class="text-center">
        <v-icon color="error" size="96">mdi-alert-circle-outline</v-icon>
        <h1 class="display-2 font-weight-bold mb-2">404</h1>
        <h2 class="subtitle-1 mb-4">Page Not Found</h2>
        <v-btn color="primary" @click="$router.push('/')">
          Go to Home
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
</script>
