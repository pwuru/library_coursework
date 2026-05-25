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

function cardAddPictureChange(event) {
  const file = event.target.files[0];
  if (file) {
    cardAddImageUrl.value = URL.createObjectURL(file);
  } else {
    cardAddImageUrl.value = null;
  }
}

async function fetchCards() {
  loading.value = true;
  const r = await axios.get("/api/registrationCards/");
  cards.value = r.data;
  loading.value = false;
}

async function onCardAdd() {
  const formData = new FormData();

  formData.append('photo', cardPictureRef.value.files[0]);

  formData.append('user', cardToAdd.value.user)
  await axios.post("/api/registrationCards/", formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  await fetchCards();
  cardToAdd.value = {};
  cardAddImageUrl.value = null;
  if (cardPictureRef.value) {
    cardPictureRef.value.value = '';
  }
}

async function onUpdateCard() {
  await axios.put(`/api/registrationCards/${cardToEdit.value.id}/`, {
    photo: cardToEdit.value.photo,
    user: cardToEdit.value.user
  });
  await fetchCards();
}

async function onCardEditClick(card) {
  cardToEdit.value = { ...card };
}

async function onRemoveClick(card) {
  await axios.delete(`/api/registrationCards/${card.id}/`);
  await fetchCards();
}

onBeforeMount(async () => {
  await fetchCards();
})
</script>

<template>
  <div class="container-fluid px-4">
    <div class="p-2 px-0">
      <form @submit.prevent.stop="onCardAdd">
        <div class="row">
          <div class="col">
            <div class="form-floating">
              <input
                type="file"
                ref="cardPictureRef"
                class="form-control"
                required
                @change="cardAddPictureChange"
              />
              <label for="floatingInput">Фото</label>
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
        <div v-show="item.picture"><img :src="item.picture" style="max-height: 60px;"></div>
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
            <h1 class="modal-title fs-5" id="exampleModalLabel">Редактировать учетную карточку</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="form-floating mb-2">
              <input type="text" class="form-control" v-model="cardToEdit.photo" />
              <label>Фото</label>
            </div>
            <div class="form-floating mb-2">
              <input type="text" class="form-control" v-model="cardToEdit.user" />
              <label>ID пользователя</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button
              type="button"
              class="btn btn-primary"
              data-bs-dismiss="modal"
              @click="onUpdateCard"
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
.card-item {
  padding: 0.5rem 1rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
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