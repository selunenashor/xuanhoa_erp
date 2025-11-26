/**
 * Xuân Hòa Manufacturing - Vue.js Frontend
 * Entry point
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'

const app = createApp(App)

// State management
app.use(createPinia())

// Router
app.use(router)

// Mount app
app.mount('#app')
