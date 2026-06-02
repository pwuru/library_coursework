<script setup>
import { ref, onBeforeMount, computed } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

const fines = ref([]);
const loading = ref(false);
const fineToAdd = ref({})
const fineToEdit = ref({})
const stats = ref({});
const showFilters = ref(false);
const filters = ref({
  fineType: "",
  amountMin: "",
  amountMax: "",
  dateFrom: "",
  dateTo: ""
});

const fineTypesList = [
  { value: 'overdue', label: 'Нарушение сроков возврата' },
  { value: 'damage', label: 'Порча книги' },
  { value: 'lost', label: 'Потеря книги' }
];

async function fetchFines() {
  loading.value = true;
  const r = await axios.get("/api/fines/");
  fines.value = r.data;
  loading.value = false;
}

async function fetchStats() {
  const r = await axios.get("/api/fines/stats/");
  stats.value = r.data;
}

async function onFineAdd() {
  await axios.post("/api/fines/", {
    ...fineToAdd.value,
  });
  await fetchFines();
  await fetchStats();
  fineToAdd.value = {};
}

async function onUpdateFine() {
  await axios.put(`/api/fines/${fineToEdit.value.id}/`, {
    fineType: fineToEdit.value.fineType,
    amount: fineToEdit.value.amount,
    date: fineToEdit.value.date
  });
  await fetchFines();
  await fetchStats();
}

async function onFineEditClick(fine) {
  fineToEdit.value = { ...fine };
}

async function onRemoveClick(fine) {
  await axios.delete(`/api/fines/${fine.id}/`);
  await fetchFines();
  await fetchStats();
}

function clearFilters() {
  filters.value = {
    fineType: "",
    amountMin: "",
    amountMax: "",
    dateFrom: "",
    dateTo: ""
  };
}

const filteredFines = computed(() => {
  return fines.value.filter(fine => {
    if (filters.value.fineType && fine.fineType !== filters.value.fineType) return false;
    if (filters.value.amountMin && fine.amount < parseInt(filters.value.amountMin)) return false;
    if (filters.value.amountMax && fine.amount > parseInt(filters.value.amountMax)) return false;
    if (filters.value.dateFrom && fine.date < filters.value.dateFrom) return false;
    if (filters.value.dateTo && fine.date > filters.value.dateTo) return false;
    return true;
  });
});

async function exportToExcel() {
  try {
    const response = await axios.get("/api/fines/export-excel/", {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    
    let filename = "fines.xlsx";
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
  await fetchFines();
  await fetchStats();
})

function formatDate(date) {
  if (!date) return '';
  return new Date(date).toLocaleDateString('ru-RU');
}

function formatFineType(type) {
  const types = {
    'overdue': 'Нарушение сроков возврата',
    'damage': 'Порча книги',
    'lost': 'Потеря книги'
  };
  return types[type] || type;
}
</script>

<template>
  <div class="container-fluid px-4">
    <div class="d-flex gap-3 p-2 border rounded mb-3">
      <span>Всего штрафов: {{ stats.count || 0 }}</span>
      <span>Средняя сумма: {{ stats.avg_amount ? Math.round(stats.avg_amount) : 0 }} руб.</span>
      <span>Максимальная сумма: {{ stats.max_amount || 0 }} руб.</span>
      <span>Минимальная сумма: {{ stats.min_amount || 0 }} руб.</span>
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
        <div class="col-md-2">
          <select v-model="filters.fineType" class="form-control form-control-sm">
            <option value="">Все типы</option>
            <option v-for="type in fineTypesList" :key="type.value" :value="type.value">{{ type.label }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <input v-model="filters.amountMin" type="number" class="form-control form-control-sm" placeholder="Сумма от">
        </div>
        <div class="col-md-2">
          <input v-model="filters.amountMax" type="number" class="form-control form-control-sm" placeholder="Сумма до">
        </div>
        <div class="col-md-2">
          <input v-model="filters.dateFrom" type="date" class="form-control form-control-sm" placeholder="Дата от">
        </div>
        <div class="col-md-2">
          <input v-model="filters.dateTo" type="date" class="form-control form-control-sm" placeholder="Дата до">
        </div>
        <div class="col-md-2">
          <button class="btn btn-sm btn-outline-danger w-100" @click="clearFilters">Очистить</button>
        </div>
      </div>
    </div>

    <div class="p-2 px-0">
      <form @submit.prevent.stop="onFineAdd">
        <div class="row">
          <div class="col">
            <div class="form-floating">
              <select class="form-control" v-model="fineToAdd.fineType" required>
                <option value="overdue">Нарушение сроков возврата</option>
                <option value="damage">Порча книги</option>
                <option value="lost">Потеря книги</option>
              </select>
              <label>Тип штрафа</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input type="number" class="form-control" v-model="fineToAdd.amount" required />
              <label>Сумма</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input type="date" class="form-control" v-model="fineToAdd.date" required />
              <label>Дата</label>
            </div>
          </div>
          <div class="col-auto">
            <button class="btn btn-primary"><i class="bi bi-plus-lg"></i></button>
          </div>
        </div>
      </form>
    </div>

    <div class="px-0">
      <div v-for="item in filteredFines" class="fine-item mb-2 p-2 border rounded">
        <div>
          <strong>{{ formatFineType(item.fineType) }}</strong> - {{ item.amount }} руб. ({{ formatDate(item.date) }})
        </div>
        <div class="mt-2">
          <button class="btn btn-success me-2" @click="onFineEditClick(item)" data-bs-toggle="modal" data-bs-target="#editFineModal">
            <i class="bi bi-pencil-fill"></i>
          </button>
          <button class="btn btn-danger" @click="onRemoveClick(item)"><i class="bi bi-x"></i></button>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editFineModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5">Редактировать штраф</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="form-floating mb-2">
              <select class="form-control" v-model="fineToEdit.fineType">
                <option value="overdue">Нарушение сроков возврата</option>
                <option value="damage">Порча книги</option>
                <option value="lost">Потеря книги</option>
              </select>
              <label>Тип штрафа</label>
            </div>
            <div class="form-floating mb-2">
              <input type="number" class="form-control" v-model="fineToEdit.amount" />
              <label>Сумма</label>
            </div>
            <div class="form-floating mb-2">
              <input type="date" class="form-control" v-model="fineToEdit.date" />
              <label>Дата</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              <i class="bi bi-x-lg"></i>
            </button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateFine">
              <i class="bi bi-check-lg"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.fine-item {
  padding: 0.5rem 1rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fine-item > div:first-child {
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