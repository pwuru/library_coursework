<script setup>
import { ref, onBeforeMount, computed } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

const records = ref([]);
const cards = ref([]);
const books = ref([]);
const fines = ref([]);
const loading = ref(false);
const recordToAdd = ref({})
const recordToEdit = ref({})
const stats = ref({});
const showFilters = ref(false);
const filters = ref({
  book_issue_date_from: "",
  book_issue_date_to: "",
  fine_status: "",
  registrationCard: "",
  book: "",
  fine: ""
});

async function fetchRecords() {
  loading.value = true;
  const r = await axios.get("/api/records/");
  records.value = r.data;
  loading.value = false;
}

async function fetchCards() {
  const r = await axios.get("/api/registrationCards/");
  cards.value = r.data;
}

async function fetchBooks() {
  const r = await axios.get("/api/books/");
  books.value = r.data;
}

async function fetchFines() {
  const r = await axios.get("/api/fines/");
  fines.value = r.data;
}

async function fetchStats() {
  const r = await axios.get("/api/records/stats/");
  stats.value = r.data;
}

async function onRecordAdd() {
  await axios.post("/api/records/", {
    ...recordToAdd.value,
  });
  await fetchRecords();
  await fetchStats();
  recordToAdd.value = {};
}

async function onUpdateRecord() {
  await axios.put(`/api/records/${recordToEdit.value.id}/`, {
    book_issue_date: recordToEdit.value.book_issue_date,
    expected_book_accept_date: recordToEdit.value.expected_book_accept_date,
    book_accept_date: recordToEdit.value.book_accept_date,
    fine_status: recordToEdit.value.fine_status,
    registrationCard: recordToEdit.value.registrationCard,
    book: recordToEdit.value.book,
    fine: recordToEdit.value.fine
  });
  await fetchRecords();
  await fetchStats();
}

async function onRecordEditClick(record) {
  recordToEdit.value = { ...record };
  recordToEdit.value.registrationCard = record.registrationCard?.id || null;
  recordToEdit.value.book = record.book?.id || null;
  recordToEdit.value.fine = record.fine?.id || null;
}

async function onRemoveClick(record) {
  await axios.delete(`/api/records/${record.id}/`);
  await fetchRecords();
  await fetchStats();
}

function formatDate(date) {
  if (!date) return '';
  return new Date(date).toLocaleDateString('ru-RU');
}

function formatFineType(type) {
  const map = {
    'overdue': 'Нарушение сроков возврата',
    'damage': 'Порча книги',
    'lost': 'Потеря книги'  
  };
  return map[type] || type;
}

function clearFilters() {
  filters.value = {
    book_issue_date_from: "",
    book_issue_date_to: "",
    fine_status: "",
    registrationCard: "",
    book: "",
    fine: ""
  };
}

const filteredRecords = computed(() => {
  return records.value.filter(record => {
    if (filters.value.book_issue_date_from && record.book_issue_date < filters.value.book_issue_date_from) return false;
    if (filters.value.book_issue_date_to && record.book_issue_date > filters.value.book_issue_date_to) return false;
    if (filters.value.fine_status && record.fine_status !== filters.value.fine_status) return false;
    if (filters.value.registrationCard && record.registrationCard != filters.value.registrationCard) return false;
    if (filters.value.book && record.book != filters.value.book) return false;
    if (filters.value.fine && record.fine != filters.value.fine) return false;
    return true;
  });
});

