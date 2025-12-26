<template>
  <div class="h-screen flex overflow-hidden bg-surface">
    <!-- 侧边栏 -->
    <aside class="w-20 lg:w-64 flex flex-col py-6 px-4 bg-surface border-r border-slate-200/50">
      <!-- Logo -->
      <div class="flex items-center space-x-3 px-2 mb-10">
        <div class="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white shadow-float">
          <el-icon :size="20"><Printer /></el-icon>
        </div>
        <span class="text-xl font-bold tracking-tight text-slate-800 hidden lg:block">PrintOS</span>
      </div>

      <!-- 导航菜单 -->
      <nav class="space-y-2 flex-1">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item flex items-center px-4 py-3 group"
          :class="{ 'active': $route.path === item.path }"
        >
          <el-icon :size="20" class="group-hover:scale-110 transition-transform">
            <component :is="item.icon" />
          </el-icon>
          <span class="ml-3 hidden lg:block">{{ item.name }}</span>
        </router-link>
      </nav>

      <!-- 用户信息 -->
      <div
        class="flex items-center px-2 py-3 mt-auto bg-white rounded-xl border border-slate-100 shadow-sm cursor-pointer hover:border-indigo-100"
        @click="handleLogout"
      >
        <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500"></div>
        <div class="ml-3 hidden lg:block flex-1">
          <p class="text-sm font-semibold text-slate-700">{{ userStore.userInfo?.username }}</p>
          <p class="text-xs text-slate-400">{{ getRoleLabel(userStore.userInfo?.role) }}</p>
        </div>
        <el-icon class="hidden lg:block text-slate-400"><Right /></el-icon>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="flex-1 flex flex-col overflow-hidden bg-surface">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'
import {
  DataBoard,
  DocumentAdd,
  Box,
  Setting,
  Printer,
  Right,
  User,
  Money,
  DataAnalysis
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 恢复用户信息
userStore.restoreUserInfo()

const menuItems = ref([
  { name: '仪表盘', path: '/dashboard', icon: DataBoard },
  { name: '销售开单', path: '/orders', icon: DocumentAdd },
  { name: '客户管理', path: '/customers', icon: User },
  { name: '收款管理', path: '/payments', icon: Money },
  { name: '财务报表', path: '/reports', icon: DataAnalysis },
  { name: '库存管理', path: '/materials', icon: Box },
  { name: '生产排程', path: '/production', icon: Setting }
])

const getRoleLabel = (role) => {
  const roleMap = {
    'ADMIN': '管理员',
    'SALES': '销售',
    'OPERATOR': '操作员'
  }
  return roleMap[role] || role
}

const handleLogout = () => {
  ElMessageBox.confirm('确认退出登录?', '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    router.push('/login')
  }).catch(() => {})
}
</script>
