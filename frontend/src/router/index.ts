import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/exchange',
    name: 'ExchangeRates',
    component: () => import('@/views/ExchangeRates.vue')
  },
  {
    path: '/exchange/:target',
    name: 'ExchangeDetail',
    component: () => import('@/views/ExchangeDetail.vue'),
    props: true
  },
  {
    path: '/interest',
    name: 'InterestRates',
    component: () => import('@/views/InterestRates.vue')
  },
  {
    path: '/interest/:code',
    name: 'InterestDetail',
    component: () => import('@/views/InterestDetail.vue'),
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router