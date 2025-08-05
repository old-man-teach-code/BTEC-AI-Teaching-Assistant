// import './assets/main.css'
import './assets/login.css'
import './assets/signup.css';
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Import MDI font trước Vuetify
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { vuetify } from './plugin/vuetify'

import api from './api/http' 
import '@fortawesome/fontawesome-free/css/all.min.css';

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(vuetify)

app.mount('#app')