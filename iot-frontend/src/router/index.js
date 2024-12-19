import { createRouter, createWebHistory } from 'vue-router';
import App from '../App.vue';
import DeltaView from '../views/DeltaView.vue';
import MapAndChartsView from '../views/MapAndChartsView.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: App
  },
  {
    path: '/delta',
    name: 'DeltaView',
    component: DeltaView
  },
  {
    path: '/maps',
    name: 'MapAndChartsView',
    component: MapAndChartsView
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

export default router;
