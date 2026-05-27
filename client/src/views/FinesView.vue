<script setup>
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

const fines = ref([]);
const loading = ref(false);
const fineToAdd = ref({})
const fineToEdit = ref({})

async function fetchFines() {
  loading.value = true;
  const r = await axios.get("/api/fines/");
  fines.value = r.data;
  loading.value = false;
}

async function onFineAdd() {
  await axios.post("/api/fines/", {
    ...fineToAdd.value,
  });
  await fetchFines();
  fineToAdd.value = {};
}

async function onUpdateFine() {
  await axios.put(`/api/fines/${fineToEdit.value.id}/`, {
    fineType: fineToEdit.value.fineType,
    amount: fineToEdit.value.amount,
    date: fineToEdit.value.date
  });
  await fetchFines();
}

async function onFineEditClick(fine) {
  fineToEdit.value = { ...fine };
}

async function onRemoveClick(fine) {
  await axios.delete(`/api/fines/${fine.id}/`);
  await fetchFines();
}

onBeforeMount(async () => {
  await fetchFines();
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
              <label for="floatingInput">Тип штрафа</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="number"
                class="form-control"
                v-model="fineToAdd.amount"
                required
              />
              <label>Сумма</label>
            </div>
          </div>
          <div class="col">
            <div class="form-floating">
              <input
                type="date"
                class="form-control"
                v-model="fineToAdd.date"
                required
              />
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
      <div v-for="item in fines" class="fine-item mb-2 p-2 border rounded">
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