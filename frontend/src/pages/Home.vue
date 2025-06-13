<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Chào mừng đến với BTEC AI Teaching Assistant!</v-card-title>
          <v-card-text>
            <p>Bạn đã đăng nhập thành công.</p>
            <v-btn color="error" @click="logout">Đăng xuất</v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { logout } from '../api/auth'
</script>