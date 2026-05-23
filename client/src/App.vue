<script setup>
import { computed, ref, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

const books = ref([]);
const loading = ref(false);

async function fetchBooks() {
  loading.value = true;
  const r = await axios.get("/api/books/");
  books.value = r.data;
  loading.value = false;
}

async function onLoadClick() {
  await fetchBooks()
}

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

const bookToAdd = ref({});

async function onBookAdd() {
  await axios.post("/api/books/", {
    ...bookToAdd.value,
  });
  await fetchBooks(); // переподтягиваю
}

async function onRemoveClick(book) {
  await axios.delete(`/api/books/${book.id}/`);
  await fetchBooks(); // переподтягиваю
}

</script>

<template>

<!-- ТУТ ПОДКЛЮЧИЛ обработчик отправки формы -->
<form @submit.prevent.stop="onBookAdd">
  <div class="row">
    <div class="col">
      <div class="form-floating">
        <!-- ТУТ ПОДКЛЮЧИЛ bookToAdd.name -->
        <input
          type="text"
          class="form-control"
          v-model="bookToAdd.name"
          required
        />
        <label for="floatingInput">Название</label>
      </div>
    </div>
    <div class="col-auto">
        <!-- А ТУТ ПОДКЛЮЧИЛ К select -->
      <div class="form-floating">
        <select class="form-select" v-model="bookToAdd.reader" required>
          <option :value="r.id" v-for="r in readers">{{ r.name }}</option>
        </select>
        <label for="floatingInput">Группа</label>
      </div>
    </div>
    <div class="col-auto">
      <button class="btn btn-primary">
        Добавить
      </button>
    </div>
  </div>
</form>

</template>

<style scoped>
</style>
