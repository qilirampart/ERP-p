<template>
  <div class="h-full overflow-auto bg-surface p-8">
    <!-- 头部 -->
    <header class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">仪表盘</h1>
        <p class="text-sm text-slate-500 mt-1">欢迎回来，{{ userStore.userInfo?.username }}</p>
      </div>
      <div class="flex space-x-3">
        <button
          @click="loadData"
          class="bg-white border border-slate-200 text-slate-600 px-4 py-2 rounded-lg text-sm hover:bg-slate-50 flex items-center"
        >
          <el-icon class="mr-2"><Refresh /></el-icon>
          刷新数据
        </button>
      </div>
    </header>

    <!-- 主要统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6" v-loading="loading">
      <!-- 今日订单 -->
      <div
        class="bg-white p-6 rounded-2xl border border-slate-200/60 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        @click="$router.push('/orders')"
      >
        <div class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">今日订单</div>
        <div class="text-3xl font-bold text-slate-800">{{ stats.today_orders_count }}</div>
        <div class="text-emerald-500 text-xs mt-2 flex items-center">
          <el-icon class="mr-1"><TrendCharts /></el-icon>
          +12% 较昨日
        </div>
      </div>

      <!-- 生产中 -->
      <div
        class="bg-white p-6 rounded-2xl border border-slate-200/60 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        @click="$router.push('/production')"
      >
        <div class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">生产中</div>
        <div class="text-3xl font-bold text-slate-800">{{ stats.production_in_progress }}</div>
        <div class="text-indigo-500 text-xs mt-2 flex items-center">
          {{ stats.production_pending }} 单待生产
        </div>
      </div>

      <!-- 库存预警 -->
      <div
        class="bg-white p-6 rounded-2xl border border-slate-200/60 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden cursor-pointer"
        @click="$router.push('/materials')"
      >
        <div class="absolute right-0 top-0 w-16 h-16 bg-red-50 rounded-bl-full -mr-2 -mt-2"></div>
        <div class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2 relative z-10">库存预警</div>
        <div class="text-3xl font-bold text-red-600 relative z-10">{{ warningMaterials.length }}</div>
        <div class="text-slate-400 text-xs mt-2 relative z-10">
          <span v-if="warningMaterials.length > 0">
            {{ warningMaterials[0]?.name }}
            <span v-if="warningMaterials[0]?.supplier">({{ warningMaterials[0]?.supplier }})</span>
          </span>
          <span v-else>库存充足</span>
        </div>
      </div>

      <!-- 今日营收 -->
      <div
        class="bg-white p-6 rounded-2xl border border-slate-200/60 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        @click="$router.push('/payments')"
      >
        <div class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">今日营收</div>
        <div class="text-3xl font-bold text-slate-800">{{ formatAmount(stats.today_orders_amount) }}</div>
      </div>
    </div>

    <!-- 财务概览 -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
      <!-- 本月收款 -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200/60 shadow-sm">
        <div class="text-slate-500 text-xs font-semibold mb-1">本月收款</div>
        <div class="text-xl font-bold text-emerald-600">{{ formatAmount(stats.month_payment_amount) }}</div>
      </div>

      <!-- 本月订单额 -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200/60 shadow-sm">
        <div class="text-slate-500 text-xs font-semibold mb-1">本月订单额</div>
        <div class="text-xl font-bold text-indigo-600">{{ formatAmount(stats.month_order_amount) }}</div>
      </div>

      <!-- 应收账款 -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200/60 shadow-sm">
        <div class="text-slate-500 text-xs font-semibold mb-1">应收账款</div>
        <div class="text-xl font-bold text-orange-600">{{ formatAmount(stats.total_receivable) }}</div>
      </div>

      <!-- 本月回款率 -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200/60 shadow-sm">
        <div class="text-slate-500 text-xs font-semibold mb-1">本月回款率</div>
        <div class="text-xl font-bold text-slate-800">{{ stats.payment_rate }}%</div>
      </div>
    </div>

    <!-- 生产概览 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <div class="bg-white p-4 rounded-2xl border border-slate-200/60 shadow-sm">
        <div class="flex items-center justify-between">
          <div class="text-slate-500 text-xs font-semibold mb-1">待生产</div>
          <el-icon class="text-amber-500" :size="20"><Clock /></el-icon>
        </div>
        <div class="text-2xl font-bold text-slate-800">{{ stats.production_pending }}</div>
      </div>

      <div class="bg-white p-4 rounded-2xl border border-slate-200/60 shadow-sm">
        <div class="flex items-center justify-between">
          <div class="text-slate-500 text-xs font-semibold mb-1">今日完成</div>
          <el-icon class="text-emerald-500" :size="20"><Check /></el-icon>
        </div>
        <div class="text-2xl font-bold text-emerald-600">{{ stats.production_completed_today }}</div>
      </div>

      <div class="bg-white p-4 rounded-2xl border border-slate-200/60 shadow-sm">
        <div class="flex items-center justify-between">
          <div class="text-slate-500 text-xs font-semibold mb-1">订单总数</div>
          <el-icon class="text-indigo-500" :size="20"><DocumentAdd /></el-icon>
        </div>
        <div class="text-2xl font-bold text-slate-800">{{ stats.total_orders_count }}</div>
      </div>
    </div>

    <!-- 销售趋势图表 -->
    <div class="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-lg font-bold text-slate-800">销售趋势</h3>
          <p class="text-xs text-slate-400 mt-1">近 7 天订单金额与数量</p>
        </div>
        <div class="flex space-x-2">
          <button
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-lg transition-colors',
              chartPeriod === 'week' ? 'bg-indigo-50 text-indigo-600' : 'text-slate-500 hover:bg-slate-50'
            ]"
            @click="chartPeriod = 'week'"
          >
            近 7 天
          </button>
          <button
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-lg transition-colors',
              chartPeriod === 'month' ? 'bg-indigo-50 text-indigo-600' : 'text-slate-500 hover:bg-slate-50'
            ]"
            @click="chartPeriod = 'month'"
          >
            近 30 天
          </button>
        </div>
      </div>
      <v-chart class="chart" :option="chartOption" :autoresize="true" style="height: 320px;" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getDashboardStats } from '@/api/dashboard'
