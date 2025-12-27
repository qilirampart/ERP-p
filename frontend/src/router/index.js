/**
 * Vue Router配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

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
        meta: { title: '仪表盘', roles: ['ADMIN', 'SALES', 'OPERATOR'] }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/Orders.vue'),
        meta: { title: '销售开单', roles: ['ADMIN', 'SALES'] }
      },
      {
        path: 'materials',
        name: 'Materials',
        component: () => import('@/views/Materials.vue'),
        meta: { title: '库存管理', roles: ['ADMIN', 'OPERATOR'] }
      },
      {
        path: 'production',
        name: 'Production',
        component: () => import('@/views/Production.vue'),
        meta: { title: '生产排程', roles: ['ADMIN', 'OPERATOR'] }
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('@/views/Customers.vue'),
        meta: { title: '客户管理', roles: ['ADMIN', 'SALES'] }
      },
      {
        path: 'payments',
        name: 'Payments',
        component: () => import('@/views/Payments.vue'),
        meta: { title: '收款管理', roles: ['ADMIN', 'SALES'] }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/Reports.vue'),
        meta: { title: '财务报表', roles: ['ADMIN', 'SALES'] }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { title: '用户管理', roles: ['ADMIN'] }
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

        // 检查角色权限
        const requiredRoles = to.meta.roles
        if (requiredRoles && requiredRoles.length > 0) {
          const userRole = userStore.userInfo?.role
          if (!requiredRoles.includes(userRole)) {
            console.log(`[路由守卫] 权限不足，需要角色: ${requiredRoles}，当前角色: ${userRole}`)
            ElMessage.error('您没有权限访问此页面')
            // 跳转到仪表盘或首页
            next('/dashboard')
            return
          }
        }

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
