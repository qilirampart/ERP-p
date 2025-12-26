<template>
  <div class="flex-1 flex flex-col min-h-0">
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
        <!-- 核心统计 - 2行3列紧凑网格 -->
        <div class="grid grid-cols-3 gap-3 mb-4" v-loading="loading">
          <div class="bento-card p-2">
            <div class="text-center">
              <p class="text-xs text-slate-500 mb-0.5">今日订单</p>
              <p class="text-xl font-bold text-indigo-600">{{ stats.today_orders_count }}</p>
            </div>
          </div>

          <div class="bento-card p-2">
            <div class="text-center">
              <p class="text-xs text-slate-500 mb-0.5">生产中</p>
              <p class="text-xl font-bold text-amber-600">{{ stats.production_in_progress }}</p>
            </div>
          </div>

          <div class="bento-card p-2">
            <div class="text-center">
              <p class="text-xs text-slate-500 mb-0.5">库存预警</p>
              <p class="text-xl font-bold text-red-600">{{ stats.low_stock_count }}</p>
            </div>
          </div>

          <div class="bento-card p-2">
            <div class="text-center">
              <p class="text-xs text-slate-500 mb-0.5">待生产</p>
              <p class="text-xl font-bold text-slate-600">{{ stats.production_pending }}</p>
            </div>
          </div>

          <div class="bento-card p-2">
            <div class="text-center">
              <p class="text-xs text-slate-500 mb-0.5">今日完成</p>
              <p class="text-xl font-bold text-emerald-600">{{ stats.production_completed_today }}</p>
            </div>
          </div>

          <div class="bento-card p-2">
            <div class="text-center">
              <p class="text-xs text-slate-500 mb-0.5">订单总数</p>
              <p class="text-xl font-bold text-blue-600">{{ stats.total_orders_count }}</p>
            </div>
          </div>
        </div>

        <!-- 财务数据 - 1行4列 -->
        <div class="grid grid-cols-4 gap-3 mb-4">
          <div class="bento-card p-2">
            <p class="text-xs text-slate-500 mb-0.5">今日订单额</p>
            <p class="text-base font-bold text-slate-800">{{ formatAmount(stats.today_orders_amount) }}</p>
          </div>

          <div class="bento-card p-2">
            <p class="text-xs text-slate-500 mb-0.5">本月收款</p>
            <p class="text-base font-bold text-emerald-600">{{ formatAmount(stats.month_payment_amount) }}</p>
          </div>

          <div class="bento-card p-2">
            <p class="text-xs text-slate-500 mb-0.5">本月订单额</p>
            <p class="text-base font-bold text-indigo-600">{{ formatAmount(stats.month_order_amount) }}</p>
          </div>

          <div class="bento-card p-2">
            <p class="text-xs text-slate-500 mb-0.5">应收账款</p>
            <p class="text-base font-bold text-orange-600">{{ formatAmount(stats.total_receivable) }}</p>
          </div>
        </div>

        <!-- 回款率 -->
        <div class="bento-card p-3 mb-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs text-slate-500 mb-1">本月回款率</p>
              <p class="text-2xl font-bold text-emerald-600">{{ stats.payment_rate }}%</p>
            </div>
            <div class="text-right text-xs text-slate-600">
              {{ formatAmount(stats.month_payment_amount) }} / {{ formatAmount(stats.month_order_amount) }}
            </div>
          </div>
        </div>

        <!-- 快速操作 -->
        <div class="bento-card">
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getDashboardStats } from '@/api/dashboard'
import { ElMessage } from 'element-plus'
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
  Check,
  TrendCharts
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 统计数据
const stats = ref({
  today_orders_count: 0,
  today_orders_amount: '0.00',
  total_orders_count: 0,
  production_in_progress: 0,
  production_pending: 0,
  production_completed_today: 0,
  low_stock_count: 0,
  total_materials_count: 0,
  month_payment_amount: '0.00',
  month_order_amount: '0.00',
  payment_rate: '0.00',
  total_receivable: '0.00'
})

// 加载状态
const loading = ref(false)

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await getDashboardStats()
    if (response.code === 200) {
      stats.value = response.data.stats
    }
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 格式化金额
const formatAmount = (amount) => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2
  }).format(amount)
}

// 组件挂载时加载数据
onMounted(() => {
  loadData()
})
</script>
