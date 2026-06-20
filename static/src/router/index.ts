import { createRouter, createWebHistory } from 'vue-router'
import ExamView from '../views/ExamView.vue'
import MainMenuView from '../views/MainMenuView.vue'
import StatsView from '../views/StatsView.vue'
import StudyView from '../views/StudyView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'menu', component: MainMenuView },
    { path: '/egzamin/:cat', name: 'exam', component: ExamView },
    { path: '/statystyki', name: 'stats', component: StatsView },
    { path: '/nauka/:cat', name: 'study', component: StudyView },
  ],
})

export default router