import { getWarningMaterials } from '@/api/material'
import { getSalesPaymentTrend } from '@/api/report'
import { ElMessage, ElNotification } from 'element-plus'
import {
  DocumentAdd,
  Refresh,
  DataAnalysis,
  Clock,
  Check,
  TrendCharts
} from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

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

// 预警物料列表
const warningMaterials = ref([])

// 销售趋势数据
const trendData = ref({
  daily_data: []
})

// 加载状态
const loading = ref(false)

// 图表周期选择
const chartPeriod = ref('week')

// 图表配置
const chartOption = computed(() => {
  const days = chartPeriod.value === 'week' ? 7 : 30
  const dailyData = trendData.value.daily_data || []

  // 取最近 N 天的数据
  const recentData = dailyData.slice(-days)

  // 提取日期和数据
  const dates = recentData.map(item => {
    const date = new Date(item.date)
    return `${date.getMonth() + 1}/${date.getDate()}`
  })
  const amounts = recentData.map(item => parseFloat(item.order_amount) || 0)
  const counts = recentData.map(item => item.order_count || 0)

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      textStyle: {
        color: '#334155',
        fontSize: 12
      },
      padding: [12, 16],
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#94a3b8'
        }
      }
    },
    legend: {
      data: ['订单金额', '订单数量'],
      top: 0,
      right: 0,
      textStyle: {
        color: '#64748b',
        fontSize: 12
      },
      itemWidth: 12,
      itemHeight: 12
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: dates,
        axisPointer: {
          type: 'shadow'
        },
        axisLine: {
          lineStyle: {
            color: '#e2e8f0'
          }
        },
        axisLabel: {
          color: '#94a3b8',
          fontSize: 11
        }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '金额（¥）',
        position: 'left',
        nameTextStyle: {
          color: '#64748b',
          fontSize: 11
        },
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          color: '#94a3b8',
          fontSize: 11,
          formatter: (value) => {
            return value >= 1000 ? `${(value / 1000).toFixed(1)}k` : value
          }
        },
        splitLine: {
          lineStyle: {
            color: '#f1f5f9',
            type: 'dashed'
          }
        }
      },
      {
        type: 'value',
        name: '订单数',
        position: 'right',
        nameTextStyle: {
          color: '#64748b',
          fontSize: 11
        },
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          color: '#94a3b8',
          fontSize: 11
        },
        splitLine: {
          show: false
        }
      }
    ],
    series: [
      {
        name: '订单金额',
        type: 'line',
        smooth: true,
        data: amounts,
        yAxisIndex: 0,
        itemStyle: {
          color: '#4f46e5'
        },
        lineStyle: {
          width: 3,
          color: '#4f46e5'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: 'rgba(79, 70, 229, 0.15)'
              },
              {
                offset: 1,
                color: 'rgba(79, 70, 229, 0.01)'
              }
            ]
          }
        }
      },
      {
        name: '订单数量',
        type: 'bar',
        data: counts,
        yAxisIndex: 1,
        barWidth: '40%',
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: '#a5b4fc'
              },
              {
                offset: 1,
                color: '#c7d2fe'
              }
            ]
          },
          borderRadius: [4, 4, 0, 0]
        }
      }
    ]
  }
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 并行加载统计数据、预警物料和销售趋势
    const [statsResponse, warningsResponse, trendResponse] = await Promise.all([
      getDashboardStats(),
      getWarningMaterials(),
      getSalesPaymentTrend(30) // 获取近30天数据
    ])

    if (statsResponse.code === 200) {
      stats.value = statsResponse.data.stats
    }

    if (trendResponse.code === 200) {
      trendData.value = trendResponse.data
    }

    if (warningsResponse.code === 200) {
      const warnings = warningsResponse.data || []
      warningMaterials.value = warnings

      // 显示预警通知
      if (warnings.length > 0) {
        const criticalCount = warnings.filter(m => m.stock_status === 'CRITICAL').length
        const warningCount = warnings.filter(m => m.stock_status === 'WARNING').length

        let message = ''
        if (criticalCount > 0) {
          message = `严重预警：${criticalCount}种物料库存严重不足！`
          ElNotification({
            title: '库存严重预警',
            message: message + `\n${warnings.filter(m => m.stock_status === 'CRITICAL').map(m => m.name).join('、')}`,
            type: 'error',
            duration: 0, // 不自动关闭
            position: 'top-right'
          })
        } else if (warningCount > 0) {
          message = `库存预警：${warningCount}种物料库存偏低`
          ElNotification({
            title: '库存预警提示',
            message: message + `\n${warnings.map(m => m.name).join('、')}`,
            type: 'warning',
            duration: 5000,
            position: 'top-right'
          })
        }
      }
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
  // 移除货币符号，只显示数字
  const num = parseFloat(amount) || 0
  return `¥ ${num.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
}

// 组件挂载时加载数据
onMounted(() => {
  loadData()
})
</script>
