import { createRouter, createWebHistory } from 'vue-router';
import RegistrationCardsView from '../views/RegistrationCardsView.vue';
import RecordsView from '../views/RecordsView.vue';
import BooksView from '../views/BooksView.vue';
import FinesView from '../views/FinesView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
      {
        path: '/',
        name: 'BooksView',
        component: BooksView
      },
      {
        path: '/registration-cards',
        name: 'RegistrationCardsView',
        component: RegistrationCardsView
      },
      {
        path: '/records',
        name: 'RecordsView',
        component: RecordsView
      },
      {
        path: '/fines',
        name: 'FinesView',
        component: FinesView
      }
    ]
})

export default router
