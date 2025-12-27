<template>
  <div class="h-full flex flex-col">
    <!-- 头部 -->
    <header class="h-20 flex items-center justify-between px-8 lg:px-12 flex-shrink-0">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">客户管理</h1>
        <p class="text-sm text-slate-500 mt-1">客户档案 / 交易统计</p>
      </div>
      <div class="flex items-center space-x-4">
        <el-button type="success" plain @click="handleDownloadTemplate">
          下载模板
        </el-button>
        <el-button type="warning" plain @click="triggerFileInput">
          导入Excel
        </el-button>
        <el-button type="info" plain @click="handleExport">
          导出Excel
        </el-button>
        <el-button type="primary" :icon="Plus" @click="showCreateDialog">
          新建客户
        </el-button>
        <el-button :icon="Refresh" circle @click="loadCustomers" />
      </div>
      <!-- 隐藏的文件输入 -->
      <input
        ref="fileInputRef"
        type="file"
        accept=".xlsx,.xls"
        style="display: none"
        @change="handleFileChange"
      />
    </header>

    <!-- 内容区 -->
    <div class="flex-1 overflow-y-auto px-8 lg:px-12 pb-12">
      <div class="max-w-7xl mx-auto">
        <!-- 筛选器 -->
        <div class="bento-card mb-6">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <el-input v-model="filters.keyword" placeholder="搜索客户名称/编码/联系人/电话" clearable>
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select v-model="filters.status" placeholder="客户状态" clearable>
              <el-option label="活跃" value="ACTIVE" />
              <el-option label="停用" value="INACTIVE" />
            </el-select>
            <el-select v-model="filters.customer_level" placeholder="客户等级" clearable>
              <el-option label="A - 重要客户" value="A" />
              <el-option label="B - 优质客户" value="B" />
              <el-option label="C - 普通客户" value="C" />
              <el-option label="D - 潜在客户" value="D" />
            </el-select>
            <el-button type="primary" @click="loadCustomers">搜索</el-button>
          </div>
        </div>

        <!-- 客户列表 -->
        <div class="bento-card">
          <el-table :data="customers" v-loading="loading" style="width: 100%">
            <el-table-column prop="customer_code" label="客户编码" width="150" fixed="left">
              <template #default="{ row }">
                <span class="font-mono text-sm font-bold text-indigo-600">{{ row.customer_code }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="customer_name" label="客户名称" min-width="150" />

            <el-table-column prop="short_name" label="简称" width="100" />

            <el-table-column label="客户等级" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getLevelType(row.customer_level)" size="small">
                  {{ getLevelLabel(row.customer_level) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column prop="contact_person" label="联系人" width="100" />

            <el-table-column prop="contact_phone" label="联系电话" width="130" />

            <el-table-column label="账户余额" width="140" align="right">
              <template #default="{ row }">
                <span class="font-numeric font-bold text-emerald-600">
                  ¥{{ formatCurrency(row.balance) }}
                </span>
              </template>
            </el-table-column>

            <el-table-column label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 'ACTIVE' ? 'success' : 'info'" size="small">
                  {{ row.status === 'ACTIVE' ? '活跃' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="创建时间" width="110">
              <template #default="{ row }">
                <span class="text-sm text-slate-500">{{ formatDate(row.created_at) }}</span>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="260" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" :icon="View" @click="showDetailDialog(row.id)">
                  详情
                </el-button>
                <el-button link type="warning" :icon="Edit" @click="showEditDialog(row)">
                  编辑
                </el-button>
                <el-button link type="danger" :icon="Delete" @click="handleDelete(row.id)">
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
              :page-sizes="[20, 50, 100, 200]"
              :total="pagination.total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="loadCustomers"
              @current-change="loadCustomers"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 创建客户对话框 -->
    <el-dialog
      title="新建客户"
      v-model="createDialogVisible"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="customerForm" :rules="customerRules" ref="customerFormRef" label-width="100px">
        <div class="mb-6 p-4 bg-slate-50 rounded-lg">
          <h3 class="text-sm font-bold text-slate-700 mb-4">基本信息</h3>
          <div class="grid grid-cols-2 gap-4">
            <el-form-item label="客户名称" prop="customer_name">
              <el-input v-model="customerForm.customer_name" placeholder="请输入客户名称" />
            </el-form-item>
            <el-form-item label="简称" prop="short_name">
              <el-input v-model="customerForm.short_name" placeholder="请输入简称" />
            </el-form-item>
            <el-form-item label="客户等级" prop="customer_level">
              <el-select v-model="customerForm.customer_level" placeholder="选择客户等级" class="w-full">
                <el-option label="A - 重要客户" value="A" />
                <el-option label="B - 优质客户" value="B" />
                <el-option label="C - 普通客户" value="C" />
                <el-option label="D - 潜在客户" value="D" />
              </el-select>
            </el-form-item>
            <el-form-item label="信用额度" prop="credit_limit">
              <el-input-number v-model="customerForm.credit_limit" :min="0" :precision="2" class="w-full" />
            </el-form-item>
          </div>
        </div>

        <div class="mb-6 p-4 bg-slate-50 rounded-lg">
          <h3 class="text-sm font-bold text-slate-700 mb-4">联系信息</h3>
          <div class="grid grid-cols-2 gap-4">
            <el-form-item label="联系人" prop="contact_person">
              <el-input v-model="customerForm.contact_person" placeholder="请输入联系人" />
            </el-form-item>
            <el-form-item label="联系电话" prop="contact_phone">
              <el-input v-model="customerForm.contact_phone" placeholder="请输入联系电话" />
            </el-form-item>
            <el-form-item label="邮箱" prop="contact_email">
              <el-input v-model="customerForm.contact_email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="税号" prop="tax_number">
              <el-input v-model="customerForm.tax_number" placeholder="请输入税号" />
            </el-form-item>
          </div>
          <el-form-item label="地址" prop="address">
            <el-input v-model="customerForm.address" type="textarea" :rows="2" placeholder="请输入地址" />
          </el-form-item>
        </div>

        <el-form-item label="备注" prop="remark">
          <el-input v-model="customerForm.remark" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateCustomer" :loading="submitting">
          创建客户
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑客户对话框 -->
    <el-dialog
      title="编辑客户"
      v-model="editDialogVisible"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" :rules="customerRules" ref="editFormRef" label-width="100px">
        <div class="mb-6 p-4 bg-slate-50 rounded-lg">
          <h3 class="text-sm font-bold text-slate-700 mb-4">基本信息</h3>
          <div class="grid grid-cols-2 gap-4">
            <el-form-item label="客户名称" prop="customer_name">
              <el-input v-model="editForm.customer_name" placeholder="请输入客户名称" />
            </el-form-item>
            <el-form-item label="简称" prop="short_name">
              <el-input v-model="editForm.short_name" placeholder="请输入简称" />
            </el-form-item>
            <el-form-item label="客户等级" prop="customer_level">
              <el-select v-model="editForm.customer_level" placeholder="选择客户等级" class="w-full">
                <el-option label="A - 重要客户" value="A" />
                <el-option label="B - 优质客户" value="B" />
                <el-option label="C - 普通客户" value="C" />
                <el-option label="D - 潜在客户" value="D" />
              </el-select>
            </el-form-item>
            <el-form-item label="信用额度" prop="credit_limit">
              <el-input-number v-model="editForm.credit_limit" :min="0" :precision="2" class="w-full" />
            </el-form-item>
            <el-form-item label="状态" prop="status">
              <el-select v-model="editForm.status" placeholder="选择状态" class="w-full">
                <el-option label="活跃" value="ACTIVE" />
                <el-option label="停用" value="INACTIVE" />
              </el-select>
            </el-form-item>
          </div>
        </div>

        <div class="mb-6 p-4 bg-slate-50 rounded-lg">
          <h3 class="text-sm font-bold text-slate-700 mb-4">联系信息</h3>
          <div class="grid grid-cols-2 gap-4">
            <el-form-item label="联系人" prop="contact_person">
              <el-input v-model="editForm.contact_person" placeholder="请输入联系人" />
            </el-form-item>
            <el-form-item label="联系电话" prop="contact_phone">
              <el-input v-model="editForm.contact_phone" placeholder="请输入联系电话" />
            </el-form-item>
            <el-form-item label="邮箱" prop="contact_email">
              <el-input v-model="editForm.contact_email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="税号" prop="tax_number">
              <el-input v-model="editForm.tax_number" placeholder="请输入税号" />
            </el-form-item>
          </div>
          <el-form-item label="地址" prop="address">
            <el-input v-model="editForm.address" type="textarea" :rows="2" placeholder="请输入地址" />
          </el-form-item>
        </div>

        <el-form-item label="备注" prop="remark">
          <el-input v-model="editForm.remark" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateCustomer" :loading="submitting">
          保存修改
        </el-button>
      </template>
    </el-dialog>

    <!-- 客户详情对话框 -->
    <el-dialog
      title="客户详情"
      v-model="detailDialogVisible"
      width="900px"
    >
      <div v-if="currentCustomer" v-loading="detailLoading">
        <!-- 客户基本信息 -->
        <div class="mb-6 p-4 bg-slate-50 rounded-lg">
          <h3 class="text-sm font-bold text-slate-700 mb-4">基本信息</h3>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <span class="text-sm text-slate-500">客户编码：</span>
              <span class="font-mono font-bold text-indigo-600">{{ currentCustomer.customer_code }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">客户名称：</span>
              <span class="font-bold">{{ currentCustomer.customer_name }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">简称：</span>
              <span>{{ currentCustomer.short_name || '-' }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">客户等级：</span>
              <el-tag :type="getLevelType(currentCustomer.customer_level)" size="small">
                {{ getLevelLabel(currentCustomer.customer_level) }}
              </el-tag>
            </div>
            <div>
              <span class="text-sm text-slate-500">状态：</span>
              <el-tag :type="currentCustomer.status === 'ACTIVE' ? 'success' : 'info'" size="small">
                {{ currentCustomer.status === 'ACTIVE' ? '活跃' : '停用' }}
              </el-tag>
            </div>
            <div>
              <span class="text-sm text-slate-500">账户余额：</span>
              <span class="font-numeric font-bold text-emerald-600">¥{{ formatCurrency(currentCustomer.balance) }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">信用额度：</span>
              <span class="font-numeric">¥{{ formatCurrency(currentCustomer.credit_limit) }}</span>
            </div>
          </div>
        </div>

        <!-- 联系信息 -->
        <div class="mb-6 p-4 bg-slate-50 rounded-lg">
          <h3 class="text-sm font-bold text-slate-700 mb-4">联系信息</h3>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <span class="text-sm text-slate-500">联系人：</span>
              <span>{{ currentCustomer.contact_person || '-' }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">联系电话：</span>
              <span>{{ currentCustomer.contact_phone || '-' }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">邮箱：</span>
              <span>{{ currentCustomer.contact_email || '-' }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">税号：</span>
              <span>{{ currentCustomer.tax_number || '-' }}</span>
            </div>
            <div class="col-span-2">
              <span class="text-sm text-slate-500">地址：</span>
              <span>{{ currentCustomer.address || '-' }}</span>
            </div>
          </div>
        </div>

        <!-- 统计信息 -->
        <div v-if="customerStatistics" class="mb-6">
          <h3 class="text-sm font-bold text-slate-700 mb-4">交易统计</h3>
          <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div class="bento-card">
              <div class="text-xs text-slate-500 mb-1">总订单数</div>
              <div class="text-2xl font-bold text-indigo-600">{{ customerStatistics.total_orders }}</div>
            </div>
            <div class="bento-card">
              <div class="text-xs text-slate-500 mb-1">已完成订单</div>
              <div class="text-2xl font-bold text-emerald-600">{{ customerStatistics.completed_orders }}</div>
            </div>
            <div class="bento-card">
              <div class="text-xs text-slate-500 mb-1">总交易额</div>
              <div class="text-lg font-bold text-amber-600">¥{{ formatCurrency(customerStatistics.total_amount) }}</div>
            </div>
            <div class="bento-card">
              <div class="text-xs text-slate-500 mb-1">平均订单金额</div>
              <div class="text-lg font-bold text-purple-600">¥{{ formatCurrency(customerStatistics.average_order_amount) }}</div>
            </div>
            <div class="bento-card">
              <div class="text-xs text-slate-500 mb-1">最近订单</div>
              <div class="text-sm font-bold text-slate-600">{{ customerStatistics.last_order_date ? formatDate(customerStatistics.last_order_date) : '-' }}</div>
            </div>
          </div>
        </div>

        <!-- 历史订单 -->
        <div v-if="customerOrders.length > 0">
          <h3 class="text-sm font-bold text-slate-700 mb-4">历史订单</h3>
          <el-table :data="customerOrders" size="small">
            <el-table-column prop="order_no" label="订单编号" width="180">
              <template #default="{ row }">
                <span class="font-mono text-sm font-bold text-indigo-600">{{ row.order_no }}</span>
              </template>
            </el-table-column>
            <el-table-column label="订单金额" width="140" align="right">
              <template #default="{ row }">
                <span class="font-numeric font-bold text-emerald-600">¥{{ formatCurrency(row.total_amount) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getOrderStatusType(row.status)" size="small">
                  {{ getOrderStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="创建时间" width="160">
              <template #default="{ row }">
                <span class="text-sm text-slate-500">{{ formatDate(row.created_at) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search, View, Edit, Delete } from '@element-plus/icons-vue'
import {
  getCustomerList,
  getCustomerDetail,
  createCustomer,
  updateCustomer,
  deleteCustomer,
  getCustomerStatistics,
  getCustomerOrders,
  downloadCustomerTemplate,
  exportCustomers,
  importCustomers
} from '@/api/customer'

// 数据状态
const loading = ref(false)
const submitting = ref(false)
const detailLoading = ref(false)
const customers = ref([])
const currentCustomer = ref(null)
const customerStatistics = ref(null)
const customerOrders = ref([])

// 筛选条件
const filters = reactive({
  keyword: '',
  status: '',
  customer_level: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 对话框状态
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const detailDialogVisible = ref(false)

// 表单引用
const customerFormRef = ref(null)
const editFormRef = ref(null)
const fileInputRef = ref(null)

// 创建表单
const customerForm = reactive({
  customer_name: '',
  short_name: '',
  contact_person: '',
  contact_phone: '',
  contact_email: '',
  address: '',
  customer_level: 'C',
  credit_limit: 0,
  tax_number: '',
  remark: ''
})

// 编辑表单
const editForm = reactive({
  id: null,
  customer_name: '',
  short_name: '',
  contact_person: '',
  contact_phone: '',
  contact_email: '',
  address: '',
  customer_level: 'C',
  credit_limit: 0,
  tax_number: '',
  status: 'ACTIVE',
  remark: ''
})

// 表单验证规则
const customerRules = {
  customer_name: [
    { required: true, message: '请输入客户名称', trigger: 'blur' }
  ],
  customer_level: [
    { required: true, message: '请选择客户等级', trigger: 'change' }
  ]
}

// 加载客户列表
const loadCustomers = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...filters
    }

    const response = await getCustomerList(params)
    if (response.code === 200) {
      customers.value = response.data
      // 注意：这里需要后端返回total，暂时用数据长度
      pagination.total = response.data.length
    }
  } catch (error) {
    ElMessage.error('加载客户列表失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  Object.assign(customerForm, {
    customer_name: '',
    short_name: '',
    contact_person: '',
    contact_phone: '',
    contact_email: '',
    address: '',
    customer_level: 'C',
    credit_limit: 0,
    tax_number: '',
    remark: ''
  })
  createDialogVisible.value = true
}

// 创建客户
const handleCreateCustomer = async () => {
  const valid = await customerFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const response = await createCustomer(customerForm)
    if (response.code === 200) {
      ElMessage.success('客户创建成功')
      createDialogVisible.value = false
      loadCustomers()
    } else {
      ElMessage.error(response.msg || '创建失败')
    }
  } catch (error) {
    ElMessage.error('创建客户失败：' + error.message)
  } finally {
    submitting.value = false
  }
}

// 显示编辑对话框
const showEditDialog = (customer) => {
  Object.assign(editForm, {
    id: customer.id,
    customer_name: customer.customer_name,
    short_name: customer.short_name,
    contact_person: customer.contact_person,
    contact_phone: customer.contact_phone,
    contact_email: customer.contact_email,
    address: customer.address,
    customer_level: customer.customer_level,
    credit_limit: customer.credit_limit,
    tax_number: customer.tax_number,
    status: customer.status,
    remark: customer.remark
  })
  editDialogVisible.value = true
}

// 更新客户
const handleUpdateCustomer = async () => {
  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const { id, ...data } = editForm
    const response = await updateCustomer(id, data)
    if (response.code === 200) {
      ElMessage.success('客户信息更新成功')
      editDialogVisible.value = false
      loadCustomers()
    } else {
      ElMessage.error(response.msg || '更新失败')
    }
  } catch (error) {
    ElMessage.error('更新客户失败：' + error.message)
  } finally {
    submitting.value = false
  }
}

// 显示详情对话框
const showDetailDialog = async (customerId) => {
  detailDialogVisible.value = true
  detailLoading.value = true

  try {
    // 加载客户详情
    const detailResponse = await getCustomerDetail(customerId)
    if (detailResponse.code === 200) {
      currentCustomer.value = detailResponse.data
    }

    // 加载统计信息
    const statsResponse = await getCustomerStatistics(customerId)
    if (statsResponse.code === 200) {
      customerStatistics.value = statsResponse.data
    }

    // 加载历史订单
    const ordersResponse = await getCustomerOrders(customerId, { skip: 0, limit: 10 })
    if (ordersResponse.code === 200) {
      customerOrders.value = ordersResponse.data
    }
  } catch (error) {
    ElMessage.error('加载客户详情失败：' + error.message)
  } finally {
    detailLoading.value = false
  }
}

// 删除客户
const handleDelete = async (customerId) => {
  try {
    await ElMessageBox.confirm('确定要删除该客户吗？如果客户有关联订单将无法删除。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await deleteCustomer(customerId)
    if (response.code === 200) {
      ElMessage.success('客户已删除')
      loadCustomers()
    } else {
      ElMessage.error(response.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除客户失败：' + error.message)
    }
  }
}

// 获取客户等级标签
const getLevelLabel = (level) => {
  const labels = {
    A: 'A级',
    B: 'B级',
    C: 'C级',
    D: 'D级'
  }
  return labels[level] || level
}

// 获取客户等级类型
const getLevelType = (level) => {
  const types = {
    A: 'danger',
    B: 'warning',
    C: '',
    D: 'info'
  }
  return types[level] || ''
}

// 获取订单状态标签
const getOrderStatusLabel = (status) => {
  const labels = {
    DRAFT: '草稿',
    CONFIRMED: '已确认',
    PRODUCTION: '生产中',
    COMPLETED: '已完成'
  }
  return labels[status] || status
}

// 获取订单状态类型
const getOrderStatusType = (status) => {
  const types = {
    DRAFT: 'info',
    CONFIRMED: 'warning',
    PRODUCTION: 'primary',
    COMPLETED: 'success'
  }
  return types[status] || ''
}

// 格式化货币
const formatCurrency = (value) => {
  if (!value) return '0.00'
  return Number(value).toFixed(2)
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

// ==================== Excel导入导出 ====================

// 下载导入模板
const handleDownloadTemplate = async () => {
  try {
    await downloadCustomerTemplate()
    ElMessage.success('模板下载成功')
  } catch (error) {
    ElMessage.error('下载模板失败：' + error.message)
  }
}

// 触发文件选择
const triggerFileInput = () => {
  fileInputRef.value.click()
}

// 处理文件变化
const handleFileChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 验证文件类型
  const validTypes = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel'
  ]
  if (!validTypes.includes(file.type)) {
    ElMessage.error('请选择Excel文件（.xlsx或.xls）')
    event.target.value = ''
    return
  }

  // 验证文件大小（限制5MB）
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过5MB')
    event.target.value = ''
    return
  }

  try {
    const loading = ElMessage({
      message: '正在导入数据，请稍候...',
      type: 'info',
      duration: 0
    })

    const response = await importCustomers(file)
    loading.close()

    if (response.code === 200) {
      const { success_count, fail_count, errors } = response.data

      let message = `导入完成！成功 ${success_count} 条`
      if (fail_count > 0) {
        message += `，失败 ${fail_count} 条`
      }

      ElMessage.success(message)

      // 如果有错误，显示详情
      if (errors && errors.length > 0) {
        const errorMsg = errors.slice(0, 5).map(err =>
          `第${err.row}行: ${err.error}`
        ).join('\n')

        ElMessageBox.alert(
          errorMsg + (errors.length > 5 ? '\n...' : ''),
          '导入错误详情',
          { type: 'warning' }
        )
      }

      // 刷新列表
      loadCustomers()
    } else {
      ElMessage.error(response.msg || '导入失败')
    }
  } catch (error) {
    ElMessage.error('导入失败：' + error.message)
  } finally {
    // 清空文件输入
    event.target.value = ''
  }
}

// 导出Excel
const handleExport = async () => {
  try {
    const loading = ElMessage({
      message: '正在导出数据，请稍候...',
      type: 'info',
      duration: 0
    })

    // 使用当前筛选条件导出
    await exportCustomers(filters)
    loading.close()

    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadCustomers()
})
</script>
