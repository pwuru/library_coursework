import { createApp } from 'vue'
import { createPinia } from 'pinia'
import "bootstrap/dist/css/bootstrap.css"
import "bootstrap/dist/js/bootstrap"
import "bootstrap-icons/font/bootstrap-icons.css"

import App from './App.vue'
import router from './router'

const app = createApp(App) // создаем Vue-приложение

app.use(createPinia()) // подключаем pinia для управления состоянием (авторизация и тп)
app.use(router) // подключаем роутер

app.mount('#app') // вставляем приложение в index.html где id=app
