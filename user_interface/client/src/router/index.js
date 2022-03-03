// import { createRouter, createWebHistory } from 'vue-router'
import Vue from 'vue'

import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
  { path: '/', name:"Home", component: () => import('../views/HomeView.vue'), props: true},
  { path: '/doc/:id', name:"Document", component: () => import('../views/DocumentView.vue'), props: true},
  { path: '/performance', name:"Performance", component: () => import('../views/PerformanceView.vue'), props: true},

]

// const router = createRouter({
//   history: createWebHistory(process.env.BASE_URL),
//   routes: routes,
//   linkExactActiveClass: 'active'
// })

const router = new VueRouter({
  routes: routes,
  mode: 'history'
})

export default router;
