<script setup>
import { ref, onBeforeMount} from 'vue'
import axios from 'axios'
import { useRouter } from "vue-router"
import { useUserStore } from '@/stores/userStore'
import { storeToRefs } from "pinia"
import Cookies from 'js-cookie'

const username = ref('')
const password = ref('')
const otpCode = ref('')
const router = useRouter()
const userStore = useUserStore()
const { userInfo } = storeToRefs(userStore)

const quickStats = ref([
  { title: 'Книг', value: '0' },
  { title: 'Штрафов', value: '0' },
  { title: 'Карточек', value: '0' },
  { title: 'Записей', value: '0' }
])

axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");

onBeforeMount(async () => {
  await userStore.checkLogin()
  await userStore.checkOTPStatus()
  await fetchQuickStats()
})

async function onFormSend() {
  await userStore.login(username.value, password.value)
}

async function onOTPSubmit() {
  await userStore.verifyOTP(otpCode.value)
}

async function fetchQuickStats() {
  try {
    const [booksRes, finesRes, cardsRes, recordsRes] = await Promise.all([
      axios.get('/api/books/stats/'),
      axios.get('/api/fines/stats/'),
      axios.get('/api/registrationCards/stats/'),
      axios.get('/api/records/stats/')
    ])
    
    quickStats.value[0].value = booksRes.data.count || 0
    quickStats.value[1].value = finesRes.data.count || 0
    quickStats.value[2].value = cardsRes.data.count || 0
    quickStats.value[3].value = recordsRes.data.count || 0
  } catch (error) {
    console.error('Error fetching quick stats:', error)
  }
}
</script>

<template>
<div class="container py-4">
  <div v-if="userInfo && userInfo.is_authenticated" class="card mb-4">
    <div class="card-body text-center">
      <h4 class="mb-0">Добро пожаловать, {{ userInfo.username || 'Пользователь' }}</h4>
      <div v-if="!userStore.otpStatus.otp_good" class="mt-3">
        <p class="text-warning mb-2">Требуется OTP для редактирования</p>
        <div class="row justify-content-center">
          <div class="col-md-3">
            <input type="text" v-model="otpCode" class="form-control text-center" placeholder="6 цифр" maxlength="6">
          </div>
          <div class="col-md-2">
            <button class="btn btn-primary" @click="onOTPSubmit">Подтвердить OTP</button>
          </div>
        </div>
      </div>
      <p v-else class="mt-2 mb-0 text-success">OTP подтвержден, доступ к редактированию открыт</p>
    </div>
  </div>

  <div v-if="!userInfo.is_authenticated" class="modal fade show d-block" style="background: rgba(0,0,0,0.5)">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Пожалуйста, авторизуйтесь</h5>
        </div>
        <div class="modal-body">
          <form @submit.stop.prevent="onFormSend" class="row g-3">
            <div class="col-md-6">
              <input v-model="username" type="text" class="form-control" placeholder="Логин" required>
            </div>
            <div class="col-md-6">
              <input v-model="password" type="password" class="form-control" placeholder="Пароль" required>
            </div>
            <div class="col-12">
              <button type="submit" class="btn btn-primary w-100">Войти</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>

</div>
</template>

<style scoped>
.stats-card {
  background: #e2c3d8;
  border: 1px solid #d49bc5;
  border-radius: 8px;
  padding: 20px;
}

.stat-item {
  padding: 15px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #0d6efd;
  margin-bottom: 5px;
}

.stat-label {
  color: #6c757d;
  font-size: 0.9rem;
}

.btn {
  padding: 10px 20px;
}
</style>