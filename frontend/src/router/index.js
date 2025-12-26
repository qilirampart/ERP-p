/**
 * Vue Router配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/Orders.vue'),
        meta: { title: '销售开单' }
      },
      {
        path: 'materials',
        name: 'Materials',
        component: () => import('@/views/Materials.vue'),
        meta: { title: '库存管理' }
      },
      {
        path: 'production',
        name: 'Production',
        component: () => import('@/views/Production.vue'),
        meta: { title: '生产排程' }
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('@/views/Customers.vue'),
        meta: { title: '客户管理' }
      },
      {
        path: 'payments',
        name: 'Payments',
        component: () => import('@/views/Payments.vue'),
        meta: { title: '收款管理' }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/Reports.vue'),
        meta: { title: '财务报表' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)

  if (requiresAuth) {
    if (!userStore.token) {
      // 没有token，跳转登录
      console.log('[路由守卫] 未找到token，跳转登录页')
      next('/login')
    } else {
      // 有token，验证有效性
      console.log('[路由守卫] 发现token，验证有效性...')
      const isValid = await userStore.validateToken()

      if (!isValid) {
        // Token无效，清除并跳转登录
        console.log('[路由守卫] Token无效，跳转登录页')
        userStore.logout()
        next('/login')
      } else {
        // Token有效，恢复用户信息
        if (!userStore.userInfo) {
          userStore.restoreUserInfo()
        }
        console.log('[路由守卫] Token有效，允许访问')
        next()
      }
    }
  } else if (to.path === '/login' && userStore.token) {
    // 已登录用户访问登录页，验证token后决定
    const isValid = await userStore.validateToken()
    if (isValid) {
      next('/')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
