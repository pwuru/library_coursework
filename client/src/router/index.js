import { createRouter, createWebHistory } from 'vue-router';
import RegistrationCardsView from '../views/RegistrationCardsView.vue';
import RecordsView from '../views/RecordsView.vue';
import BooksView from '../views/BooksView.vue';
import FinesView from '../views/FinesView.vue';
import UserProfilesView from '../views/UserProfilesView.vue';
import LoginView from '../views/LoginView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
      {
        path: '/',
        name: 'Login',
        component: LoginView
      },
      {
        path: '/books',
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
      },
      {
        path: '/user-profiles',
        name: 'UserProfiles',
        component: UserProfilesView
      }
    ]
})

export default router
