<script setup>
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

const cards = ref([]);
const loading = ref(false);
const cardToAdd = ref({})
const cardToEdit = ref({})
const cardPictureRef = ref();
const cardAddImageUrl = ref();
const cardEditPictureRef = ref();
const cardEditImageUrl = ref();
const showImageModal = ref(false);
const currentImageUrl = ref('');
const stats = ref({});

function cardAddPictureChange(event) {
  const file = event.target.files[0];
  if (file) {
    cardAddImageUrl.value = URL.createObjectURL(file);
  } else {
    cardAddImageUrl.value = null;
  }
}

function cardEditPictureChange(event) {
  const file = event.target.files[0];
  if (file) {
    cardEditImageUrl.value = URL.createObjectURL(file);
  } else {
    cardEditImageUrl.value = null;
  }
}

async function fetchCards() {
  loading.value = true;
  const r = await axios.get("/api/registrationCards/");
  cards.value = r.data;
  loading.value = false;
}

async function fetchStats() {
  const r = await axios.get("/api/registrationCards/stats/");
  stats.value = r.data;
}

async function onCardAdd() {
  const formData = new FormData();

  if (cardPictureRef.value && cardPictureRef.value.files[0]) {
    formData.append('photo', cardPictureRef.value.files[0]);
  }

  formData.append('user', cardToAdd.value.user);
  await axios.post("/api/registrationCards/", formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  await fetchCards();
  await fetchStats();
  cardToAdd.value = {};
  cardAddImageUrl.value = null;
  if (cardPictureRef.value) {
    cardPictureRef.value.value = '';
  }
}

async function onUpdateCard() {
  const formData = new FormData();
  
  if (cardEditPictureRef.value && cardEditPictureRef.value.files[0]) {
    formData.append('photo', cardEditPictureRef.value.files[0]);
  }
  
  formData.append('user', cardToEdit.value.user);
  
  await axios.put(`/api/registrationCards/${cardToEdit.value.id}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  await fetchCards();
  await fetchStats();
  cardEditImageUrl.value = null;
  if (cardEditPictureRef.value) {
    cardEditPictureRef.value.value = '';
  }
}

async function onCardEditClick(card) {
  cardToEdit.value = { ...card };
  if (card.photo) {
    cardEditImageUrl.value = card.photo.replace('localhost:5173', 'localhost:8000');
  } else {
    cardEditImageUrl.value = null;
  }
}

async function onRemoveClick(card) {
  await axios.delete(`/api/registrationCards/${card.id}/`);
  await fetchCards();
  await fetchStats();
}

function openImageModal(photoUrl) {
  currentImageUrl.value = photoUrl.replace('localhost:5173', 'localhost:8000');
  showImageModal.value = true;
}

onBeforeMount(async () => {
  await fetchCards();
  await fetchStats();
})
</script>

<template>
  <div class="container-fluid px-4">
    <div class="d-flex gap-3 p-2 border rounded mb-3">
      <span>Всего карточек: {{ stats.count || 0 }}</span>
      <span>Средний ID: {{ stats.avg_id ? Math.round(stats.avg_id) : 0 }}</span>
      <span>Максимальный ID: {{ stats.max_id || 0 }}</span>
      <span>Минимальный ID: {{ stats.min_id || 0 }}</span>
    </div>
    <div class="p-2 px-0">
      <form @submit.prevent.stop="onCardAdd" enctype="multipart/form-data">
        <div class="row">
          <div class="col">
            <div class="form-floating">
              <input
                type="file"
                ref="cardPictureRef"
                class="form-control"
                @change="cardAddPictureChange"
              />
              <label>Фото</label>
            </div>
          </div>
          <div class="col-auto">
            <img :src="cardAddImageUrl" style="max-height: 60px;" alt="">
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="cardToAdd.user"
                required
              />
              <label>ID пользователя</label>
            </div>
          </div>
          <div class="col-auto">
            <button class="btn btn-primary"><i class="bi bi-plus-lg"></i></button>
          </div>
        </div>
      </form>
    </div>

    <div class="px-0">
      <div v-for="item in cards" class="card-item mb-2 p-2 border rounded">
        <div>ID карточки: <strong>{{ item.id }}</strong>, ID пользователя: <strong>{{ item.user }}</strong></div>
        <div v-if="item.photo" class="card-photo">
          <img 
            :src="item.photo.replace('localhost:5173', 'localhost:8000')" 
            style="max-height: 60px; cursor: pointer;" 
            alt="Фото карточки"
            @click="openImageModal(item.photo)"
            data-bs-toggle="modal"
            data-bs-target="#imageModal"
          >
        </div>
        <div v-else>Нет фото</div>
        <div class="mt-2">
          <button class="btn btn-success me-2" @click="onCardEditClick(item)" data-bs-toggle="modal" data-bs-target="#editCardModal">
            <i class="bi bi-pencil-fill"></i>
          </button>
          <button class="btn btn-danger" @click="onRemoveClick(item)"><i class="bi bi-x"></i></button>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editCardModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5">Редактировать учетную карточку</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="form-floating mb-2">
              <input type="file" class="form-control" ref="cardEditPictureRef" @change="cardEditPictureChange" />
              <label>Фото</label>
            </div>
            <div class="mb-2">
              <img :src="cardEditImageUrl" style="max-height: 100px;" alt="Текущее фото">
            </div>
            <div class="form-floating mb-2">
              <input type="text" class="form-control" v-model="cardToEdit.user" />
              <label>ID пользователя</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              <i class="bi bi-x-lg"></i>
            </button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateCard">
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
.card-item {
  padding: 0.5rem 1rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-photo {
  margin-right: 20px;
}

.card-item > div:first-child {
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