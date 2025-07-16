import { createWebHistory, createRouter } from 'vue-router'

import HomeView from '../pages/Home.vue'
import AboutView from '../pages/About.vue'
import Grids from '../pages/Session.vue'

const routes = [
  { path: '/', component: HomeView },
  { path: '/about', component: AboutView },
  { path: '/session', component:Grids}
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
