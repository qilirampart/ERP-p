<template>
  <div class="reports-container">
    <!-- 财务概览卡片 -->
    <div class="overview-grid">
      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">订单总额</div>
            <div class="stat-value">¥{{ formatCurrency(overview.total_order_amount) }}</div>
            <div class="stat-meta">共{{ overview.total_orders }}笔订单</div>
          </div>
          <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <el-icon :size="32" color="#fff"><DocumentAdd /></el-icon>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">收款总额</div>
            <div class="stat-value">¥{{ formatCurrency(overview.total_payment_amount) }}</div>
            <div class="stat-meta">共{{ overview.total_payments }}笔收款</div>
          </div>
          <div class="stat-icon" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
            <el-icon :size="32" color="#fff"><Money /></el-icon>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">回款率</div>
            <div class="stat-value">{{ overview.payment_rate }}%</div>
            <div class="stat-meta">应收¥{{ formatCurrency(overview.total_receivable) }}</div>
          </div>
          <div class="stat-icon" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
            <el-icon :size="32" color="#fff"><TrendCharts /></el-icon>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">本月收款</div>
            <div class="stat-value">¥{{ formatCurrency(overview.month_payment_amount) }}</div>
            <div class="stat-meta">{{ overview.month_payment_count }}笔</div>
          </div>
          <div class="stat-icon" style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);">
            <el-icon :size="32" color="#fff"><Calendar /></el-icon>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Tab页 -->
    <el-card shadow="never" class="mt-4">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 销售收款趋势 -->
        <el-tab-pane label="📈 销售收款趋势" name="trend">
          <div class="tab-content">
            <div class="mb-4 flex items-center justify-between">
              <el-radio-group v-model="trendDays" @change="loadTrendData">
                <el-radio-button :label="7">近7天</el-radio-button>
                <el-radio-button :label="15">近15天</el-radio-button>
                <el-radio-button :label="30">近30天</el-radio-button>
              </el-radio-group>

              <div class="text-sm text-slate-600">
                <span class="mr-4">订单总额: <strong class="text-indigo-600">¥{{ formatCurrency(trendData.total_order_amount) }}</strong></span>
                <span>收款总额: <strong class="text-emerald-600">¥{{ formatCurrency(trendData.total_payment_amount) }}</strong></span>
              </div>
            </div>

            <div v-loading="trendLoading" class="chart-container">
              <v-chart :option="trendChartOption" autoresize />
            </div>
          </div>
        </el-tab-pane>

        <!-- 账龄分析 -->
        <el-tab-pane label="📊 账龄分析" name="aging">
          <div class="tab-content">
            <div class="mb-4">
              <el-alert type="info" :closable="false">
                <template #title>
                  <span class="font-bold">总应收金额: ¥{{ formatCurrency(agingData.total_receivable) }}</span>
                </template>
              </el-alert>
            </div>

            <el-row :gutter="20">
              <el-col :span="12">
                <div v-loading="agingLoading" class="chart-container">
                  <v-chart :option="agingPieOption" autoresize />
                </div>
              </el-col>
              <el-col :span="12">
                <div class="aging-list">
                  <div
                    v-for="bracket in agingData.aging_brackets"
                    :key="bracket.bracket_name"
                    class="aging-item"
                  >
                    <div class="aging-item-header">
                      <span class="aging-item-name">{{ bracket.bracket_name }}</span>
                      <span class="aging-item-amount">¥{{ formatCurrency(bracket.amount) }}</span>
                    </div>
                    <div class="aging-item-meta">
                      <span>{{ bracket.order_count }}笔订单</span>
                      <span>占比{{ bracket.percentage }}%</span>
                    </div>
                    <el-progress
                      :percentage="Number(bracket.percentage)"
                      :show-text="false"
                      :color="getAgingColor(bracket.bracket_name)"
                    />
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <!-- 日报月报 -->
        <el-tab-pane label="📅 收款报表" name="daily">
          <div class="tab-content">
            <el-radio-group v-model="reportType" class="mb-4" @change="handleReportTypeChange">
              <el-radio-button label="daily">日报</el-radio-button>
              <el-radio-button label="monthly">月报</el-radio-button>
            </el-radio-group>

            <!-- 日报 -->
            <div v-if="reportType === 'daily'">
              <div class="mb-4 flex items-center gap-4">
                <el-date-picker
                  v-model="dailyDateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  @change="loadDailyReport"
                />
                <el-button type="primary" @click="loadDailyReport">查询</el-button>
              </div>

              <el-table :data="dailyReports" border v-loading="dailyLoading">
                <el-table-column prop="date" label="日期" width="120" />
                <el-table-column prop="payment_count" label="收款笔数" width="100" align="center" />
                <el-table-column prop="total_amount" label="总金额" width="120" align="right">
                  <template #default="{ row }">
                    <span class="font-bold text-emerald-600">¥{{ formatCurrency(row.total_amount) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="cash_amount" label="现金" width="100" align="right">
                  <template #default="{ row }">
                    {{ formatCurrency(row.cash_amount) }}
                  </template>
                </el-table-column>
                <el-table-column prop="bank_transfer_amount" label="银行转账" width="110" align="right">
                  <template #default="{ row }">
                    {{ formatCurrency(row.bank_transfer_amount) }}
                  </template>
                </el-table-column>
                <el-table-column prop="alipay_amount" label="支付宝" width="100" align="right">
                  <template #default="{ row }">
                    {{ formatCurrency(row.alipay_amount) }}
                  </template>
                </el-table-column>
                <el-table-column prop="wechat_amount" label="微信" width="100" align="right">
                  <template #default="{ row }">
                    {{ formatCurrency(row.wechat_amount) }}
                  </template>
                </el-table-column>
                <el-table-column prop="check_amount" label="支票" width="100" align="right">
                  <template #default="{ row }">
                    {{ formatCurrency(row.check_amount) }}
                  </template>
                </el-table-column>
                <el-table-column prop="other_amount" label="其他" width="100" align="right">
                  <template #default="{ row }">
                    {{ formatCurrency(row.other_amount) }}
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- 月报 -->
            <div v-else>
              <div class="mb-4 flex items-center gap-4">
                <el-date-picker
                  v-model="monthlyDate"
                  type="month"
                  placeholder="选择月份"
                  format="YYYY年MM月"
                  value-format="YYYY-MM"
                  @change="loadMonthlyReport"
                />
                <el-button type="primary" @click="loadMonthlyReport">查询</el-button>
              </div>

              <div v-if="monthlyReport" v-loading="monthlyLoading">
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="年月" :span="2">
                    {{ monthlyReport.year }}年{{ monthlyReport.month }}月
                  </el-descriptions-item>
                  <el-descriptions-item label="收款笔数">
                    {{ monthlyReport.payment_count }}笔
                  </el-descriptions-item>
                  <el-descriptions-item label="收款总额">
                    <span class="text-lg font-bold text-emerald-600">
                      ¥{{ formatCurrency(monthlyReport.total_amount) }}
                    </span>
                  </el-descriptions-item>
                  <el-descriptions-item label="平均金额">
                    ¥{{ formatCurrency(monthlyReport.average_amount) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="环比增长率">
                    <el-tag v-if="monthlyReport.growth_rate !== null" :type="Number(monthlyReport.growth_rate) >= 0 ? 'success' : 'danger'">
                      {{ monthlyReport.growth_rate }}%
                    </el-tag>
                    <span v-else>-</span>
                  </el-descriptions-item>
                </el-descriptions>

                <div class="mt-4">
                  <h3 class="text-sm font-bold mb-2">收款方式分布</h3>
                  <div class="flex flex-wrap gap-3">
                    <el-tag
                      v-for="(amount, method) in monthlyReport.payment_methods"
                      :key="method"
                      size="large"
                    >
                      {{ getPaymentMethodLabel(method) }}: ¥{{ formatCurrency(amount) }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { ElMessage } from 'element-plus'
import {
  DocumentAdd, Money, TrendCharts, Calendar
} from '@element-plus/icons-vue'
import {
  getFinancialOverview,
  getDailyPaymentReport,
  getMonthlyPaymentReport,
  getSalesPaymentTrend,
  getReceivablesAging
} from '@/api/report'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// 财务概览
const overview = reactive({
  total_orders: 0,
  total_order_amount: 0,
  completed_orders: 0,
  total_payments: 0,
  total_payment_amount: 0,
  payment_rate: 0,
  total_receivable: 0,
  overdue_amount: 0,
  overdue_count: 0,
  month_order_amount: 0,
  month_payment_amount: 0,
  month_order_count: 0,
  month_payment_count: 0
})

// Tab切换
const activeTab = ref('trend')

// 销售收款趋势
const trendDays = ref(7)
const trendLoading = ref(false)
const trendData = reactive({
  start_date: '',
  end_date: '',
  total_order_amount: 0,
  total_payment_amount: 0,
  total_order_count: 0,
  total_payment_count: 0,
  daily_data: []
})

// 账龄分析
const agingLoading = ref(false)
const agingData = reactive({
  total_receivable: 0,
  aging_brackets: [],
  bracket_0_7: null,
  bracket_8_30: null,
  bracket_31_60: null,
  bracket_61_90: null,
  bracket_90_plus: null
})

// 日报月报
const reportType = ref('daily')
const dailyDateRange = ref([])
const dailyReports = ref([])
const dailyLoading = ref(false)
const monthlyDate = ref('')
const monthlyReport = ref(null)
const monthlyLoading = ref(false)

// 加载财务概览
const loadOverview = async () => {
  try {
    const response = await getFinancialOverview()
    if (response.code === 200) {
      Object.assign(overview, response.data)
    }
  } catch (error) {
    console.error('加载财务概览失败:', error)
  }
}

// 加载趋势数据
const loadTrendData = async () => {
  trendLoading.value = true
  try {
    const response = await getSalesPaymentTrend(trendDays.value)
    if (response.code === 200) {
      Object.assign(trendData, response.data)
    }
  } catch (error) {
    ElMessage.error('加载趋势数据失败')
  } finally {
    trendLoading.value = false
  }
}

// 加载账龄数据
const loadAgingData = async () => {
  agingLoading.value = true
  try {
    const response = await getReceivablesAging()
    if (response.code === 200) {
      Object.assign(agingData, response.data)
    }
  } catch (error) {
    ElMessage.error('加载账龄数据失败')
  } finally {
    agingLoading.value = false
  }
}

// 加载日报
const loadDailyReport = async () => {
  if (!dailyDateRange.value || dailyDateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  dailyLoading.value = true
  try {
    const [startDate, endDate] = dailyDateRange.value
    const response = await getDailyPaymentReport(startDate, endDate)
    if (response.code === 200) {
      dailyReports.value = response.data
    }
  } catch (error) {
    ElMessage.error('加载日报失败')
  } finally {
    dailyLoading.value = false
  }
}

// 加载月报
const loadMonthlyReport = async () => {
  if (!monthlyDate.value) {
    ElMessage.warning('请选择月份')
    return
  }

  monthlyLoading.value = true
  try {
    const [year, month] = monthlyDate.value.split('-')
    const response = await getMonthlyPaymentReport(Number(year), Number(month))
    if (response.code === 200) {
      monthlyReport.value = response.data
    }
  } catch (error) {
    ElMessage.error('加载月报失败')
  } finally {
    monthlyLoading.value = false
  }
}

// 趋势图表配置
const trendChartOption = computed(() => ({
  title: {
    text: '销售收款趋势对比',
    left: 'center',
    top: 10
  },
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['订单金额', '收款金额'],
    top: 35
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: trendData.daily_data.map(d => d.date)
  },
  yAxis: {
    type: 'value',
    name: '金额（元）',
    axisLabel: {
      formatter: (value) => `¥${value}`
    }
  },
  series: [
    {
      name: '订单金额',
      type: 'line',
      data: trendData.daily_data.map(d => Number(d.order_amount)),
      smooth: true,
      itemStyle: { color: '#667eea' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
          ]
        }
      }
    },
    {
      name: '收款金额',
      type: 'line',
      data: trendData.daily_data.map(d => Number(d.payment_amount)),
      smooth: true,
      itemStyle: { color: '#10b981' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0.05)' }
          ]
        }
      }
    }
  ]
}))

