import { createApp } from 'vue'
import App from './App.vue'

import router from './router'

import 'bootstrap/dist/css/bootstrap.css';

import VueSidebarMenu from 'vue-sidebar-menu'
import 'vue-sidebar-menu/dist/vue-sidebar-menu.css'


createApp(App)
  .use(router)
  .use(VueSidebarMenu)
  .mount('#app')
  