<script setup>
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

const books = ref([]);
const loading = ref(false);
const bookToAdd = ref({})
const bookToEdit = ref({})
const bookPictureRef = ref();
const bookAddImageUrl = ref();
const bookEditPictureRef = ref();
const bookEditImageUrl = ref();
const showImageModal = ref(false);
const currentImageUrl = ref('');

function bookAddPictureChange(event) {
  const file = event.target.files[0];
  if (file) {
    bookAddImageUrl.value = URL.createObjectURL(file);
  } else {
    bookAddImageUrl.value = null;
  }
}

function bookEditPictureChange(event) {
  const file = event.target.files[0];
  if (file) {
    bookEditImageUrl.value = URL.createObjectURL(file);
  } else {
    bookEditImageUrl.value = null;
  }
}

async function fetchBooks() {
  loading.value = true;
  const r = await axios.get("/api/books/");
  books.value = r.data;
  loading.value = false;
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
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  await fetchBooks();
  bookToAdd.value = {};
  bookAddImageUrl.value = null;
  if (bookPictureRef.value) {
    bookPictureRef.value.value = '';
  }
}

async function onUpdateBook() {
  const formData = new FormData();
  
  if (bookEditPictureRef.value && bookEditPictureRef.value.files[0]) {
    formData.append('photo', bookEditPictureRef.value.files[0]);
  }
  
  formData.append('name', bookToEdit.value.name);
  formData.append('genre', bookToEdit.value.genre);
  formData.append('date', bookToEdit.value.date);
  formData.append('author', bookToEdit.value.author);
  
  await axios.put(`/api/books/${bookToEdit.value.id}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  await fetchBooks();
  bookEditImageUrl.value = null;
  if (bookEditPictureRef.value) {
    bookEditPictureRef.value.value = '';
  }
}

async function onBookEditClick(book) {
  bookToEdit.value = { ...book };
  if (book.photo) {
    bookEditImageUrl.value = book.photo.replace('localhost:5173', 'localhost:8000');
  } else {
    bookEditImageUrl.value = null;
  }
}

async function onRemoveClick(book) {
  await axios.delete(`/api/books/${book.id}/`);
  await fetchBooks();
}

function openImageModal(photoUrl) {
  currentImageUrl.value = photoUrl.replace('localhost:5173', 'localhost:8000');
  showImageModal.value = true;
}

onBeforeMount(async () => {
  await fetchBooks();
})
</script>

<template>
  <div class="container-fluid px-4">
    <div class="p-2 px-0">
      <form @submit.prevent.stop="onBookAdd" enctype="multipart/form-data">
        <div class="row">
          <div class="col">
            <div class="form-floating">
              <input
                type="file"
                ref="bookPictureRef"
                class="form-control"
                @change="bookAddPictureChange"
              />
              <label>Фото</label>
            </div>
          </div>
          <div class="col-auto">
            <img :src="bookAddImageUrl" style="max-height: 60px;" alt="">
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="bookToAdd.name"
                required
              />
              <label>Название</label>
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
                type="number"
                class="form-control"
                v-model="bookToAdd.date"
                required
              />
              <label>Год публикации</label>
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
            <button class="btn btn-primary"><i class="bi bi-plus-lg"></i></button>
          </div>
        </div>
      </form>
    </div>

    <div class="px-0">
      <div v-for="item in books" class="book-item mb-2 p-2 border rounded">
        <div>
          <strong>{{ item.name }}</strong> - {{ item.author }} ({{ item.date }}, {{ item.genre }})
        </div>
        <div v-if="item.photo" class="book-photo">
          <img 
            :src="item.photo.replace('localhost:5173', 'localhost:8000')" 
            style="max-height: 60px; cursor: pointer;" 
            alt="Фото книги"
            @click="openImageModal(item.photo)"
            data-bs-toggle="modal"
            data-bs-target="#imageModal"
          >
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
              <input type="file" class="form-control" ref="bookEditPictureRef" @change="bookEditPictureChange" />
              <label>Фото</label>
            </div>
            <div class="mb-2">
              <img :src="bookEditImageUrl" style="max-height: 100px;" alt="Фото">
            </div>
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

    <div class="modal fade" id="imageModal" tabindex="-1" data-bs-backdrop="static">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Просмотр фото</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body text-center">
            <img :src="currentImageUrl" style="max-width: 100%; max-height: 70vh;" alt="Фото">
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              <i class="bi bi-x-lg"></i>
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