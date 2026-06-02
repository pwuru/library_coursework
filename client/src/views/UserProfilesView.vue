<script setup>
import { ref, onBeforeMount, computed } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

const profiles = ref([]);
const stats = ref({});
const loading = ref(false);
const profileToAdd = ref({})
const profileToEdit = ref({})
const showFilters = ref(false);
const filters = ref({
  name: "",
  phone: "",
  type: ""
});

async function fetchProfiles() {
  loading.value = true;
  const r = await axios.get("/api/userProfiles/");
  profiles.value = r.data;
  loading.value = false;
}

async function fetchStats() {
  const r = await axios.get("/api/userProfiles/stats/");
  stats.value = r.data;
}

async function onProfileAdd() {
  await axios.post("/api/userProfiles/", {
    ...profileToAdd.value,
  });
  await fetchProfiles();
  await fetchStats();
  profileToAdd.value = {};
}

async function onUpdateProfile() {
  await axios.put(`/api/userProfiles/${profileToEdit.value.id}/`, {
    name: profileToEdit.value.name,
    phone: profileToEdit.value.phone,
    type: profileToEdit.value.type
  });
  await fetchProfiles();
  await fetchStats();
}

async function onProfileEditClick(profile) {
  profileToEdit.value = { ...profile };
}

async function onRemoveClick(profile) {
  await axios.delete(`/api/userProfiles/${profile.id}/`);
  await fetchProfiles();
  await fetchStats();
}

function clearFilters() {
  filters.value = {
    name: "",
    phone: "",
    type: ""
  };
}

const filteredProfiles = computed(() => {
  return profiles.value.filter(profile => {
    if (filters.value.name && !profile.name?.toLowerCase().includes(filters.value.name.toLowerCase())) return false;
    if (filters.value.phone && !profile.phone?.toLowerCase().includes(filters.value.phone.toLowerCase())) return false;
    if (filters.value.type && profile.type !== filters.value.type) return false;
    return true;
  });
});

async function exportToExcel() {
  try {
    const response = await axios.get("/api/userProfiles/export-excel/", {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    
    let filename = "users.xlsx";
    const contentDisposition = response.headers['content-disposition'];
    if (contentDisposition) {
      const match = contentDisposition.match(/filename=(.+)/);
      if (match && match[1]) {
        filename = match[1];
      }
    }
    
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Ошибка при экспорте:', error);
  }
}

onBeforeMount(async () => {
  await fetchProfiles();
  await fetchStats();
})
</script>

<template>
  <div class="container-fluid px-4">
    <div class="d-flex gap-3 p-2 border rounded mb-3">
      <span>Всего пользователей: {{ stats.count || 0 }}</span>
      <span>Средний ID: {{ stats.avg_id ? Math.round(stats.avg_id) : 0 }}</span>
      <span>Макс. ID: {{ stats.max_id || 0 }}</span>
      <span>Мин. ID: {{ stats.min_id || 0 }}</span>
    </div>

    <div class="mb-2" style="display: flex; gap: 10px;">
      <button class="btn btn-light border px-3 py-2" @click="showFilters = !showFilters" style="min-width: 150px; white-space: nowrap; color: black;">
        {{ showFilters ? 'Скрыть фильтры' : 'Показать фильтры' }}
      </button>
      <button class="btn btn-success px-3 py-2" @click="exportToExcel" style="min-width: 150px; white-space: nowrap;">
        Экспорт в Excel
      </button>
    </div>

    <div v-if="showFilters" class="p-2 border rounded mb-3">
      <div class="row g-2">
        <div class="col-md-3">
          <input v-model="filters.name" type="text" class="form-control form-control-sm" placeholder="Имя">
        </div>
        <div class="col-md-3">
          <input v-model="filters.phone" type="text" class="form-control form-control-sm" placeholder="Телефон">
        </div>
        <div class="col-md-3">
          <select v-model="filters.type" class="form-control form-control-sm">
            <option value="">Все типы</option>
            <option value="admin">Администратор</option>
            <option value="employee">Работник</option>
            <option value="reader">Читатель</option>
          </select>
        </div>
        <div class="col-md-3">
          <button class="btn btn-sm btn-outline-danger w-100" @click="clearFilters">Очистить</button>
        </div>
      </div>
    </div>

    <div class="p-2 px-0">
      <form @submit.prevent.stop="onProfileAdd">
        <div class="row">
          <div class="col">
            <div class="form-floating">
              <input type="text" class="form-control" v-model="profileToAdd.name" required />
              <label>Имя</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input type="text" class="form-control" v-model="profileToAdd.phone" required />
              <label>Телефон</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <select class="form-control" v-model="profileToAdd.type" required>
                <option value="admin">Администратор</option>
                <option value="employee">Работник</option>
                <option value="reader">Читатель</option>
              </select>
              <label>Тип</label>
            </div>
          </div>
          <div class="col-auto">
            <button class="btn btn-primary"><i class="bi bi-plus-lg"></i></button>
          </div>
        </div>
      </form>
    </div>

    <div class="px-0">
      <div v-for="item in filteredProfiles" class="profile-item mb-2 p-2 border rounded">
        <div>
          <strong>{{ item.name }}</strong> - {{ item.phone }} ({{ item.type }})
        </div>
        <div class="mt-2">
          <button class="btn btn-success me-2" @click="onProfileEditClick(item)" data-bs-toggle="modal" data-bs-target="#editProfileModal">
            <i class="bi bi-pencil-fill"></i>
          </button>
          <button class="btn btn-danger" @click="onRemoveClick(item)"><i class="bi bi-x"></i></button>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editProfileModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5">Редактировать профиль</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="form-floating mb-2">
              <input type="text" class="form-control" v-model="profileToEdit.name" />
              <label>Имя</label>
            </div>
            <div class="form-floating mb-2">
              <input type="text" class="form-control" v-model="profileToEdit.phone" />
              <label>Телефон</label>
            </div>
            <div class="form-floating mb-2">
              <select class="form-control" v-model="profileToEdit.type">
                <option value="admin">Администратор</option>
                <option value="employee">Работник</option>
                <option value="reader">Читатель</option>
              </select>
              <label>Тип</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              <i class="bi bi-x-lg"></i>
            </button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateProfile">
              <i class="bi bi-check-lg"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.profile-item {
  padding: 0.5rem 1rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-item > div:first-child {
  flex: 1;
}

button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

button i {
  font-size: 16px;
}
</style>