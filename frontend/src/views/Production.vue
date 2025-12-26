<template>
  <div class="flex-1 flex flex-col">
    <!-- 头部 -->
    <header class="h-20 flex items-center justify-between px-8 lg:px-12 flex-shrink-0">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">生产排程</h1>
        <p class="text-sm text-slate-500 mt-1">生产工单管理 / 生产进度跟踪</p>
      </div>
      <div class="flex items-center space-x-4">
        <el-button type="primary" :icon="Plus" @click="showCreateDialog">
          新建工单
        </el-button>
        <el-button :icon="Refresh" circle @click="loadProductions" />
      </div>
    </header>

    <!-- 内容区 -->
    <div class="flex-1 overflow-y-auto px-8 lg:px-12 pb-12">
      <div class="max-w-7xl mx-auto">
        <!-- 统计卡片 -->
        <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
          <div class="bento-card p-3 bg-gradient-to-br from-indigo-50 to-white">
            <div class="text-center">
              <p class="text-xs text-slate-500 mb-1">总工单数</p>
              <p class="text-xl font-bold text-indigo-600">{{ statistics.total_production_orders }}</p>
            </div>
          </div>
          <div class="bento-card p-3">
            <div class="text-center">
              <p class="text-xs text-slate-500 mb-1">待生产</p>
              <p class="text-xl font-bold text-slate-600">{{ statistics.pending_count }}</p>
            </div>
          </div>
          <div class="bento-card p-3">
            <div class="text-center">
              <p class="text-xs text-slate-500 mb-1">生产中</p>
              <p class="text-xl font-bold text-blue-600">{{ statistics.in_progress_count }}</p>
            </div>
          </div>
          <div class="bento-card p-3">
            <div class="text-center">
              <p class="text-xs text-slate-500 mb-1">已完成</p>
              <p class="text-xl font-bold text-emerald-600">{{ statistics.completed_count }}</p>
            </div>
          </div>
          <div class="bento-card p-3">
            <div class="text-center">
              <p class="text-xs text-slate-500 mb-1">今日完成</p>
              <p class="text-xl font-bold text-orange-600">{{ statistics.today_completed_count }}</p>
            </div>
          </div>
        </div>

        <!-- 筛选器 -->
        <div class="bento-card mb-6">
          <div class="flex items-center gap-4">
            <el-select v-model="filters.status" placeholder="生产状态" clearable @change="loadProductions" class="w-64">
              <el-option
                v-for="status in productionStatuses"
                :key="status.value"
                :label="status.label"
                :value="status.value"
              />
            </el-select>
            <el-button type="primary" @click="loadProductions">搜索</el-button>
          </div>
        </div>

        <!-- 生产工单列表 -->
        <div class="bento-card">
          <el-table :data="productions" v-loading="loading" style="width: 100%">
            <el-table-column prop="production_no" label="工单号" width="180" fixed="left">
              <template #default="{ row }">
                <span class="font-mono font-bold text-indigo-600">{{ row.production_no }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="order_no" label="关联订单" width="150">
              <template #default="{ row }">
                <span class="font-mono text-sm">{{ row.order_no }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="customer_name" label="客户名称" min-width="120" />

            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="优先级" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)" size="small">
                  P{{ row.priority }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="进度" width="200">
              <template #default="{ row }">
                <div class="flex items-center space-x-2">
                  <el-progress
                    :percentage="row.progress_percent"
                    :color="getProgressColor(row.progress_percent)"
                    :stroke-width="8"
                  />
                  <span class="text-xs text-slate-500">
                    {{ row.total_completed_quantity }}/{{ row.total_plan_quantity }}
                  </span>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="operator_name" label="操作员" width="100" />

            <el-table-column label="计划时间" width="180">
              <template #default="{ row }">
                <span class="text-sm text-slate-500">
                  {{ row.plan_start_date ? formatDate(row.plan_start_date) : '-' }}
                </span>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="320" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" :icon="View" @click="showDetailDialog(row.id)">
                  详情
                </el-button>
                <el-button
                  v-if="row.status === 'PENDING'"
                  link
                  type="success"
                  :icon="VideoPlay"
                  @click="handleStart(row.id)"
                >
                  开始
                </el-button>
                <el-button
                  v-if="row.status === 'IN_PROGRESS'"
                  link
                  type="warning"
                  :icon="CircleCheck"
                  @click="handleComplete(row.id)"
                >
                  完成
                </el-button>
                <el-button
                  link
                  type="primary"
                  :icon="Printer"
                  @click="handlePrint(row)"
                >
                  打印工单
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
              @size-change="loadProductions"
              @current-change="loadProductions"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 创建工单对话框 -->
    <el-dialog
      title="新建生产工单"
      v-model="createDialogVisible"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="productionForm" :rules="productionRules" ref="productionFormRef" label-width="120px">
        <el-form-item label="选择订单" prop="order_id">
          <el-select
            v-model="productionForm.order_id"
            placeholder="选择已确认的订单"
            class="w-full"
            filterable
            @change="onOrderSelect"
          >
            <el-option
              v-for="order in confirmedOrders"
              :key="order.id"
              :label="`${order.order_no} - ${order.customer_name} (¥${order.total_amount})`"
              :value="order.id"
            />
          </el-select>
        </el-form-item>

        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="计划开始时间" prop="plan_start_date">
            <el-date-picker
              v-model="productionForm.plan_start_date"
              type="datetime"
              placeholder="选择开始时间"
              class="w-full"
            />
          </el-form-item>

          <el-form-item label="计划完成时间" prop="plan_end_date">
            <el-date-picker
              v-model="productionForm.plan_end_date"
              type="datetime"
              placeholder="选择完成时间"
              class="w-full"
            />
          </el-form-item>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="优先级" prop="priority">
            <el-select v-model="productionForm.priority" placeholder="选择优先级" class="w-full">
              <el-option label="最高 (P1)" :value="1" />
              <el-option label="高 (P3)" :value="3" />
              <el-option label="普通 (P5)" :value="5" />
              <el-option label="低 (P7)" :value="7" />
              <el-option label="最低 (P10)" :value="10" />
            </el-select>
          </el-form-item>

          <el-form-item label="操作员" prop="operator_name">
            <el-input v-model="productionForm.operator_name" placeholder="操作员姓名" />
          </el-form-item>
        </div>

        <el-form-item label="生产设备" prop="machine_name">
          <el-input v-model="productionForm.machine_name" placeholder="设备名称（如：海德堡CD102）" />
        </el-form-item>

        <el-form-item label="备注" prop="remark">
          <el-input v-model="productionForm.remark" type="textarea" :rows="3" placeholder="备注信息" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateProduction" :loading="submitting">
          创建工单
        </el-button>
      </template>
    </el-dialog>

    <!-- 工单详情对话框 -->
    <el-dialog
      title="生产工单详情"
      v-model="detailDialogVisible"
      width="1000px"
    >
      <div v-if="currentProduction" v-loading="detailLoading">
        <!-- 工单信息 -->
        <div class="mb-6 p-4 bg-slate-50 rounded-lg">
          <div class="grid grid-cols-3 gap-4">
            <div>
              <span class="text-sm text-slate-500">工单号：</span>
              <span class="font-mono font-bold text-indigo-600">{{ currentProduction.production_no }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">关联订单：</span>
              <span class="font-mono">{{ currentProduction.order_no }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">状态：</span>
              <el-tag :type="getStatusType(currentProduction.status)" size="small">
                {{ getStatusLabel(currentProduction.status) }}
              </el-tag>
            </div>
            <div>
              <span class="text-sm text-slate-500">客户：</span>
              <span class="font-bold">{{ currentProduction.customer_name }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">优先级：</span>
              <el-tag :type="getPriorityType(currentProduction.priority)" size="small">
                P{{ currentProduction.priority }}
              </el-tag>
            </div>
            <div>
              <span class="text-sm text-slate-500">操作员：</span>
              <span>{{ currentProduction.operator_name || '-' }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">设备：</span>
              <span>{{ currentProduction.machine_name || '-' }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">计划开始：</span>
              <span class="text-sm">{{ formatDate(currentProduction.plan_start_date) || '-' }}</span>
            </div>
            <div>
              <span class="text-sm text-slate-500">计划完成：</span>
              <span class="text-sm">{{ formatDate(currentProduction.plan_end_date) || '-' }}</span>
            </div>
            <div v-if="currentProduction.actual_start_date">
              <span class="text-sm text-slate-500">实际开始：</span>
              <span class="text-sm text-green-600">{{ formatDate(currentProduction.actual_start_date) }}</span>
            </div>
            <div v-if="currentProduction.actual_end_date">
              <span class="text-sm text-slate-500">实际完成：</span>
              <span class="text-sm text-green-600">{{ formatDate(currentProduction.actual_end_date) }}</span>
            </div>
          </div>
          <div v-if="currentProduction.remark" class="mt-4">
            <span class="text-sm text-slate-500">备注：</span>
            <span>{{ currentProduction.remark }}</span>
          </div>
        </div>

        <!-- 生产明细 -->
        <div class="mb-6">
          <h3 class="text-sm font-bold text-slate-700 mb-4">生产明细</h3>
          <el-table :data="currentProduction.items" border>
            <el-table-column type="index" label="#" width="50" />
            <el-table-column prop="product_name" label="产品名称" min-width="120" />
            <el-table-column label="成品尺寸" width="120">
              <template #default="{ row }">
                {{ row.finished_size_w }}×{{ row.finished_size_h }}mm
              </template>
            </el-table-column>
            <el-table-column label="开纸方案" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="row.cut_method === 'ROTATED' ? 'warning' : 'info'">
                  {{ row.cut_method === 'ROTATED' ? '横切' : '直切' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="纸张消耗" width="100" align="right">
              <template #default="{ row }">
                {{ row.paper_usage }} 张
              </template>
            </el-table-column>
            <el-table-column label="计划数量" width="100" align="right">
              <template #default="{ row }">
                {{ row.plan_quantity }}
              </template>
            </el-table-column>
            <el-table-column label="完成数量" width="100" align="right">
              <template #default="{ row }">
                <span class="font-bold text-emerald-600">{{ row.completed_quantity }}</span>
              </template>
            </el-table-column>
            <el-table-column label="报废数量" width="100" align="right">
              <template #default="{ row }">
                <span class="font-bold text-red-600">{{ row.rejected_quantity }}</span>
              </template>
            </el-table-column>
            <el-table-column label="完成率" width="100" align="center">
              <template #default="{ row }">
                {{ ((row.completed_quantity / row.plan_quantity) * 100).toFixed(1) }}%
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 报工记录 -->
        <div v-if="productionReports.length > 0">
          <h3 class="text-sm font-bold text-slate-700 mb-4">报工记录</h3>
          <el-timeline>
            <el-timeline-item
              v-for="report in productionReports"
              :key="report.id"
              :timestamp="formatDate(report.report_time)"
              placement="top"
              :color="getReportColor(report.report_type)"
            >
              <div class="flex items-center space-x-2 mb-2">
                <el-tag :type="getReportTagType(report.report_type)" size="small">
                  {{ getReportTypeLabel(report.report_type) }}
                </el-tag>
                <span class="text-sm text-slate-600">{{ report.operator_name }}</span>
              </div>
              <div class="text-sm text-slate-500">
                <span v-if="report.completed_quantity > 0">
                  完成数量: <span class="font-bold text-emerald-600">{{ report.completed_quantity }}</span>
                </span>
                <span v-if="report.rejected_quantity > 0" class="ml-4">
                  报废数量: <span class="font-bold text-red-600">{{ report.rejected_quantity }}</span>
                </span>
              </div>
              <div v-if="report.remark" class="text-sm text-slate-500 mt-1">
                备注: {{ report.remark }}
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button
          v-if="currentProduction && (currentProduction.status === 'PENDING' || currentProduction.status === 'IN_PROGRESS')"
          type="danger"
          @click="handleCancel(currentProduction.id)"
        >
          取消工单
        </el-button>
        <el-button
          v-if="currentProduction && currentProduction.status === 'PENDING'"
          type="primary"
          @click="showEditDialog"
        >
          编辑工单
        </el-button>
        <el-button
          v-if="currentProduction && currentProduction.status === 'PENDING'"
          type="success"
          :icon="VideoPlay"
          @click="handleStart(currentProduction.id)"
        >
          开始生产
        </el-button>
        <el-button
          v-if="currentProduction && currentProduction.status === 'IN_PROGRESS'"
          type="primary"
          @click="showReportDialog"
        >
          进度报工
        </el-button>
        <el-button
          v-if="currentProduction && currentProduction.status === 'IN_PROGRESS'"
          type="warning"
          :icon="CircleCheck"
          @click="handleComplete(currentProduction.id)"
        >
          完成生产
        </el-button>
      </template>
    </el-dialog>

    <!-- 生产报工对话框 -->
    <el-dialog
      title="生产报工"
      v-model="reportDialogVisible"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="reportForm" :rules="reportRules" ref="reportFormRef" label-width="100px">
        <el-form-item label="报工类型" prop="report_type">
          <el-radio-group v-model="reportForm.report_type">
            <el-radio label="PROGRESS">进度报工</el-radio>
            <el-radio label="REJECT">报废登记</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item
          v-if="reportForm.report_type === 'PROGRESS'"
          label="完成数量"
          prop="completed_quantity"
        >
          <el-input-number
            v-model="reportForm.completed_quantity"
            :min="0"
            :max="10000"
            class="w-full"
          />
          <div class="text-xs text-slate-500 mt-1">
            本次完成的数量
          </div>
        </el-form-item>

        <el-form-item label="报废数量" prop="rejected_quantity">
          <el-input-number
            v-model="reportForm.rejected_quantity"
            :min="0"
            :max="10000"
            class="w-full"
          />
          <div class="text-xs text-slate-500 mt-1">
            {{ reportForm.report_type === 'REJECT' ? '报废的数量' : '生产过程中报废的数量' }}
          </div>
        </el-form-item>

        <el-form-item label="操作员" prop="operator_name">
          <el-input v-model="reportForm.operator_name" placeholder="请输入操作员姓名" />
        </el-form-item>

        <el-form-item label="报工说明" prop="remark">
          <el-input
            v-model="reportForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入报工说明（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="reportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateReport" :loading="submitting">
          提交报工
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑工单对话框 -->
    <el-dialog
      title="编辑工单"
      v-model="editDialogVisible"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" ref="editFormRef" label-width="120px">
        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="计划开始时间" prop="plan_start_date">
            <el-date-picker
              v-model="editForm.plan_start_date"
              type="datetime"
              placeholder="选择开始时间"
              class="w-full"
            />
          </el-form-item>

          <el-form-item label="计划完成时间" prop="plan_end_date">
            <el-date-picker
              v-model="editForm.plan_end_date"
              type="datetime"
              placeholder="选择完成时间"
              class="w-full"
            />
          </el-form-item>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="优先级" prop="priority">
            <el-select v-model="editForm.priority" placeholder="选择优先级" class="w-full">
              <el-option label="最高 (P1)" :value="1" />
              <el-option label="高 (P3)" :value="3" />
              <el-option label="普通 (P5)" :value="5" />
              <el-option label="低 (P7)" :value="7" />
              <el-option label="最低 (P10)" :value="10" />
            </el-select>
          </el-form-item>

          <el-form-item label="操作员" prop="operator_name">
            <el-input v-model="editForm.operator_name" placeholder="操作员姓名" />
          </el-form-item>
        </div>

        <el-form-item label="生产设备" prop="machine_name">
          <el-input v-model="editForm.machine_name" placeholder="设备名称（如：海德堡CD102）" />
        </el-form-item>

        <el-form-item label="备注" prop="remark">
          <el-input v-model="editForm.remark" type="textarea" :rows="3" placeholder="备注信息" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateProduction" :loading="submitting">
          保存修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Refresh, View, VideoPlay, CircleCheck,
  DocumentCopy, Clock, Calendar, Printer
} from '@element-plus/icons-vue'
import {
  getProductionList,
  createProductionOrder,
  getProductionDetail,
  startProduction,
  completeProduction,
  getProductionStatistics,
  createProductionReport,
  getProductionReports,
  updateProduction,
  cancelProduction
} from '@/api/production'
import { getOrderList } from '@/api/order'
import { downloadProductionPDF, downloadFile } from '@/api/print'

// 生产工单列表
const productions = ref([])
const loading = ref(false)

// 统计数据
const statistics = ref({
  total_production_orders: 0,
  pending_count: 0,
  in_progress_count: 0,
  completed_count: 0,
  today_completed_count: 0,
  avg_completion_rate: 0
})

// 筛选条件
const filters = reactive({
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 生产状态选项
const productionStatuses = [
  { label: '待生产', value: 'PENDING' },
  { label: '生产中', value: 'IN_PROGRESS' },
  { label: '已完成', value: 'COMPLETED' },
  { label: '已取消', value: 'CANCELLED' }
]

// 创建工单对话框
const createDialogVisible = ref(false)
const productionForm = reactive({
  order_id: null,
  plan_start_date: null,
  plan_end_date: null,
  priority: 5,
  operator_name: '',
  machine_name: '',
  remark: ''
})

const productionFormRef = ref(null)
const submitting = ref(false)
const confirmedOrders = ref([])

const productionRules = {
  order_id: [{ required: true, message: '请选择订单', trigger: 'change' }]
}

// 工单详情对话框
const detailDialogVisible = ref(false)
const currentProduction = ref(null)
const detailLoading = ref(false)

// 报工记录
const productionReports = ref([])

// 报工对话框
const reportDialogVisible = ref(false)
const reportForm = reactive({
  production_order_id: null,
  report_type: 'PROGRESS',
  completed_quantity: 0,
  rejected_quantity: 0,
  operator_name: '',
  remark: ''
})
const reportFormRef = ref(null)

const reportRules = {
  report_type: [{ required: true, message: '请选择报工类型', trigger: 'change' }],
  operator_name: [{ required: true, message: '请输入操作员姓名', trigger: 'blur' }]
}

// 编辑工单对话框
const editDialogVisible = ref(false)
const editForm = reactive({
  id: null,
  plan_start_date: null,
  plan_end_date: null,
  priority: 5,
  operator_name: '',
  machine_name: '',
  remark: ''
})
const editFormRef = ref(null)

// 加载生产统计
const loadStatistics = async () => {
  try {
    const response = await getProductionStatistics()
    if (response.code === 200) {
      statistics.value = response.data
    }
  } catch (error) {
    console.error('加载生产统计失败', error)
  }
}

// 加载生产工单列表
const loadProductions = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }

    if (filters.status) {
      params.status = filters.status
    }

    const response = await getProductionList(params)
    if (response.code === 200) {
      productions.value = response.data
      pagination.total = response.data.length
    }
  } catch (error) {
    ElMessage.error('加载生产工单列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 加载已确认订单
const loadConfirmedOrders = async () => {
  try {
    const response = await getOrderList({ status: 'CONFIRMED' })
    if (response.code === 200) {
      confirmedOrders.value = response.data
    }
  } catch (error) {
    console.error('加载订单列表失败', error)
  }
}

// 显示创建对话框
const showCreateDialog = async () => {
  await loadConfirmedOrders()

  if (confirmedOrders.value.length === 0) {
    ElMessage.warning('没有可用的已确认订单，请先确认订单')
    return
  }

  // 重置表单
  Object.assign(productionForm, {
    order_id: null,
    plan_start_date: null,
    plan_end_date: null,
    priority: 5,
    operator_name: '',
    machine_name: '',
    remark: ''
  })

  createDialogVisible.value = true
}

// 选择订单
const onOrderSelect = (orderId) => {
  // 可以在这里加载订单详情，自动填充一些信息
}

// 创建生产工单
const handleCreateProduction = async () => {
  if (!productionFormRef.value) return

  await productionFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const response = await createProductionOrder(productionForm)
      if (response.code === 200) {
        ElMessage.success('生产工单创建成功')
        createDialogVisible.value = false
        loadProductions()
        loadStatistics()
      } else {
        ElMessage.error(response.msg || '创建生产工单失败')
      }
    } catch (error) {
      ElMessage.error('创建生产工单失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

// 显示工单详情
const showDetailDialog = async (productionId) => {
  detailDialogVisible.value = true
  detailLoading.value = true
  currentProduction.value = null
  productionReports.value = []

  try {
    // 加载工单详情
    const response = await getProductionDetail(productionId)
    if (response.code === 200) {
      currentProduction.value = response.data
    } else {
      ElMessage.error('获取工单详情失败')
    }

    // 加载报工记录
    const reportsResponse = await getProductionReports(productionId)
    if (reportsResponse.code === 200) {
      productionReports.value = reportsResponse.data
    }
  } catch (error) {
    ElMessage.error('获取工单详情失败')
    console.error(error)
  } finally {
    detailLoading.value = false
  }
}

// 开始生产
const handleStart = async (productionId) => {
  try {
    const { value: operatorName } = await ElMessageBox.prompt('请输入操作员姓名', '开始生产', {
      confirmButtonText: '开始',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '请输入操作员姓名'
    })

    const response = await startProduction(productionId, operatorName)
    if (response.code === 200) {
      ElMessage.success('生产已开始')
      detailDialogVisible.value = false
      loadProductions()
      loadStatistics()
    } else {
      ElMessage.error(response.msg || '开始生产失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('开始生产失败')
      console.error(error)
    }
  }
}

// 完成生产
const handleComplete = async (productionId) => {
  try {
    const { value: operatorName } = await ElMessageBox.prompt('请输入操作员姓名', '完成生产', {
      confirmButtonText: '完成',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '请输入操作员姓名'
    })

    const response = await completeProduction(productionId, operatorName)
    if (response.code === 200) {
      ElMessage.success('生产已完成')
      detailDialogVisible.value = false
      loadProductions()
      loadStatistics()
    } else {
      ElMessage.error(response.msg || '完成生产失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('完成生产失败')
      console.error(error)
    }
  }
}

// 处理打印工单
const handlePrint = async (row) => {
  try {
    const blob = await downloadProductionPDF(row.id)
    const filename = `生产工单_${row.production_no}.pdf`
    downloadFile(blob, filename)
    ElMessage.success('PDF生成成功')
  } catch (error) {
    console.error('下载PDF失败:', error)
    ElMessage.error('下载PDF失败')
  }
}

// 显示报工对话框
const showReportDialog = () => {
  if (!currentProduction.value) return

  Object.assign(reportForm, {
    production_order_id: currentProduction.value.id,
    report_type: 'PROGRESS',
    completed_quantity: 0,
    rejected_quantity: 0,
    operator_name: currentProduction.value.operator_name || '',
    remark: ''
  })

  reportDialogVisible.value = true
}

// 创建报工记录
const handleCreateReport = async () => {
  if (!reportFormRef.value) return

  await reportFormRef.value.validate(async (valid) => {
    if (!valid) return

    // 验证至少要有完成数量或报废数量
    if (reportForm.completed_quantity === 0 && reportForm.rejected_quantity === 0) {
      ElMessage.warning('请输入完成数量或报废数量')
      return
    }

    submitting.value = true
    try {
      const response = await createProductionReport(reportForm)
      if (response.code === 200) {
        ElMessage.success('报工提交成功')
        reportDialogVisible.value = false

        // 重新加载工单详情和报工记录
        await showDetailDialog(currentProduction.value.id)

        // 刷新工单列表和统计
        loadProductions()
        loadStatistics()
      } else {
        ElMessage.error(response.msg || '报工提交失败')
      }
    } catch (error) {
      ElMessage.error('报工提交失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

// 获取报工类型标签
const getReportTypeLabel = (reportType) => {
  const labelMap = {
    'START': '开始生产',
    'PROGRESS': '进度报工',
    'COMPLETE': '完成生产',
    'REJECT': '报废登记'
  }
  return labelMap[reportType] || reportType
}

// 获取报工类型标签类型
const getReportTagType = (reportType) => {
  const typeMap = {
    'START': 'success',
    'PROGRESS': 'primary',
    'COMPLETE': 'success',
    'REJECT': 'danger'
  }
  return typeMap[reportType] || 'info'
}

// 获取报工记录颜色
const getReportColor = (reportType) => {
  const colorMap = {
    'START': '#10b981',
    'PROGRESS': '#3b82f6',
    'COMPLETE': '#10b981',
    'REJECT': '#ef4444'
  }
  return colorMap[reportType] || '#64748b'
}

// 显示编辑工单对话框
const showEditDialog = () => {
  if (!currentProduction.value) return

  // 复制当前工单数据到编辑表单
  Object.assign(editForm, {
    id: currentProduction.value.id,
    plan_start_date: currentProduction.value.plan_start_date || null,
    plan_end_date: currentProduction.value.plan_end_date || null,
    priority: currentProduction.value.priority || 5,
    operator_name: currentProduction.value.operator_name || '',
    machine_name: currentProduction.value.machine_name || '',
    remark: currentProduction.value.remark || ''
  })

  editDialogVisible.value = true
}

// 更新生产工单
const handleUpdateProduction = async () => {
  submitting.value = true
  try {
    const { id, ...updateData } = editForm
    const response = await updateProduction(id, updateData)

    if (response.code === 200) {
      ElMessage.success('工单更新成功')
      editDialogVisible.value = false

      // 重新加载工单详情
      await showDetailDialog(id)

      // 刷新工单列表
      loadProductions()
    } else {
      ElMessage.error(response.msg || '工单更新失败')
    }
  } catch (error) {
    ElMessage.error('工单更新失败')
    console.error(error)
  } finally {
    submitting.value = false
  }
}

// 取消生产工单
const handleCancel = async (productionId) => {
  try {
    const { value: reason } = await ElMessageBox.prompt(
      '请输入取消原因',
      '取消生产工单',
      {
        confirmButtonText: '确认取消',
        cancelButtonText: '返回',
        inputPattern: /.+/,
        inputErrorMessage: '请输入取消原因',
        confirmButtonClass: 'el-button--danger',
        type: 'warning'
      }
    )

    const response = await cancelProduction(productionId, reason)

    if (response.code === 200) {
      ElMessage.success('工单已取消')
      detailDialogVisible.value = false
      loadProductions()
      loadStatistics()
    } else {
      ElMessage.error(response.msg || '取消工单失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消工单失败')
      console.error(error)
    }
  }
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    'PENDING': 'info',
    'IN_PROGRESS': 'primary',
    'COMPLETED': 'success',
    'CANCELLED': 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取状态标签
const getStatusLabel = (status) => {
  const labelMap = {
    'PENDING': '待生产',
    'IN_PROGRESS': '生产中',
    'COMPLETED': '已完成',
    'CANCELLED': '已取消'
  }
  return labelMap[status] || status
}

// 获取优先级类型
const getPriorityType = (priority) => {
  if (priority <= 2) return 'danger'
  if (priority <= 4) return 'warning'
  if (priority <= 6) return 'primary'
  return 'info'
}

// 获取进度条颜色
const getProgressColor = (percent) => {
  if (percent >= 100) return '#10b981'
  if (percent >= 80) return '#3b82f6'
  if (percent >= 50) return '#f59e0b'
  return '#ef4444'
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
  loadProductions()
  loadStatistics()
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

:deep(.el-progress__text) {
  font-size: 12px !important;
}
</style>
