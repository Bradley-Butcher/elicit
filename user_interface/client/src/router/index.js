import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name:"Home", component: () => import('../views/HomeView.vue') },
  { path: '/doc/:id', name:"Document", component: () => import('../views/DocumentView.vue') },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes: routes
})

export default router;