// 账龄饼图配置
const agingPieOption = computed(() => ({
  title: {
    text: '应收账款账龄分布',
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{b}: ¥{c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center'
  },
  series: [
    {
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      data: agingData.aging_brackets.map((bracket, index) => ({
        value: Number(bracket.amount),
        name: bracket.bracket_name,
        itemStyle: {
          color: getAgingColor(bracket.bracket_name)
        }
      }))
    }
  ]
}))

// Tab切换处理
const handleTabChange = (name) => {
  if (name === 'trend' && trendData.daily_data.length === 0) {
    loadTrendData()
  } else if (name === 'aging' && agingData.aging_brackets.length === 0) {
    loadAgingData()
  }
}

// 报表类型切换
const handleReportTypeChange = () => {
  if (reportType.value === 'daily') {
    // 默认查询最近7天
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - 6)
    dailyDateRange.value = [
      start.toISOString().split('T')[0],
      end.toISOString().split('T')[0]
    ]
    loadDailyReport()
  } else {
    // 默认查询当前月
    const now = new Date()
    monthlyDate.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
    loadMonthlyReport()
  }
}

// 格式化金额
const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return Number(amount).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// 获取账龄颜色
const getAgingColor = (name) => {
  const colorMap = {
    '0-7天': '#10b981',
    '8-30天': '#3b82f6',
    '31-60天': '#f59e0b',
    '61-90天': '#ef4444',
    '90天以上': '#991b1b'
  }
  return colorMap[name] || '#6b7280'
}

