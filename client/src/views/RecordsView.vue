<script setup>
import { ref, onBeforeMount } from 'vue';
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

async function onRecordAdd() {
  await axios.post("/api/records/", {
    ...recordToAdd.value,
  });
  await fetchRecords();
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
}

async function onRecordEditClick(record) {
  recordToEdit.value = { ...record };
}

async function onRemoveClick(record) {
  await axios.delete(`/api/records/${record.id}/`);
  await fetchRecords();
}

function formatDate(date) {
  if (!date) return '';
  return new Date(date).toLocaleDateString('ru-RU');
}

onBeforeMount(async () => {
  await fetchRecords();
  await fetchCards();
  await fetchBooks();
  await fetchFines();
})
</script>

<template>
  <div class="container-fluid px-4">
    <div class="p-2 px-0">
      <form @submit.prevent.stop="onRecordAdd">
        <div class="row">
          <div class="col">
            <div class="form-floating">
              <input
                type="date"
                class="form-control"
                v-model="recordToAdd.book_issue_date"
                required
              />
              <label>Дата выдачи</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="date"
                class="form-control"
                v-model="recordToAdd.expected_book_accept_date"
                required
              />
              <label>Ожидаемая дата возврата</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="date"
                class="form-control"
                v-model="recordToAdd.book_accept_date"
              />
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
                <option v-for="card in cards" :key="card.id" :value="card.id">
                  Карточка #{{ card.id }}
                </option>
              </select>
              <label>Карточка</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <select class="form-control" v-model="recordToAdd.book">
                <option :value="null">Не выбрано</option>
                <option v-for="book in books" :key="book.id" :value="book.id">
                  {{ book.name }} ({{ book.author }})
                </option>
              </select>
              <label>Книга</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <select class="form-control" v-model="recordToAdd.fine">
                <option :value="null">Не выбрано</option>
                <option v-for="fine in fines" :key="fine.id" :value="fine.id">
                  {{ fine.fineType }} - {{ fine.amount }} руб.
                </option>
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
      <div v-for="item in records" class="record-item mb-2 p-2 border rounded">
        <div>
          <strong>Выдача: {{ formatDate(item.book_issue_date) }}</strong> | 
          Ожидаемый возврат: {{ formatDate(item.expected_book_accept_date) }} | 
          Возврат: {{ formatDate(item.book_accept_date) || 'не возвращена' }} | 
          Статус: 
          <span v-if="item.fine_status === 'no_fine'">Нет</span>
          <span v-else-if="item.fine_status === 'unpaid'">Не оплачен</span>
          <span v-else-if="item.fine_status === 'paid'">Оплачен</span>
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
                <option v-for="card in cards" :key="card.id" :value="card.id">
                  Карточка #{{ card.id }}
                </option>
              </select>
              <label>Карточка</label>
            </div>
            <div class="form-floating mb-2">
              <select class="form-control" v-model="recordToEdit.book">
                <option :value="null">Не выбрано</option>
                <option v-for="book in books" :key="book.id" :value="book.id">
                  {{ book.name }} ({{ book.author }})
                </option>
              </select>
              <label>Книга</label>
            </div>
            <div class="form-floating mb-2">
              <select class="form-control" v-model="recordToEdit.fine">
                <option :value="null">Не выбрано</option>
                <option v-for="fine in fines" :key="fine.id" :value="fine.id">
                  {{ fine.fineType }} - {{ fine.amount }} руб.
                </option>
              </select>
              <label>Штраф</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateRecord">
              Сохранить
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