<template>
  <div class="h-screen flex overflow-hidden bg-surface">
    <!-- 侧边栏 - 现代设计 -->
    <aside class="w-64 bg-white border-r border-slate-100 flex flex-col py-6 px-4 flex-shrink-0 shadow-[4px_0_24px_rgba(0,0,0,0.02)]">
      <!-- Logo -->
      <div class="flex items-center space-x-3 px-3 mb-8">
        <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white shadow-lg shadow-indigo-200">
          <el-icon :size="18"><Printer /></el-icon>
        </div>
        <span class="text-xl font-bold text-slate-800 tracking-tight">PrintOS</span>
      </div>

      <!-- 新建工单按钮 -->
      <div class="mb-6 px-2">
        <button
          @click="createOrder"
          class="w-full bg-slate-900 hover:bg-slate-800 text-white py-2.5 rounded-xl text-sm font-medium transition-colors shadow-md flex items-center justify-center group"
        >
          <el-icon class="mr-2 group-hover:rotate-90 transition-transform"><Plus /></el-icon>
          新建工单
        </button>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 space-y-8 overflow-y-auto">
        <!-- 数据中心 -->
        <div v-if="visibleMenus.dashboard">
          <div class="px-4 text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">数据中心</div>
          <ul class="space-y-1">
            <li v-for="item in visibleMenus.dashboard" :key="item.path">
              <router-link
                :to="item.path"
                class="nav-item flex items-center px-3 py-2.5 rounded-lg text-sm font-medium group relative transition-all"
                :class="$route.path === item.path
                  ? 'bg-indigo-50 text-indigo-600 active'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'"
              >
                <el-icon
                  :size="18"
                  class="mr-3 transition-colors"
                  :class="$route.path === item.path ? 'text-indigo-600' : 'text-slate-400 group-hover:text-slate-600'"
                >
                  <component :is="item.icon" />
                </el-icon>
                {{ item.name }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- 业务管理 -->
        <div v-if="visibleMenus.business">
          <div class="px-4 text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">业务管理</div>
          <ul class="space-y-1">
            <li v-for="item in visibleMenus.business" :key="item.path">
              <router-link
                :to="item.path"
                class="nav-item flex items-center px-3 py-2.5 rounded-lg text-sm font-medium group relative transition-all"
                :class="$route.path === item.path
                  ? 'bg-indigo-50 text-indigo-600 active'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'"
              >
                <el-icon
                  :size="18"
                  class="mr-3 transition-colors"
                  :class="$route.path === item.path ? 'text-indigo-600' : 'text-slate-400 group-hover:text-slate-600'"
                >
                  <component :is="item.icon" />
                </el-icon>
                {{ item.name }}
                <span v-if="item.badge" class="ml-auto bg-red-100 text-red-600 py-0.5 px-2 rounded-full text-[10px] font-bold">
                  {{ item.badge }}
                </span>
              </router-link>
            </li>
          </ul>
        </div>

        <!-- 财务报表 -->
        <div v-if="visibleMenus.finance">
          <div class="px-4 text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">财务报表</div>
          <ul class="space-y-1">
            <li v-for="item in visibleMenus.finance" :key="item.path">
              <router-link
                :to="item.path"
                class="nav-item flex items-center px-3 py-2.5 rounded-lg text-sm font-medium group relative transition-all"
                :class="$route.path === item.path
                  ? 'bg-indigo-50 text-indigo-600 active'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'"
              >
                <el-icon
                  :size="18"
                  class="mr-3 transition-colors"
                  :class="$route.path === item.path ? 'text-indigo-600' : 'text-slate-400 group-hover:text-slate-600'"
                >
                  <component :is="item.icon" />
                </el-icon>
                {{ item.name }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- 系统管理 -->
        <div v-if="visibleMenus.system">
          <div class="px-4 text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">系统管理</div>
          <ul class="space-y-1">
            <li v-for="item in visibleMenus.system" :key="item.path">
              <router-link
                :to="item.path"
                class="nav-item flex items-center px-3 py-2.5 rounded-lg text-sm font-medium group relative transition-all"
                :class="$route.path === item.path
                  ? 'bg-indigo-50 text-indigo-600 active'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'"
              >
                <el-icon
                  :size="18"
                  class="mr-3 transition-colors"
                  :class="$route.path === item.path ? 'text-indigo-600' : 'text-slate-400 group-hover:text-slate-600'"
                >
                  <component :is="item.icon" />
                </el-icon>
                {{ item.name }}
              </router-link>
            </li>
          </ul>
        </div>
      </nav>

      <!-- 用户信息 -->
      <div class="mt-auto pt-4 border-t border-slate-100">
        <el-dropdown @command="handleUserMenuCommand" trigger="click">
          <div class="flex items-center p-2 rounded-xl hover:bg-slate-50 cursor-pointer transition-colors group">
            <div class="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-semibold text-sm border border-slate-200">
              {{ userStore.userInfo?.username?.charAt(0).toUpperCase() }}
            </div>
            <div class="ml-3 flex-1 overflow-hidden">
              <p class="text-sm font-semibold text-slate-700 group-hover:text-indigo-600 truncate">
                {{ userStore.userInfo?.username }}
              </p>
              <p class="text-xs text-slate-400 truncate">{{ getRoleLabel(userStore.userInfo?.role) }}</p>
            </div>
            <el-icon class="text-slate-400"><MoreFilled /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="changePassword">
                <el-icon><EditPen /></el-icon>
                修改密码
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="flex-1 overflow-hidden bg-surface">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  DataBoard,
  DocumentAdd,
  Box,
  Setting,
  Printer,
  User,
  Money,
  DataAnalysis,
  EditPen,
  SwitchButton,
  Plus,
  MoreFilled
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 恢复用户信息
userStore.restoreUserInfo()

// 分组菜单（静态配置，不需要响应式）
const menuGroups = {
  dashboard: [
    { name: '仪表盘', path: '/dashboard', icon: DataBoard, roles: ['ADMIN', 'SALES', 'OPERATOR'] }
  ],
  business: [
    { name: '销售开单', path: '/orders', icon: DocumentAdd, roles: ['ADMIN', 'SALES'] },
    { name: '客户管理', path: '/customers', icon: User, roles: ['ADMIN', 'SALES'] },
    { name: '生产排程', path: '/production', icon: Setting, roles: ['ADMIN', 'OPERATOR'] },
    { name: '库存管理', path: '/materials', icon: Box, badge: null, roles: ['ADMIN', 'OPERATOR'] }
  ],
  finance: [
    { name: '收款管理', path: '/payments', icon: Money, roles: ['ADMIN', 'SALES'] },
    { name: '财务报表', path: '/reports', icon: DataAnalysis, roles: ['ADMIN', 'SALES'] }
  ],
  system: [
    { name: '用户管理', path: '/users', icon: User, roles: ['ADMIN'] }
  ]
}

// 根据用户角色过滤菜单
const visibleMenus = computed(() => {
  const userRole = userStore.userInfo?.role
  if (!userRole) return {}

  const result = {}
  Object.keys(menuGroups).forEach(groupKey => {
    const filteredItems = menuGroups[groupKey].filter(item =>
      item.roles.includes(userRole)
    )
    if (filteredItems.length > 0) {
      result[groupKey] = filteredItems
    }
  })
  return result
})

const getRoleLabel = (role) => {
  const roleMap = {
    'ADMIN': '管理员',
    'SALES': '销售',
    'OPERATOR': '操作员'
  }
  return roleMap[role] || role
}

// 新建工单
const createOrder = () => {
  router.push('/orders')
}

// 用户菜单命令处理
const handleUserMenuCommand = (command) => {
  if (command === 'logout') {
    handleLogout()
  } else if (command === 'changePassword') {
    handleChangePassword()
  }
}

// 退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确认退出登录?', '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }).catch(() => {})
}

// 修改密码
const handleChangePassword = async () => {
  const { value } = await ElMessageBox.prompt('', '修改密码', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    inputType: 'password',
    inputPlaceholder: '请输入新密码',
    inputPattern: /.{6,}/,
    inputErrorMessage: '密码至少6位',
    customClass: 'change-password-box',
    beforeClose: async (action, instance, done) => {
      if (action === 'confirm') {
        const newPassword = instance.inputValue

        // 二次确认密码
        try {
          const { value: confirmPassword } = await ElMessageBox.prompt('', '确认新密码', {
            confirmButtonText: '确认',
            cancelButtonText: '取消',
            inputType: 'password',
            inputPlaceholder: '请再次输入新密码'
          })

          if (newPassword !== confirmPassword) {
            ElMessage.error('两次输入的密码不一致')
            return
          }

          // TODO: 调用修改密码API
          // await updatePassword({ new_password: newPassword })

          ElMessage.warning('修改密码API尚未实现，请联系管理员')
          done()
        } catch (err) {
          // 用户取消了第二次输入
        }
      } else {
        done()
      }
    }
  }).catch(() => {})
}
</script>

<style scoped>
/* 选中状态的左侧小竖条装饰 */
.nav-item.active::before {
  content: '';
  position: absolute;
  left: -16px;
  top: 50%;
  transform: translateY(-50%);
  height: 20px;
  width: 4px;
  background-color: #4F46E5;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}
</style>
