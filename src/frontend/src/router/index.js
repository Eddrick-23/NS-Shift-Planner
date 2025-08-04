import { createWebHistory, createRouter } from 'vue-router'
import Grids from '../pages/Session.vue'

const routes = [
  { path: '/', component:Grids}
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
