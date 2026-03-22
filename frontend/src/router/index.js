import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/secret/new',
    name: 'SecretNew',
    component: () => import('../views/SecretForm.vue'),
    meta: { requiresAuth: true, requiresUnlock: true },
  },
  {
    path: '/secret/:id',
    name: 'SecretEdit',
    component: () => import('../views/SecretForm.vue'),
    meta: { requiresAuth: true, requiresUnlock: true },
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('../views/CategoryView.vue'),
    meta: { requiresAuth: true, requiresUnlock: true },
  },
  {
    path: '/import-export',
    name: 'ImportExport',
    component: () => import('../views/ImportExportView.vue'),
    meta: { requiresAuth: true, requiresUnlock: true },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) {
    return { name: 'Login' }
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { name: 'Dashboard' }
  }
  // 有 token 但没有用户信息时，自动获取
  if (auth.token && !auth.currentUser) {
    await auth.fetchMe()
    if (to.meta.requiresAdmin && !auth.isAdmin) {
      return { name: 'Dashboard' }
    }
  }
  // 检查保险箱解锁状态（需要等待用户在 Dashboard 解锁）
  if (to.meta.requiresUnlock && !auth.vaultUnlocked) {
    // 如果需要解锁但未解锁，返回主页（主页会自动弹出解锁弹窗）
    return { name: 'Dashboard' }
  }
})

export default router