// 获取收款方式标签
const getPaymentMethodLabel = (method) => {
  const labelMap = {
    'CASH': '现金',
    'BANK_TRANSFER': '银行转账',
    'ALIPAY': '支付宝',
    'WECHAT': '微信',
    'CHECK': '支票',
    'OTHER': '其他'
  }
  return labelMap[method] || method
}

// 初始化
onMounted(() => {
  loadOverview()
  loadTrendData()
})
</script>

<style scoped>
.reports-container {
  padding: 20px;
}

/* 概览卡片 */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 12px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 4px;
}

.stat-meta {
  font-size: 12px;
  color: #9ca3af;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Tab内容 */
.tab-content {
  padding: 20px 0;
}

.chart-container {
  height: 400px;
  width: 100%;
}

/* 账龄列表 */
.aging-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.aging-item {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.aging-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.aging-item-name {
  font-weight: 600;
  color: #374151;
}

.aging-item-amount {
  font-weight: 700;
  font-size: 18px;
  color: #10b981;
}

.aging-item-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
}

/* 工具类 */
.mt-4 {
  margin-top: 1rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mr-4 {
  margin-right: 1rem;
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.gap-3 {
  gap: 0.75rem;
}

.gap-4 {
  gap: 1rem;
}

.flex-wrap {
  flex-wrap: wrap;
}

.text-sm {
  font-size: 0.875rem;
}

.text-lg {
  font-size: 1.125rem;
}

.font-bold {
  font-weight: 700;
}

.text-slate-600 {
  color: #475569;
}

.text-indigo-600 {
  color: #4f46e5;
}

.text-emerald-600 {
  color: #10b981;
}
</style>