async function exportToExcel() {
  try {
    const response = await axios.get("/api/records/export-excel/", {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    
    let filename = "records.xlsx";
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
  await fetchRecords();
  await fetchCards();
  await fetchBooks();
  await fetchFines();
  await fetchStats();
})
</script>

<template>
  <div class="container-fluid px-4">
    <div class="d-flex gap-3 p-2 border rounded mb-3">
      <span>Всего записей: {{ stats.count || 0 }}</span>
      <span>Средний ID: {{ stats.avg_id ? Math.round(stats.avg_id) : 0 }}</span>
      <span>Максимальный ID: {{ stats.max_id || 0 }}</span>
      <span>Минимальный ID: {{ stats.min_id || 0 }}</span>
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
          <input v-model="filters.book_issue_date_from" type="date" class="form-control form-control-sm" placeholder="Дата выдачи от">
        </div>
        <div class="col-md-2">
          <input v-model="filters.book_issue_date_to" type="date" class="form-control form-control-sm" placeholder="Дата выдачи до">
        </div>
        <div class="col-md-2">
          <select v-model="filters.fine_status" class="form-control form-control-sm">
            <option value="">Все статусы</option>
            <option value="no_fine">Нет</option>
            <option value="unpaid">Не оплачен</option>
            <option value="paid">Оплачен</option>
          </select>
        </div>
        <div class="col-md-2">
          <select v-model="filters.registrationCard" class="form-control form-control-sm">
            <option :value="null">Все карточки</option>
            <option v-for="card in cards" :key="card.id" :value="card.id">Карточка #{{ card.id }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <select v-model="filters.book" class="form-control form-control-sm">
            <option :value="null">Все книги</option>
            <option v-for="book in books" :key="book.id" :value="book.id">{{ book.name }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <button class="btn btn-sm btn-outline-danger w-100" @click="clearFilters">Очистить</button>
        </div>
      </div>
    </div>

    <div class="p-2 px-0">
      <form @submit.prevent.stop="onRecordAdd">
        <div class="row">
          <div class="col">
            <div class="form-floating">
              <input type="date" class="form-control" v-model="recordToAdd.book_issue_date" required />
              <label>Дата выдачи</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input type="date" class="form-control" v-model="recordToAdd.expected_book_accept_date" required />
              <label>Ожидаемая дата возврата</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input type="date" class="form-control" v-model="recordToAdd.book_accept_date" />
              <label>Дата возврата</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <select class="form-control" v-model="recordToAdd.fine_status" required>
                <option value="no_fine">Нет</option>
                <option value="unpaid">Не оплачен</option>
                <option value="paid">Оплачен</option>
              </select>
              <label>Статус штрафа</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <select class="form-control" v-model="recordToAdd.registrationCard">
                <option :value="null">Не выбрано</option>
                <option v-for="card in cards" :key="card.id" :value="card.id">Карточка #{{ card.id }}</option>
              </select>
              <label>Карточка</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <select class="form-control" v-model="recordToAdd.book">
                <option :value="null">Не выбрано</option>
                <option v-for="book in books" :key="book.id" :value="book.id">{{ book.name }} ({{ book.author }})</option>
              </select>
              <label>Книга</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <select class="form-control" v-model="recordToAdd.fine">
                <option :value="null">Не выбрано</option>
                <option v-for="fine in fines" :key="fine.id" :value="fine.id">{{ formatFineType(fine.fineType) }} - {{ fine.amount }} руб.</option>
              </select>
              <label>Штраф</label>
            </div>
          </div>
          <div class="col-auto">
            <button class="btn btn-primary"><i class="bi bi-plus-lg"></i></button>
          </div>
        </div>
      </form>
    </div>

    <div class="px-0">
      <div v-for="item in filteredRecords" class="record-item mb-2 p-2 border rounded">
        <div>
          Дата выдачи: {{ formatDate(item.book_issue_date) }},
          ожидаемая дата возврата: {{ formatDate(item.expected_book_accept_date) }}, 
          дата возврата: {{ formatDate(item.book_accept_date) || 'не возвращена' }}, 
          штраф:
          <span v-if="item.fine_status === 'no_fine'">нет</span>
          <span v-else-if="item.fine_status === 'unpaid'">не оплачен</span>
          <span v-else-if="item.fine_status === 'paid'">оплачен</span>
        </div>
        <div class="mt-2">
          <button class="btn btn-success me-2" @click="onRecordEditClick(item)" data-bs-toggle="modal" data-bs-target="#editRecordModal">
            <i class="bi bi-pencil-fill"></i>
          </button>
          <button class="btn btn-danger" @click="onRemoveClick(item)"><i class="bi bi-x"></i></button>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editRecordModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5">Редактировать запись</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="form-floating mb-2">
              <input type="date" class="form-control" v-model="recordToEdit.book_issue_date" />
              <label>Дата выдачи</label>
            </div>
            <div class="form-floating mb-2">
              <input type="date" class="form-control" v-model="recordToEdit.expected_book_accept_date" />
              <label>Ожидаемая дата возврата</label>
            </div>
            <div class="form-floating mb-2">
              <input type="date" class="form-control" v-model="recordToEdit.book_accept_date" />
              <label>Дата возврата</label>
            </div>
            <div class="form-floating mb-2">
              <select class="form-control" v-model="recordToEdit.fine_status">
                <option value="no_fine">Нет</option>
                <option value="unpaid">Не оплачен</option>
                <option value="paid">Оплачен</option>
              </select>
              <label>Статус штрафа</label>
            </div>
            <div class="form-floating mb-2">
              <select class="form-control" v-model="recordToEdit.registrationCard">
                <option :value="null">Не выбрано</option>
                <option v-for="card in cards" :key="card.id" :value="card.id">Карточка #{{ card.id }}</option>
              </select>
              <label>Карточка</label>
            </div>
            <div class="form-floating mb-2">
              <select class="form-control" v-model="recordToEdit.book">
                <option :value="null">Не выбрано</option>
                <option v-for="book in books" :key="book.id" :value="book.id">{{ book.name }} ({{ book.author }})</option>
              </select>
              <label>Книга</label>
            </div>
            <div class="form-floating mb-2">
              <select class="form-control" v-model="recordToEdit.fine">
                <option :value="null">Не выбрано</option>
                <option v-for="fine in fines" :key="fine.id" :value="fine.id">{{ formatFineType(fine.fineType) }} - {{ fine.amount }} руб.</option>
              </select>
              <label>Штраф</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              <i class="bi bi-x-lg"></i>
            </button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateRecord">
              <i class="bi bi-check-lg"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.record-item {
  padding: 0.5rem 1rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.record-item > div:first-child {
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