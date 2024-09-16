import { createRouter, createWebHistory } from 'vue-router';
import App from '../App.vue';
import DeltaView from '../views/DeltaView.vue'; // 修改为 DeltaView

const routes = [
  {
    path: '/',
    name: 'Home',
    component: App
  },
  {
    path: '/delta',
    name: 'DeltaView',
    component: DeltaView  // 修改为 DeltaView
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

export default router;
