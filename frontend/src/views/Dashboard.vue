<template>
  <div class="flex-1 flex flex-col">
    <!-- 头部 -->
    <header class="h-20 flex items-center justify-between px-8 lg:px-12 flex-shrink-0">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">仪表盘</h1>
        <p class="text-sm text-slate-500 mt-1">欢迎回来，{{ userStore.userInfo?.username }}</p>
      </div>
      <div class="flex items-center space-x-4">
        <el-button :icon="Refresh" circle @click="loadData" />
      </div>
    </header>

    <!-- 内容区 -->
    <div class="flex-1 overflow-y-auto px-8 lg:px-12 pb-12">
      <div class="max-w-7xl mx-auto">
        <!-- 统计卡片 -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <div class="bento-card">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-slate-500 uppercase">今日订单</span>
              <el-icon class="text-indigo-500"><DocumentAdd /></el-icon>
            </div>
            <p class="text-3xl font-bold text-slate-800">{{ stats.todayOrders }}</p>
            <p class="text-sm text-slate-500 mt-2">
              <span class="text-green-500">+12%</span> 较昨日
            </p>
          </div>

          <div class="bento-card">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-slate-500 uppercase">生产中</span>
              <el-icon class="text-amber-500"><Setting /></el-icon>
            </div>
            <p class="text-3xl font-bold text-slate-800">{{ stats.production }}</p>
            <p class="text-sm text-slate-500 mt-2">5个工单</p>
          </div>

          <div class="bento-card">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-slate-500 uppercase">库存预警</span>
              <el-icon class="text-red-500"><Warning /></el-icon>
            </div>
            <p class="text-3xl font-bold text-slate-800">{{ stats.lowStock }}</p>
            <p class="text-sm text-slate-500 mt-2">物料低于阈值</p>
          </div>

          <div class="bento-card">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-slate-500 uppercase">本月营收</span>
              <el-icon class="text-emerald-500"><Money /></el-icon>
            </div>
            <p class="text-3xl font-bold text-slate-800 font-numeric">¥{{ stats.revenue }}</p>
            <p class="text-sm text-slate-500 mt-2">
              <span class="text-green-500">+28%</span> 较上月
            </p>
          </div>
        </div>

        <!-- 快速操作 -->
        <div class="bento-card mb-6">
          <h3 class="text-lg font-bold text-slate-800 mb-4">快速操作</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button
              class="flex flex-col items-center p-4 rounded-xl hover:bg-slate-50 transition-colors"
              @click="$router.push('/orders')"
            >
              <div class="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600 mb-2">
                <el-icon :size="24"><DocumentAdd /></el-icon>
              </div>
              <span class="text-sm font-medium text-slate-700">新建订单</span>
            </button>

            <button
              class="flex flex-col items-center p-4 rounded-xl hover:bg-slate-50 transition-colors"
              @click="$router.push('/materials')"
            >
              <div class="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600 mb-2">
                <el-icon :size="24"><Box /></el-icon>
              </div>
              <span class="text-sm font-medium text-slate-700">库存入库</span>
            </button>

            <button
              class="flex flex-col items-center p-4 rounded-xl hover:bg-slate-50 transition-colors"
            >
              <div class="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600 mb-2">
                <el-icon :size="24"><Printer /></el-icon>
              </div>
              <span class="text-sm font-medium text-slate-700">打印工单</span>
            </button>

            <button
              class="flex flex-col items-center p-4 rounded-xl hover:bg-slate-50 transition-colors"
            >
              <div class="w-12 h-12 rounded-xl bg-rose-50 flex items-center justify-center text-rose-600 mb-2">
                <el-icon :size="24"><DataAnalysis /></el-icon>
              </div>
              <span class="text-sm font-medium text-slate-700">数据报表</span>
            </button>
          </div>
        </div>

        <!-- 待办事项 -->
        <div class="bento-card">
          <h3 class="text-lg font-bold text-slate-800 mb-4">待处理事项</h3>
          <div class="space-y-3">
            <div class="flex items-center p-3 rounded-lg hover:bg-slate-50 cursor-pointer">
              <el-icon class="text-indigo-500 mr-3"><Clock /></el-icon>
              <div class="flex-1">
                <p class="text-sm font-medium text-slate-700">订单 SO20251207001 待确认</p>
                <p class="text-xs text-slate-400">2小时前</p>
              </div>
              <el-tag size="small" type="warning">待处理</el-tag>
            </div>

            <div class="flex items-center p-3 rounded-lg hover:bg-slate-50 cursor-pointer">
              <el-icon class="text-amber-500 mr-3"><Warning /></el-icon>
              <div class="flex-1">
                <p class="text-sm font-medium text-slate-700">双铜纸 157g 库存不足</p>
                <p class="text-xs text-slate-400">1天前</p>
              </div>
              <el-tag size="small" type="danger">紧急</el-tag>
            </div>

            <div class="flex items-center p-3 rounded-lg hover:bg-slate-50 cursor-pointer">
              <el-icon class="text-emerald-500 mr-3"><Check /></el-icon>
              <div class="flex-1">
                <p class="text-sm font-medium text-slate-700">生产工单 PRD001 已完工</p>
                <p class="text-xs text-slate-400">3小时前</p>
              </div>
              <el-tag size="small" type="success">已完成</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  DocumentAdd,
  Setting,
  Warning,
  Money,
  Refresh,
  Box,
  Printer,
  DataAnalysis,
  Clock,
  Check
} from '@element-plus/icons-vue'

const userStore = useUserStore()

const stats = ref({
  todayOrders: 12,
  production: 8,
  lowStock: 3,
  revenue: '125,600'
})

const loadData = () => {
  // TODO: 加载实际数据
  console.log('刷新数据')
}
</script>
