import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router.ts'
import { useAuthStore } from './stores/auth'
import './styles/variables.css'
import './styles/base.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// Fetch current user before mounting (prevents UI flash)
const authStore = useAuthStore()
authStore.fetchMe().finally(() => {
  app.mount('#app')
})