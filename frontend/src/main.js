// import './assets/main.css'
import './assets/login.css'
import './assets/signup.css';
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import 'vuetify/styles'
import api from './api/http' 
import '@fortawesome/fontawesome-free/css/all.min.css';


const vuetify = createVuetify({ components, directives })

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(vuetify)

app.mount('#app')
