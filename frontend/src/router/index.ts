import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/Chat.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/auth/verify',
    name: 'VerifyToken',
    component: () => import('@/views/VerifyToken.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth) {
    if (!authStore.accessToken) {
      next({ name: 'Login' })
      return
    }

    if (authStore.tokenExpiry && Date.now() > authStore.tokenExpiry) {
      const refreshed = await authStore.attemptRefresh()
      if (!refreshed) {
        next({ name: 'Login' })
        return
      }
    }

    if (!authStore.user) {
      const result = await authStore.fetchUser()
      if (!result.success) {
        next({ name: 'Login' })
        return
      }
    }
  }

  next()
})

export default router