<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useUserStore } from '@/stores/userStore';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const router = useRouter();

async function handleLogout() {
  await userStore.logout();
  router.push('/');
}

axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");

onBeforeMount(() => {
  userStore.checkLogin();
  userStore.checkOTPStatus();
})
</script>

<template>
  <div>
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Библиотека</a>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNavDropdown"
          aria-controls="navbarNavDropdown"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNavDropdown">
          <ul class="navbar-nav">
            <li class="nav-item">
              <router-link class="nav-link" to="/books">Книги</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/registration-cards">Учетные карточки</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/records">Записи в уч. карточках</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/fines">Штрафы</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/user-profiles">Пользователи</router-link>
            </li>
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                Пользователь
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="/admin">Админка</a></li>
                <li v-if="userStore.userInfo.is_authenticated"><a class="dropdown-item" href="#" @click.prevent="handleLogout">Выйти</a></li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <div class="container mt-4">
      <router-view/>
    </div>
  </div>
</template>