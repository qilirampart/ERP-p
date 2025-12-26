<template>
  <div class="payments-container">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card shadow="hover" class="stat-card stat-card-total">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">总收款金额</div>
            <div class="stat-value">¥{{ formatCurrency(statistics.total_payment_amount) }}</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="40" color="#10b981"><Money /></el-icon>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stat-card stat-card-today">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">今日收款</div>
            <div class="stat-value">¥{{ formatCurrency(statistics.today_payment_amount) }}</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="40" color="#f59e0b"><Calendar /></el-icon>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stat-card stat-card-count">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">收款记录数</div>
            <div class="stat-value">{{ statistics.total_payment_count }}</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="40" color="#6366f1"><Document /></el-icon>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stat-card stat-card-methods">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">收款方式</div>
            <div class="stat-methods">
              <el-tag
                v-for="(amount, method) in statistics.payment_method_stats"
                :key="method"
                size="small"
                class="method-tag"
              >
                {{ getPaymentMethodLabel(method) }}: ¥{{ formatCurrency(amount) }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 搜索和操作栏 -->
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="订单号">
          <el-input
            v-model="searchForm.order_no"
            placeholder="输入订单号"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>

        <el-form-item label="收款方式">
          <el-select
            v-model="searchForm.payment_method"
            placeholder="选择收款方式"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option
              v-for="method in paymentMethods"
              :key="method.value"
              :label="method.label"
              :value="method.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="收款状态">
          <el-select
            v-model="searchForm.status"
            placeholder="选择状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="已确认" value="CONFIRMED" />
            <el-option label="待确认" value="PENDING" />
            <el-option label="已取消" value="CANCELLED" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 收款记录列表 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">收款记录</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            登记收款
          </el-button>
        </div>
      </template>

      <el-table
        :data="payments"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="payment_no" label="收款单号" width="160" fixed>
          <template #default="{ row }">
            <span class="font-mono font-bold text-indigo-600">{{ row.payment_no }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="order_no" label="订单号" width="160">
          <template #default="{ row }">
            <span class="font-mono">{{ row.order_no }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="customer_name" label="客户名称" width="150" />

        <el-table-column prop="payment_amount" label="收款金额" width="120" align="right">
          <template #default="{ row }">
            <span class="font-bold text-emerald-600">¥{{ formatCurrency(row.payment_amount) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="payment_method" label="收款方式" width="110">
          <template #default="{ row }">
            <el-tag :type="getPaymentMethodType(row.payment_method)" size="small">
              {{ getPaymentMethodLabel(row.payment_method) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="payment_date" label="收款日期" width="160">
          <template #default="{ row }">
            {{ formatDate(row.payment_date) }}
          </template>
        </el-table-column>

        <el-table-column prop="received_by" label="收款人" width="100" />

        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="voucher_no" label="凭证号" width="140" show-overflow-tooltip />

        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="showDetail(row)"
            >
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button
              v-if="row.status === 'CONFIRMED'"
              type="primary"
              size="small"
              link
              @click="handlePrint(row)"
            >
              <el-icon><Printer /></el-icon>
              打印凭证
            </el-button>
            <el-button
              v-if="row.status === 'CONFIRMED'"
              type="danger"
              size="small"
              link
              @click="handleCancel(row)"
            >
              <el-icon><CloseBold /></el-icon>
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadPayments"
          @current-change="loadPayments"
        />
      </div>
    </el-card>

    <!-- 创建收款对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="登记收款"
      width="600px"
      @close="resetCreateForm"
    >
      <el-form
        :model="createForm"
        :rules="createRules"
        ref="createFormRef"
        label-width="100px"
      >
        <el-form-item label="选择订单" prop="order_id">
          <el-select
            v-model="createForm.order_id"
            placeholder="请选择订单"
            filterable
            @change="handleOrderChange"
            class="w-full"
          >
            <el-option
              v-for="order in availableOrders"
              :key="order.id"
              :label="`${order.order_no} - ${order.customer_name} (¥${order.total_amount})`"
              :value="order.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="订单信息" v-if="selectedOrderSummary">
          <div class="w-full p-3 bg-slate-50 rounded">
            <div class="flex justify-between mb-2">
              <span class="text-sm text-slate-600">订单总额：</span>
              <span class="font-bold">¥{{ formatCurrency(selectedOrderSummary.total_amount) }}</span>
            </div>
            <div class="flex justify-between mb-2">
              <span class="text-sm text-slate-600">已收款：</span>
              <span class="font-bold text-emerald-600">¥{{ formatCurrency(selectedOrderSummary.paid_amount) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-slate-600">未收款：</span>
              <span class="font-bold text-red-600">¥{{ formatCurrency(selectedOrderSummary.unpaid_amount) }}</span>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="收款金额" prop="payment_amount">
          <el-input-number
            v-model="createForm.payment_amount"
            :min="0.01"
            :max="selectedOrderSummary ? Number(selectedOrderSummary.unpaid_amount) : 999999"
            :precision="2"
            class="w-full"
          />
        </el-form-item>

        <el-form-item label="收款方式" prop="payment_method">
          <el-select v-model="createForm.payment_method" class="w-full">
            <el-option
              v-for="method in paymentMethods"
              :key="method.value"
              :label="method.label"
              :value="method.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="收款日期" prop="payment_date">
          <el-date-picker
            v-model="createForm.payment_date"
            type="datetime"
            placeholder="选择日期时间"
            class="w-full"
            format="YYYY-MM-DD HH:mm"
          />
        </el-form-item>

        <el-form-item label="收款人" prop="received_by">
          <el-input v-model="createForm.received_by" placeholder="请输入收款人" />
        </el-form-item>

        <el-form-item label="凭证号" prop="voucher_no">
          <el-input v-model="createForm.voucher_no" placeholder="银行流水号/支付订单号等" />
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="createForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="submitting">
          确认收款
        </el-button>
      </template>
    </el-dialog>

    <!-- 收款详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="收款详情"
      width="600px"
    >
      <div v-if="currentPayment" class="payment-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="收款单号" :span="2">
            <span class="font-mono font-bold text-indigo-600">{{ currentPayment.payment_no }}</span>
          </el-descriptions-item>

          <el-descriptions-item label="订单号" :span="2">
            <span class="font-mono">{{ currentPayment.order_no }}</span>
          </el-descriptions-item>

          <el-descriptions-item label="客户名称" :span="2">
            {{ currentPayment.customer_name }}
          </el-descriptions-item>

          <el-descriptions-item label="收款金额" :span="2">
            <span class="text-xl font-bold text-emerald-600">
              ¥{{ formatCurrency(currentPayment.payment_amount) }}
            </span>
          </el-descriptions-item>

          <el-descriptions-item label="收款方式">
            <el-tag :type="getPaymentMethodType(currentPayment.payment_method)">
              {{ getPaymentMethodLabel(currentPayment.payment_method) }}
            </el-tag>
          </el-descriptions-item>

          <el-descriptions-item label="收款状态">
            <el-tag :type="getStatusType(currentPayment.status)">
              {{ getStatusLabel(currentPayment.status) }}
            </el-tag>
          </el-descriptions-item>

          <el-descriptions-item label="收款日期" :span="2">
            {{ formatDate(currentPayment.payment_date) }}
          </el-descriptions-item>

          <el-descriptions-item label="收款人">
            {{ currentPayment.received_by }}
          </el-descriptions-item>

          <el-descriptions-item label="凭证号">
            {{ currentPayment.voucher_no || '-' }}
          </el-descriptions-item>

          <el-descriptions-item label="备注" :span="2">
            <div class="whitespace-pre-wrap">{{ currentPayment.remark || '-' }}</div>
          </el-descriptions-item>

          <el-descriptions-item label="创建时间" :span="2">
            {{ formatDate(currentPayment.created_at) }}
          </el-descriptions-item>

          <el-descriptions-item label="更新时间" :span="2">
            {{ formatDate(currentPayment.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Money, Calendar, Document, Search, Refresh, Plus,
  View, CloseBold, Printer
} from '@element-plus/icons-vue'
import {
  getPaymentList,
  getPaymentDetail,
  createPayment,
  cancelPayment,
  getPaymentStatistics,
  getOrderPaymentSummary
} from '@/api/payment'
import { getOrderList } from '@/api/order'
import { downloadPaymentReceiptPDF, downloadFile } from '@/api/print'

// 统计数据
const statistics = reactive({
  total_payment_count: 0,
  total_payment_amount: 0,
  today_payment_amount: 0,
  payment_method_stats: {}
})

// 搜索表单
const searchForm = reactive({
  order_no: '',
  payment_method: '',
  status: ''
})

// 收款方式选项
const paymentMethods = [
  { label: '现金', value: 'CASH' },
  { label: '银行转账', value: 'BANK_TRANSFER' },
  { label: '支付宝', value: 'ALIPAY' },
  { label: '微信', value: 'WECHAT' },
  { label: '支票', value: 'CHECK' },
  { label: '其他', value: 'OTHER' }
]

// 收款列表
const payments = ref([])
const loading = ref(false)
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 创建收款
const createDialogVisible = ref(false)
const createFormRef = ref(null)
const createForm = reactive({
  order_id: null,
  payment_amount: 0,
  payment_method: 'BANK_TRANSFER',
  payment_date: new Date(),
  received_by: '',
  voucher_no: '',
  remark: ''
})

const createRules = {
  order_id: [{ required: true, message: '请选择订单', trigger: 'change' }],
  payment_amount: [{ required: true, message: '请输入收款金额', trigger: 'blur' }],
  payment_method: [{ required: true, message: '请选择收款方式', trigger: 'change' }],
  payment_date: [{ required: true, message: '请选择收款日期', trigger: 'change' }],
  received_by: [{ required: true, message: '请输入收款人', trigger: 'blur' }]
}

const submitting = ref(false)
const availableOrders = ref([])
const selectedOrderSummary = ref(null)

// 收款详情
const detailDialogVisible = ref(false)
const currentPayment = ref(null)

// 加载统计数据
const loadStatistics = async () => {
  try {
    const response = await getPaymentStatistics()
    if (response.code === 200) {
      Object.assign(statistics, response.data)
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 加载收款列表
const loadPayments = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      status: searchForm.status || undefined
    }

    const response = await getPaymentList(params)
    if (response.code === 200) {
      let data = response.data

      // 如果有订单号筛选，在前端过滤
      if (searchForm.order_no) {
        data = data.filter(p => p.order_no.includes(searchForm.order_no))
      }

      // 如果有收款方式筛选，在前端过滤
      if (searchForm.payment_method) {
        data = data.filter(p => p.payment_method === searchForm.payment_method)
      }

      payments.value = data
      pagination.total = data.length
    }
  } catch (error) {
    ElMessage.error('加载收款列表失败')
  } finally {
    loading.value = false
  }
}

// 加载可用订单
const loadAvailableOrders = async () => {
  try {
    const response = await getOrderList()
    if (response.code === 200) {
      availableOrders.value = response.data
    }
  } catch (error) {
    console.error('加载订单列表失败:', error)
  }
}

// 订单选择改变
const handleOrderChange = async (orderId) => {
  if (!orderId) {
    selectedOrderSummary.value = null
    return
  }

  try {
    const response = await getOrderPaymentSummary(orderId)
    if (response.code === 200) {
      selectedOrderSummary.value = response.data
      // 自动设置收款金额为未收款金额
      createForm.payment_amount = Number(response.data.unpaid_amount)
    }
  } catch (error) {
    ElMessage.error('获取订单收款信息失败')
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadPayments()
}

// 重置
const handleReset = () => {
  searchForm.order_no = ''
  searchForm.payment_method = ''
  searchForm.status = ''
  handleSearch()
}

// 显示创建对话框
const showCreateDialog = () => {
  createDialogVisible.value = true
  loadAvailableOrders()
}

// 重置创建表单
const resetCreateForm = () => {
  if (createFormRef.value) {
    createFormRef.value.resetFields()
  }
  createForm.order_id = null
  createForm.payment_amount = 0
  createForm.payment_method = 'BANK_TRANSFER'
  createForm.payment_date = new Date()
  createForm.received_by = ''
  createForm.voucher_no = ''
  createForm.remark = ''
  selectedOrderSummary.value = null
}

// 创建收款
const handleCreate = async () => {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const response = await createPayment(createForm)
      if (response.code === 200) {
        ElMessage.success('收款登记成功')
        createDialogVisible.value = false
        loadPayments()
        loadStatistics()
      }
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '收款登记失败')
    } finally {
      submitting.value = false
    }
  })
}

// 显示详情
const showDetail = async (payment) => {
  try {
    const response = await getPaymentDetail(payment.id)
    if (response.code === 200) {
      currentPayment.value = response.data
      detailDialogVisible.value = true
    }
  } catch (error) {
    ElMessage.error('获取收款详情失败')
  }
}

// 处理打印凭证
const handlePrint = async (row) => {
  try {
    const blob = await downloadPaymentReceiptPDF(row.id)
    const filename = `收款凭证_${row.payment_no}.pdf`
    downloadFile(blob, filename)
    ElMessage.success('PDF生成成功')
  } catch (error) {
    console.error('下载PDF失败:', error)
    ElMessage.error('下载PDF失败')
  }
}

// 取消收款
const handleCancel = async (payment) => {
  try {
    const { value: reason } = await ElMessageBox.prompt('请输入取消原因', '取消收款', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '请输入取消原因'
    })

    const response = await cancelPayment(payment.id, reason)
    if (response.code === 200) {
      ElMessage.success('收款已取消')
      loadPayments()
      loadStatistics()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消收款失败')
    }
  }
}

// 格式化金额
const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return Number(amount).toFixed(2)
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取收款方式标签
const getPaymentMethodLabel = (method) => {
  const item = paymentMethods.find(m => m.value === method)
  return item ? item.label : method
}

// 获取收款方式类型
const getPaymentMethodType = (method) => {
  const typeMap = {
    'CASH': 'warning',
    'BANK_TRANSFER': 'success',
    'ALIPAY': 'primary',
    'WECHAT': 'success',
    'CHECK': 'info',
    'OTHER': ''
  }
  return typeMap[method] || ''
}

// 获取状态标签
const getStatusLabel = (status) => {
  const map = {
    'CONFIRMED': '已确认',
    'PENDING': '待确认',
    'CANCELLED': '已取消'
  }
  return map[status] || status
}

// 获取状态类型
const getStatusType = (status) => {
  const map = {
    'CONFIRMED': 'success',
    'PENDING': 'warning',
    'CANCELLED': 'info'
  }
  return map[status] || ''
}

// 初始化
onMounted(() => {
  loadStatistics()
  loadPayments()
})
</script>

<style scoped>
.payments-container {
  padding: 20px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
}

.stat-icon {
  opacity: 0.6;
}

.stat-methods {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.method-tag {
  font-size: 12px;
}

/* 搜索卡片 */
.search-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.search-form {
  margin: 0;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

/* 分页 */
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 收款详情 */
.payment-detail {
  padding: 10px 0;
}

/* 工具类 */
.w-full {
  width: 100%;
}

.font-mono {
  font-family: ui-monospace, monospace;
}

.font-bold {
  font-weight: 700;
}

.text-indigo-600 {
  color: #4f46e5;
}

.text-emerald-600 {
  color: #10b981;
}

.text-red-600 {
  color: #dc2626;
}

.text-slate-600 {
  color: #475569;
}

.bg-slate-50 {
  background-color: #f8fafc;
}

.rounded {
  border-radius: 0.375rem;
}

.whitespace-pre-wrap {
  white-space: pre-wrap;
}

.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.p-3 {
  padding: 0.75rem;
}

.text-sm {
  font-size: 0.875rem;
}

.text-xl {
  font-size: 1.25rem;
}
</style>
