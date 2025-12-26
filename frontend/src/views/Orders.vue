<template>
  <div class="flex-1 flex flex-col">
    <!-- 头部 -->
    <header class="h-20 flex items-center justify-between px-8 lg:px-12 flex-shrink-0">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">销售开单</h1>
        <p class="text-sm text-slate-500 mt-1">订单管理 / 智能报价</p>
      </div>
      <div class="flex items-center space-x-4">
        <el-button type="primary" :icon="Plus" @click="showCreateDialog">
          新建订单
        </el-button>
        <el-button :icon="Refresh" circle @click="loadOrders" />
      </div>
    </header>

    <!-- 内容区 -->
    <div class="flex-1 overflow-y-auto px-8 lg:px-12 pb-12">
      <div class="max-w-7xl mx-auto">
        <!-- 筛选器 -->
        <div class="bento-card mb-6">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <el-select v-model="filters.status" placeholder="订单状态" clearable @change="loadOrders">
              <el-option
                v-for="status in orderStatuses"
                :key="status.value"
                :label="status.label"
                :value="status.value"
              />
            </el-select>
            <el-input v-model="filters.customer_name" placeholder="搜索客户名称" clearable>
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="loadOrders">搜索</el-button>
          </div>
        </div>

        <!-- 订单列表 -->
        <div class="bento-card">
          <el-table :data="orders" v-loading="loading" style="width: 100%">
            <el-table-column prop="order_no" label="订单编号" width="180" fixed="left">
              <template #default="{ row }">
                <span class="font-mono font-bold text-indigo-600">{{ row.order_no }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="customer_name" label="客户名称" min-width="150" />

            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="明细数" width="80" align="center">
              <template #default="{ row }">
                <span class="font-bold text-slate-600">{{ row.items_count || 0 }}</span>
              </template>
            </el-table-column>

            <el-table-column label="订单金额" width="140" align="right">
              <template #default="{ row }">
                <span class="font-numeric font-bold text-lg text-emerald-600">
                  ¥{{ formatCurrency(row.total_amount) }}
                </span>
              </template>
            </el-table-column>

            <el-table-column label="创建时间" width="160">
              <template #default="{ row }">
                <span class="text-sm text-slate-500">{{ formatDate(row.created_at) }}</span>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="300" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" :icon="View" @click="showDetailDialog(row.id)">
                  详情
                </el-button>
                <el-button
                  v-if="row.status === 'DRAFT'"
                  link
                  type="success"
                  :icon="Check"
                  @click="handleConfirm(row.id)"
                >
                  确认
                </el-button>
                <el-dropdown @command="(cmd) => handlePrint(cmd, row)">
                  <el-button link type="primary" :icon="Printer">
                    打印
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="order">销售订单</el-dropdown-item>
                      <el-dropdown-item command="delivery">送货单</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
                <el-button
                  v-if="row.status === 'DRAFT'"
                  link
                  type="danger"
                  :icon="Delete"
                  @click="handleDelete(row.id)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div class="mt-6 flex justify-end">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="pagination.total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="loadOrders"
              @current-change="loadOrders"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 创建订单对话框 -->
    <el-dialog
      title="新建订单"
      v-model="createDialogVisible"
      width="1000px"
      :close-on-click-modal="false"
    >
      <el-form :model="orderForm" :rules="orderRules" ref="orderFormRef" label-width="120px">
        <!-- 客户信息 -->
        <div class="mb-6 p-4 bg-slate-50 rounded-lg">
          <h3 class="text-sm font-bold text-slate-700 mb-4">客户信息</h3>
          <div class="grid grid-cols-2 gap-4">
            <el-form-item label="选择客户" prop="customer_id" class="col-span-2">
              <el-select
                v-model="orderForm.customer_id"
                placeholder="输入客户名称搜索，或留空手动输入"
                clearable
                filterable
                remote
                :remote-method="searchCustomers"
                :loading="customerSearchLoading"
                @change="handleCustomerChange"
                class="w-full"
              >
                <el-option
                  v-for="customer in customerList"
                  :key="customer.id"
                  :label="`${customer.customer_name} (${customer.customer_code})`"
                  :value="customer.id"
                >
                  <div class="flex items-center justify-between">
                    <span>{{ customer.customer_name }}</span>
                    <el-tag :type="getCustomerLevelType(customer.customer_level)" size="small">
                      {{ customer.customer_level }}级
                    </el-tag>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="客户名称" prop="customer_name">
              <el-input v-model="orderForm.customer_name" placeholder="请输入客户名称" :disabled="!!orderForm.customer_id" />
            </el-form-item>
            <el-form-item label="联系人" prop="contact_person">
              <el-input v-model="orderForm.contact_person" placeholder="请输入联系人" :disabled="!!orderForm.customer_id" />
            </el-form-item>
            <el-form-item label="联系电话" prop="contact_phone">
              <el-input v-model="orderForm.contact_phone" placeholder="请输入联系电话" :disabled="!!orderForm.customer_id" />
            </el-form-item>
            <el-form-item label="备注" prop="remark">
              <el-input v-model="orderForm.remark" placeholder="备注信息" />
            </el-form-item>
          </div>
        </div>

        <!-- 订单明细 -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-bold text-slate-700">订单明细</h3>
            <el-button type="primary" size="small" :icon="Plus" @click="addOrderItem">
              添加明细
            </el-button>
          </div>

          <div v-for="(item, index) in orderForm.items" :key="index" class="mb-4 p-4 border border-slate-200 rounded-lg">
            <div class="flex justify-between items-start mb-4">
              <span class="text-sm font-bold text-slate-600">明细 #{{ index + 1 }}</span>
              <el-button
                v-if="orderForm.items.length > 1"
                size="small"
                type="danger"
                :icon="Delete"
                link
                @click="removeOrderItem(index)"
              >
                删除
              </el-button>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <el-form-item
                :label="`产品名称`"
                :prop="`items.${index}.product_name`"
                :rules="[{ required: true, message: '请输入产品名称' }]"
              >
                <el-input v-model="item.product_name" placeholder="如：宣传单、名片" />
              </el-form-item>

              <el-form-item
                :label="`选择纸张`"
                :prop="`items.${index}.paper_material_id`"
                :rules="[{ required: true, message: '请选择纸张' }]"
              >
                <el-select v-model="item.paper_material_id" placeholder="选择纸张" class="w-full">
                  <el-option
                    v-for="paper in paperMaterials"
                    :key="paper.id"
                    :label="`${paper.name} - ${paper.spec_width}×${paper.spec_length}mm`"
                    :value="paper.id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item :label="`成品尺寸`">
                <div class="flex items-center space-x-2">
                  <el-input-number v-model="item.finished_size_w" :min="10" :max="2000" placeholder="宽" class="flex-1" />
                  <span>×</span>
                  <el-input-number v-model="item.finished_size_h" :min="10" :max="2000" placeholder="高" class="flex-1" />
                  <span class="text-xs text-slate-400">mm</span>
                </div>
              </el-form-item>

              <el-form-item :label="`印数`">
                <el-input-number v-model="item.quantity" :min="1" :step="100" class="w-full" />
              </el-form-item>

              <el-form-item :label="`页数 (P数)`">
                <el-input-number v-model="item.page_count" :min="1" :max="500" class="w-full" />
              </el-form-item>
            </div>
          </div>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateOrder" :loading="submitting">
          创建订单
        </el-button>
      </template>
    </el-dialog>

    <!-- 订单详情对话框 -->
    <el-dialog
      title="订单详情"
      v-model="detailDialogVisible"
      width="900px"
    >
      <div v-if="currentOrder" v-loading="detailLoading">
        <!-- 订单信息 -->
        <div class="mb-6 p-4 bg-slate-50 rounded-lg">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <span class="text-sm text-slate-500">订单编号：</span>
              <span class="font-mono font-bold text-indigo-600">{{ currentOrder.order_no }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">订单状态：</span>
              <el-tag :type="getStatusType(currentOrder.status)" size="small">
                {{ getStatusLabel(currentOrder.status) }}
              </el-tag>
            </div>
            <div>
              <span class="text-sm text-slate-500">客户名称：</span>
              <span class="font-bold">{{ currentOrder.customer_name }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">联系人：</span>
              <span>{{ currentOrder.contact_person || '-' }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">联系电话：</span>
              <span>{{ currentOrder.contact_phone || '-' }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">创建时间：</span>
              <span>{{ formatDate(currentOrder.created_at) }}</span>
            </div>
            <div class="col-span-2" v-if="currentOrder.remark">
              <span class="text-sm text-slate-500">备注：</span>
              <span>{{ currentOrder.remark }}</span>
            </div>
          </div>
        </div>

        <!-- 订单明细 -->
        <div class="mb-6">
          <h3 class="text-sm font-bold text-slate-700 mb-4">订单明细</h3>
          <el-table :data="currentOrder.items" border>
            <el-table-column type="index" label="#" width="50" />
            <el-table-column prop="product_name" label="产品名称" min-width="120" />
            <el-table-column label="成品尺寸" width="120">
              <template #default="{ row }">
                {{ row.finished_size_w }}×{{ row.finished_size_h }}mm
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="印数" width="100" align="right" />
            <el-table-column prop="page_count" label="页数" width="80" align="center" />
            <el-table-column label="开纸方案" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="row.cut_method === 'ROTATED' ? 'warning' : 'info'">
                  {{ row.cut_method === 'ROTATED' ? '横切' : '直切' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="paper_usage" label="纸张消耗" width="100" align="right">
              <template #default="{ row }">
                <span class="font-numeric">{{ row.paper_usage }}</span> 张
              </template>
            </el-table-column>
            <el-table-column label="明细金额" width="120" align="right">
              <template #default="{ row }">
                <span class="font-numeric font-bold text-emerald-600">
                  ¥{{ formatCurrency(row.item_amount) }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 订单金额汇总 -->
        <div class="flex justify-end mb-6">
          <div class="p-4 bg-indigo-50 rounded-lg border-2 border-indigo-200 min-w-[360px]">
            <div class="flex justify-between items-center mb-2">
              <span class="text-slate-600">明细数量：</span>
              <span class="font-bold">{{ currentOrder.items.length }} 项</span>
            </div>
            <div class="flex justify-between items-center mb-2 pb-2 border-b border-indigo-200">
              <span class="text-lg font-bold text-slate-700">订单总金额：</span>
              <span class="text-2xl font-bold text-indigo-600">
                ¥{{ formatCurrency(currentOrder.total_amount) }}
              </span>
            </div>

            <!-- 收款状态 -->
            <div v-if="paymentSummary" class="mt-3 pt-3 border-t border-indigo-200">
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm text-slate-600">收款状态：</span>
                <el-tag :type="getPaymentStatusType(paymentSummary.payment_status)" size="small">
                  {{ getPaymentStatusLabel(paymentSummary.payment_status) }}
                </el-tag>
              </div>
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm text-slate-600">已收款：</span>
                <span class="font-bold text-emerald-600">
                  ¥{{ formatCurrency(paymentSummary.paid_amount) }}
                </span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-slate-600">未收款：</span>
                <span class="font-bold text-red-600">
                  ¥{{ formatCurrency(paymentSummary.unpaid_amount) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 收款记录 -->
        <div v-if="paymentRecords.length > 0" class="mb-6">
          <h3 class="text-sm font-bold text-slate-700 mb-4">收款记录</h3>
          <el-timeline>
            <el-timeline-item
              v-for="payment in paymentRecords"
              :key="payment.id"
              :timestamp="formatDate(payment.payment_date)"
              placement="top"
              color="#10b981"
            >
              <div class="flex items-center space-x-3 mb-2">
                <el-tag type="success" size="small">
                  {{ getPaymentMethodLabel(payment.payment_method) }}
                </el-tag>
                <span class="font-mono font-bold text-emerald-600">
                  ¥{{ formatCurrency(payment.payment_amount) }}
                </span>
                <span class="text-xs text-slate-500">
                  收款人: {{ payment.received_by }}
                </span>
              </div>
              <div class="text-xs text-slate-500">
                <span class="font-mono">{{ payment.payment_no }}</span>
                <span v-if="payment.voucher_no" class="ml-2">
                  凭证号: {{ payment.voucher_no }}
                </span>
              </div>
              <div v-if="payment.remark" class="text-sm text-slate-500 mt-1">
                备注: {{ payment.remark }}
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button
          v-if="currentOrder && paymentSummary && paymentSummary.payment_status !== 'PAID'"
          type="warning"
          :icon="Money"
          @click="showPaymentDialog"
        >
          收款登记
        </el-button>
        <el-button
          v-if="currentOrder && currentOrder.status === 'DRAFT'"
          type="success"
          :icon="Check"
          @click="handleConfirm(currentOrder.id)"
        >
          确认订单
        </el-button>
      </template>
    </el-dialog>

    <!-- 收款对话框 -->
    <el-dialog
      title="收款登记"
      v-model="paymentDialogVisible"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="paymentForm" :rules="paymentRules" ref="paymentFormRef" label-width="100px">
        <el-form-item label="订单信息">
          <div class="w-full p-3 bg-slate-50 rounded">
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm text-slate-500">订单号：</span>
              <span class="font-mono font-bold">{{ currentOrder?.order_no }}</span>
            </div>
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm text-slate-500">客户名称：</span>
              <span>{{ currentOrder?.customer_name }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm text-slate-500">订单总金额：</span>
              <span class="font-bold text-indigo-600">¥{{ formatCurrency(currentOrder?.total_amount) }}</span>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="未收款金额">
          <div class="text-xl font-bold text-red-600">
            ¥{{ formatCurrency(paymentSummary?.unpaid_amount || 0) }}
          </div>
        </el-form-item>

        <el-form-item label="收款金额" prop="payment_amount">
          <el-input-number
            v-model="paymentForm.payment_amount"
            :min="0.01"
            :max="Number(paymentSummary?.unpaid_amount || 0)"
            :precision="2"
            :step="100"
            class="w-full"
          />
        </el-form-item>

        <el-form-item label="收款方式" prop="payment_method">
          <el-select v-model="paymentForm.payment_method" class="w-full">
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
            v-model="paymentForm.payment_date"
            type="datetime"
            placeholder="选择收款日期"
            class="w-full"
          />
        </el-form-item>

        <el-form-item label="收款人" prop="received_by">
          <el-input v-model="paymentForm.received_by" placeholder="请输入收款人姓名" />
        </el-form-item>

        <el-form-item label="凭证号" prop="voucher_no">
          <el-input
            v-model="paymentForm.voucher_no"
            placeholder="银行流水号/支付宝订单号等（可选）"
          />
        </el-form-item>

        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="paymentForm.remark"
            type="textarea"
            :rows="3"
            placeholder="备注信息（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="paymentDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreatePayment" :loading="paymentSubmitting">
          确认收款
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search, View, Edit, Delete, Check, Top, Bottom, Money, Wallet, Printer } from '@element-plus/icons-vue'
import { getOrderList, getOrderDetail, createOrder, confirmOrder, deleteOrder } from '@/api/order'
import { getMaterialList } from '@/api/material'
import { getCustomerList } from '@/api/customer'
import { createPayment, getPaymentList, getOrderPaymentSummary } from '@/api/payment'
import { downloadOrderPDF, downloadDeliveryPDF, downloadFile } from '@/api/print'

// 订单列表
const orders = ref([])
const loading = ref(false)

// 筛选条件
const filters = reactive({
  status: '',
  customer_name: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 订单状态选项
const orderStatuses = [
  { label: '草稿', value: 'DRAFT' },
  { label: '已确认', value: 'CONFIRMED' },
  { label: '生产中', value: 'PRODUCTION' },
  { label: '已完成', value: 'COMPLETED' }
]

// 创建订单对话框
const createDialogVisible = ref(false)
const orderForm = reactive({
  customer_id: null,
  customer_name: '',
  contact_person: '',
  contact_phone: '',
  remark: '',
  items: [
    {
      product_name: '',
      paper_material_id: null,
      finished_size_w: 210,
      finished_size_h: 285,
      quantity: 1000,
      page_count: 4,
      crafts: null
    }
  ]
})

const orderFormRef = ref(null)
const submitting = ref(false)

const orderRules = {
  customer_name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }]
}

// 纸张物料列表
const paperMaterials = ref([])

// 客户列表和搜索
const customerList = ref([])
const customerSearchLoading = ref(false)

// 订单详情对话框
const detailDialogVisible = ref(false)
const currentOrder = ref(null)
const detailLoading = ref(false)

// 收款管理相关
const paymentDialogVisible = ref(false)
const paymentForm = reactive({
  order_id: null,
  payment_amount: 0,
  payment_method: 'BANK_TRANSFER',
  payment_date: new Date(),
  received_by: '',
  voucher_no: '',
  remark: ''
})
const paymentFormRef = ref(null)
const paymentSubmitting = ref(false)

// 收款记录列表
const paymentRecords = ref([])

// 收款汇总信息
const paymentSummary = ref(null)

const paymentRules = {
  payment_amount: [
    { required: true, message: '请输入收款金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '收款金额必须大于0', trigger: 'blur' }
  ],
  payment_method: [{ required: true, message: '请选择收款方式', trigger: 'change' }],
  payment_date: [{ required: true, message: '请选择收款日期', trigger: 'change' }],
  received_by: [{ required: true, message: '请输入收款人', trigger: 'blur' }]
}

// 收款方式选项
const paymentMethods = [
  { label: '现金', value: 'CASH' },
  { label: '银行转账', value: 'BANK_TRANSFER' },
  { label: '支付宝', value: 'ALIPAY' },
  { label: '微信', value: 'WECHAT' },
  { label: '支票', value: 'CHECK' },
  { label: '其他', value: 'OTHER' }
]

// 加载订单列表
const loadOrders = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }

    if (filters.status) {
      params.status = filters.status
    }

    if (filters.customer_name) {
      params.customer_name = filters.customer_name
    }

    const response = await getOrderList(params)
    if (response.code === 200) {
      orders.value = response.data
      // 注意：后端没有返回total，这里简化处理
      pagination.total = response.data.length
    }
  } catch (error) {
    ElMessage.error('加载订单列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 加载纸张物料
const loadPaperMaterials = async () => {
  try {
    const response = await getMaterialList({ category: 'PAPER' })
    if (response.code === 200) {
      paperMaterials.value = response.data
    }
  } catch (error) {
    console.error('加载纸张物料失败', error)
  }
}

// 搜索客户
const searchCustomers = async (keyword) => {
  if (!keyword || keyword.trim() === '') {
    customerList.value = []
    return
  }

  customerSearchLoading.value = true
  try {
    const response = await getCustomerList({
      keyword: keyword.trim(),
      status: 'ACTIVE',
      limit: 20
    })
    if (response.code === 200) {
      customerList.value = response.data
    }
  } catch (error) {
    console.error('搜索客户失败', error)
  } finally {
    customerSearchLoading.value = false
  }
}

// 处理客户选择
const handleCustomerChange = (customerId) => {
  if (!customerId) {
    // 清空选择，允许手动输入
    orderForm.customer_name = ''
    orderForm.contact_person = ''
    orderForm.contact_phone = ''
    return
  }

  // 根据选中的客户ID填充信息
  const selectedCustomer = customerList.value.find(c => c.id === customerId)
  if (selectedCustomer) {
    orderForm.customer_name = selectedCustomer.customer_name
    orderForm.contact_person = selectedCustomer.contact_person || ''
    orderForm.contact_phone = selectedCustomer.contact_phone || ''
  }
}

// 获取客户等级颜色类型
const getCustomerLevelType = (level) => {
  const types = {
    A: 'danger',
    B: 'warning',
    C: '',
    D: 'info'
  }
  return types[level] || ''
}

// 显示创建对话框
const showCreateDialog = () => {
  // 重置表单
  orderForm.customer_id = null
  orderForm.customer_name = ''
  orderForm.contact_person = ''
  orderForm.contact_phone = ''
  orderForm.remark = ''
  orderForm.items = [
    {
      product_name: '',
      paper_material_id: null,
      finished_size_w: 210,
      finished_size_h: 285,
      quantity: 1000,
      page_count: 4,
      crafts: null
    }
  ]
  customerList.value = []
  createDialogVisible.value = true
}

// 添加订单明细
const addOrderItem = () => {
  orderForm.items.push({
    product_name: '',
    paper_material_id: null,
    finished_size_w: 210,
    finished_size_h: 285,
    quantity: 1000,
    page_count: 4,
    crafts: null
  })
}

// 删除订单明细
const removeOrderItem = (index) => {
  orderForm.items.splice(index, 1)
}

// 创建订单
const handleCreateOrder = async () => {
  if (!orderFormRef.value) return

  await orderFormRef.value.validate(async (valid) => {
    if (!valid) return

    // 验证至少有一个明细
    if (orderForm.items.length === 0) {
      ElMessage.warning('请至少添加一个订单明细')
      return
    }

    // 验证每个明细的必填字段
    for (let i = 0; i < orderForm.items.length; i++) {
      const item = orderForm.items[i]
      if (!item.product_name) {
        ElMessage.warning(`请输入明细 #${i + 1} 的产品名称`)
        return
      }
      if (!item.paper_material_id) {
        ElMessage.warning(`请选择明细 #${i + 1} 的纸张`)
        return
      }
    }

    submitting.value = true
    try {
      const response = await createOrder(orderForm)
      if (response.code === 200) {
        ElMessage.success('订单创建成功')
        createDialogVisible.value = false
        loadOrders()
      } else {
        ElMessage.error(response.msg || '创建订单失败')
      }
    } catch (error) {
      ElMessage.error('创建订单失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

// 显示订单详情
const showDetailDialog = async (orderId) => {
  detailDialogVisible.value = true
  detailLoading.value = true
  currentOrder.value = null
  paymentSummary.value = null
  paymentRecords.value = []

  try {
    // 加载订单详情
    const response = await getOrderDetail(orderId)
    if (response.code === 200) {
      currentOrder.value = response.data

      // 加载收款汇总信息
      loadPaymentSummary(orderId)

      // 加载收款记录
      loadPaymentRecords(orderId)
    } else {
      ElMessage.error('获取订单详情失败')
    }
  } catch (error) {
    ElMessage.error('获取订单详情失败')
    console.error(error)
  } finally {
    detailLoading.value = false
  }
}

// 加载订单收款汇总
const loadPaymentSummary = async (orderId) => {
  try {
    const response = await getOrderPaymentSummary(orderId)
    if (response.code === 200) {
      paymentSummary.value = response.data
    }
  } catch (error) {
    console.error('加载收款汇总失败', error)
  }
}

// 加载收款记录
const loadPaymentRecords = async (orderId) => {
  try {
    const response = await getPaymentList({ order_id: orderId })
    if (response.code === 200) {
      paymentRecords.value = response.data
    }
  } catch (error) {
    console.error('加载收款记录失败', error)
  }
}

// 显示收款对话框
const showPaymentDialog = () => {
  if (!currentOrder.value) return

  // 重置表单
  Object.assign(paymentForm, {
    order_id: currentOrder.value.id,
    payment_amount: paymentSummary.value?.unpaid_amount || 0,
    payment_method: 'BANK_TRANSFER',
    payment_date: new Date(),
    received_by: '',
    voucher_no: '',
    remark: ''
  })

  paymentDialogVisible.value = true
}

// 创建收款记录
const handleCreatePayment = async () => {
  if (!paymentFormRef.value) return

  await paymentFormRef.value.validate(async (valid) => {
    if (!valid) return

    paymentSubmitting.value = true
    try {
      const response = await createPayment(paymentForm)
      if (response.code === 200) {
        ElMessage.success('收款登记成功')
        paymentDialogVisible.value = false

        // 重新加载收款信息
        await loadPaymentSummary(currentOrder.value.id)
        await loadPaymentRecords(currentOrder.value.id)
      } else {
        ElMessage.error(response.msg || '收款登记失败')
      }
    } catch (error) {
      ElMessage.error('收款登记失败')
      console.error(error)
    } finally {
      paymentSubmitting.value = false
    }
  })
}

// 获取收款方式标签
const getPaymentMethodLabel = (method) => {
  const methodMap = {
    'CASH': '现金',
    'BANK_TRANSFER': '银行转账',
    'ALIPAY': '支付宝',
    'WECHAT': '微信',
    'CHECK': '支票',
    'OTHER': '其他'
  }
  return methodMap[method] || method
}

// 获取收款状态类型
const getPaymentStatusType = (status) => {
  const typeMap = {
    'UNPAID': 'danger',
    'PARTIAL': 'warning',
    'PAID': 'success'
  }
  return typeMap[status] || 'info'
}

// 获取收款状态标签
const getPaymentStatusLabel = (status) => {
  const labelMap = {
    'UNPAID': '未收款',
    'PARTIAL': '部分收款',
    'PAID': '已收款'
  }
  return labelMap[status] || status
}

// 确认订单
const handleConfirm = async (orderId) => {
  try {
    await ElMessageBox.confirm('确认后订单将进入生产流程，确定要确认此订单吗？', '确认订单', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await confirmOrder(orderId)
    if (response.code === 200) {
      ElMessage.success('订单已确认')
      detailDialogVisible.value = false
      loadOrders()
    } else {
      ElMessage.error(response.msg || '确认订单失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('确认订单失败')
      console.error(error)
    }
  }
}

// 删除订单
const handleDelete = async (orderId) => {
  try {
    await ElMessageBox.confirm('删除后将无法恢复，确定要删除此订单吗？', '删除订单', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'error'
    })

    const response = await deleteOrder(orderId)
    if (response.code === 200) {
      ElMessage.success('订单已删除')
      loadOrders()
    } else {
      ElMessage.error(response.msg || '删除订单失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除订单失败')
      console.error(error)
    }
  }
}

// 处理打印
const handlePrint = async (command, row) => {
  try {
    let blob, filename

    if (command === 'order') {
      // 下载销售订单PDF
      blob = await downloadOrderPDF(row.id)
      filename = `销售订单_${row.order_no}.pdf`
    } else if (command === 'delivery') {
      // 下载送货单PDF
      blob = await downloadDeliveryPDF(row.id)
      filename = `送货单_${row.order_no}.pdf`
    }

    if (blob) {
      downloadFile(blob, filename)
      ElMessage.success('PDF生成成功')
    }
  } catch (error) {
    console.error('下载PDF失败:', error)
    ElMessage.error('下载PDF失败')
  }
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    'DRAFT': 'info',
    'CONFIRMED': 'success',
    'PRODUCTION': 'warning',
    'COMPLETED': ''
  }
  return typeMap[status] || 'info'
}

// 获取状态标签
const getStatusLabel = (status) => {
  const labelMap = {
    'DRAFT': '草稿',
    'CONFIRMED': '已确认',
    'PRODUCTION': '生产中',
    'COMPLETED': '已完成'
  }
  return labelMap[status] || status
}

// 格式化金额
const formatCurrency = (amount) => {
  return parseFloat(amount).toFixed(2)
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 初始化
onMounted(() => {
  loadOrders()
  loadPaperMaterials()
})
</script>

<style scoped>
/* Element Plus 表格自定义样式 */
:deep(.el-table) {
  border-radius: 12px;
}

:deep(.el-table__header) {
  background-color: #f8fafc;
}

:deep(.el-pagination) {
  --el-pagination-button-disabled-bg-color: transparent;
}
</style>
