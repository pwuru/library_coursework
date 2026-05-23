<script setup>
import { computed, ref, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

const books = ref([]);
const loading = ref(false);
const bookToAdd = ref({})
const bookToEdit = ref({})

async function fetchBooks() {
  loading.value = true;
  const r = await axios.get("/api/books/");
  books.value = r.data;
  loading.value = false;
}

async function onBookAdd() {
  await axios.post("/api/books/", {
    ...bookToAdd.value,
  });
  await fetchBooks(); // переподтягиваю
}

async function onUpdateBook() {
  await axios.put(`/api/books/${bookToEdit.value.id}/`, {
    name: bookToEdit.value.name,
    genre: bookToEdit.value.genre,
    date: bookToEdit.value.date,
    author: bookToEdit.value.author
  });
  await fetchBooks();
}

async function onBookEditClick(book) {
  bookToEdit.value = { ...book };
}

async function onRemoveClick(book) {
  await axios.delete(`/api/books/${book.id}/`);
  await fetchBooks(); // переподтягиваю
}

onBeforeMount(async () => {
  await fetchBooks();
})

</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <form @submit.prevent.stop="onBookAdd">
        <div class="row">
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="bookToAdd.name"
                required
              />
              <label for="floatingInput">Название</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="bookToAdd.genre"
                required
              />
              <label>Жанр</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="bookToAdd.date"
                required
              />
              <label>Дата публикации</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="bookToAdd.author"
                required
              />
              <label>Автор</label>
            </div>
          </div>
          <div class="col-auto">
            <button class="btn btn-primary">Добавить</button>
          </div>
        </div>
      </form>
    </div>

    <div v-for="item in books" class="book-item mb-2 p-2 border rounded">
      <div>
        <strong>{{ item.name }}</strong> - {{ item.author }} ({{ item.date }}, {{ item.genre }})
      </div>
      <div class="mt-2">
        <button
          class="btn btn-success me-2"
          @click="onBookEditClick(item)"
          data-bs-toggle="modal"
          data-bs-target="#editBookModal"
        >
          Редактировать
        </button>
        <button class="btn btn-danger" @click="onRemoveClick(item)">
          Удалить
        </button>
      </div>
    </div>

    <div class="modal fade" id="editBookModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">Редактировать книгу</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
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
              <input type="text" class="form-control" v-model="bookToEdit.date" />
              <label>Дата публикации</label>
            </div>
            <div class="form-floating mb-2">
              <input type="text" class="form-control" v-model="bookToEdit.author" />
              <label>Автор</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button
              type="button"
              class="btn btn-primary"
              data-bs-dismiss="modal"
              @click="onUpdateBook"
            >
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.book-item {
  padding: 0.5rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
  display: grid;
  grid-template-columns: 1fr auto;
  align-content: center;
  align-items: center;
  gap: 16px;
}
</style>
