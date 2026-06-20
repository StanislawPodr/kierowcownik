import { createRouter, createWebHistory } from 'vue-router'
import ExamView from '../views/ExamView.vue'
import MainMenuView from '../views/MainMenuView.vue'
import StatsView from '../views/StatsView.vue'
import StudyView from '../views/StudyView.vue'
import RegistrationView from '../views/RegistrationView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'menu', component: MainMenuView },
    { path: '/egzamin/:cat', name: 'exam', component: ExamView },
    { path: '/statystyki', name: 'stats', component: StatsView },
    { path: '/nauka/:cat', name: 'study', component: StudyView },
    { path: '/rejestracja', name: 'register', component: RegistrationView},
    { path: '/logowanie', name: 'login', component: LoginView}
  ],
})

export default router
