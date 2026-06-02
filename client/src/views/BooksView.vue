<script setup>
import { ref, onBeforeMount, computed } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

const books = ref([]);
const stats = ref({});
const loading = ref(false);
const bookToAdd = ref({})
const bookToEdit = ref({})
const bookPictureRef = ref();
const bookAddImageUrl = ref();
const showFilters = ref(false);
const filters = ref({
  name: "",
  genre: "",
  author: ""
});

const genresList = ['Роман', 'Детектив', 'Фантастика', 'Поэзия', 'Драма', 'Приключения', 'Комедия', 'Фэнтези'];

async function fetchBooks() {
  loading.value = true;
  const r = await axios.get("/api/books/");
  books.value = r.data;
  loading.value = false;
}

async function fetchStats() {
  const r = await axios.get("/api/books/stats/");
  stats.value = r.data;
}

async function onBookAdd() {
  const formData = new FormData();
  if (bookPictureRef.value && bookPictureRef.value.files[0]) {
    formData.append('photo', bookPictureRef.value.files[0]);
  }
  formData.append('name', bookToAdd.value.name);
  formData.append('genre', bookToAdd.value.genre);
  formData.append('date', bookToAdd.value.date);
  formData.append('author', bookToAdd.value.author);
  await axios.post("/api/books/", formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  await fetchBooks();
  await fetchStats();
  bookToAdd.value = {};
  bookAddImageUrl.value = null;
  if (bookPictureRef.value) {
    bookPictureRef.value.value = '';
  }
}

function bookAddPictureChange(event) {
  const file = event.target.files[0];
  if (file) {
    bookAddImageUrl.value = URL.createObjectURL(file);
  } else {
    bookAddImageUrl.value = null;
  }
}

async function onUpdateBook() {
  await axios.put(`/api/books/${bookToEdit.value.id}/`, {
    name: bookToEdit.value.name,
    genre: bookToEdit.value.genre,
    date: bookToEdit.value.date,
    author: bookToEdit.value.author
  });
  await fetchBooks();
  await fetchStats();
}

async function onBookEditClick(book) {
  bookToEdit.value = { ...book };
}

async function onRemoveClick(book) {
  await axios.delete(`/api/books/${book.id}/`);
  await fetchBooks();
  await fetchStats();
}

function clearFilters() {
  filters.value = {
    name: "",
    genre: "",
    author: ""
  };
}

const filteredBooks = computed(() => {
  return books.value.filter(book => {
    if (filters.value.name && !book.name?.toLowerCase().includes(filters.value.name.toLowerCase())) return false;
    if (filters.value.genre && book.genre !== filters.value.genre) return false;
    if (filters.value.author && !book.author?.toLowerCase().includes(filters.value.author.toLowerCase())) return false;
    return true;
  });
});

async function exportToExcel() {
  try {
    const response = await axios.get("/api/books/export-excel/", {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', response.headers['content-disposition'].split('filename=')[1]);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Ошибка при экспорте:', error);
  }
}

onBeforeMount(async () => {
  await fetchBooks();
  await fetchStats();
})
</script>

<template>
  <div class="container-fluid px-4">
    <div class="d-flex gap-3 p-2 border rounded mb-3">
      <span>Всего книг: {{ stats.count || 0 }}</span>
      <span>Средний год: {{ stats.avg_year ? Math.round(stats.avg_year) : 0 }}</span>
      <span>Самый новый: {{ stats.max_year || 0 }}</span>
      <span>Самый старый: {{ stats.min_year || 0 }}</span>
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
        <div class="col-md-4">
          <input v-model="filters.name" type="text" class="form-control form-control-sm" placeholder="Название">
        </div>
        <div class="col-md-3">
          <select v-model="filters.genre" class="form-control form-control-sm">
            <option value="">Все жанры</option>
            <option v-for="genre in genresList" :key="genre" :value="genre">{{ genre }}</option>
          </select>
        </div>
        <div class="col-md-3">
          <input v-model="filters.author" type="text" class="form-control form-control-sm" placeholder="Автор">
        </div>
        <div class="col-md-2">
          <button class="btn btn-sm btn-outline-danger w-100" @click="clearFilters">Очистить</button>
        </div>
      </div>
    </div>

    <div class="p-2 px-0">
      <form @submit.prevent.stop="onBookAdd" enctype="multipart/form-data">
        <div class="row">
          <div class="col">
            <div class="form-floating">
              <input type="file" ref="bookPictureRef" class="form-control" @change="bookAddPictureChange" />
              <label>Фото</label>
            </div>
          </div>
          <div class="col-auto">
            <img :src="bookAddImageUrl" style="max-height: 60px;" alt="">
          </div>
          <div class="col">
            <div class="form-floating">
              <input type="text" class="form-control" v-model="bookToAdd.name" required />
              <label>Название</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input type="text" class="form-control" v-model="bookToAdd.genre" required />
              <label>Жанр</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input type="number" class="form-control" v-model="bookToAdd.date" required />
              <label>Год публикации</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input type="text" class="form-control" v-model="bookToAdd.author" required />
              <label>Автор</label>
            </div>
          </div>
          <div class="col-auto">
            <button class="btn btn-primary"><i class="bi bi-plus-lg"></i></button>
          </div>
        </div>
      </form>
    </div>

    <div class="px-0">
      <div v-for="item in filteredBooks" class="book-item mb-2 p-2 border rounded">
        <div>
          <strong>{{ item.name }}</strong> - {{ item.author }} ({{ item.date }}, {{ item.genre }})
        </div>
        <div v-if="item.photo" class="book-photo">
          <img :src="item.photo.replace('localhost:5173', 'localhost:8000')" style="max-height: 60px;" alt="Фото книги">
        </div>
        <div v-else>Нет фото</div>
        <div class="mt-2">
          <button class="btn btn-success me-2" @click="onBookEditClick(item)" data-bs-toggle="modal" data-bs-target="#editBookModal">
            <i class="bi bi-pencil-fill"></i>
          </button>
          <button class="btn btn-danger" @click="onRemoveClick(item)"><i class="bi bi-x"></i></button>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editBookModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5">Редактировать книгу</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="form-floating mb-2">
              <input type="text" class="form-control" v-model="bookToEdit.name" />
              <label>Название</label>
            </div>
            <div class="form-floating mb-2">
              <input type="text" class="form-control" v-model="bookToEdit.genre" />
              <label>Жанр</label>
            </div>
            <div class="form-floating mb-2">
              <input type="number" class="form-control" v-model="bookToEdit.date" />
              <label>Год публикации</label>
            </div>
            <div class="form-floating mb-2">
              <input type="text" class="form-control" v-model="bookToEdit.author" />
              <label>Автор</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              <i class="bi bi-x-lg"></i>
            </button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateBook">
              <i class="bi bi-check-lg"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.book-item {
  padding: 0.5rem 1rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.book-photo {
  margin-right: 20px;
}

.book-item > div:first-child {
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