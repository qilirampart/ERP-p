<template>
  <div class="h-full flex flex-col">
    <!-- 头部 -->
    <header class="h-20 flex items-center justify-between px-8 lg:px-12 flex-shrink-0">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">库存管理</h1>
        <p class="text-sm text-slate-500 mt-1">物料信息 / 入库出库</p>
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
          新增物料
        </el-button>
        <el-button :icon="Refresh" circle @click="loadMaterials" />
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
            <el-select v-model="filters.category" placeholder="物料分类" clearable @change="loadMaterials">
              <el-option
                v-for="cat in categories"
                :key="cat.value"
                :label="cat.label"
                :value="cat.value"
              />
            </el-select>
            <el-input v-model="filters.keyword" placeholder="搜索物料名称/编码" clearable>
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="loadMaterials">搜索</el-button>
          </div>
        </div>

        <!-- 物料列表 -->
        <div class="bento-card">
          <el-table :data="materials" v-loading="loading" style="width: 100%">
            <el-table-column prop="code" label="物料编码" width="120" />
            <el-table-column label="分类" width="80">
              <template #default="{ row }">
                <el-tag :type="getCategoryType(row.category)" size="small">
                  {{ getCategoryLabel(row.category) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="物料名称" min-width="150" />
            <el-table-column label="规格" width="180">
              <template #default="{ row }">
                <span v-if="row.category === 'PAPER'">
                  {{ row.spec_width }}×{{ row.spec_length }}mm {{ row.gram_weight }}g
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="库存" width="160" align="right">
              <template #default="{ row }">
                <div class="flex items-center justify-end">
                  <el-icon
                    v-if="getStockStatus(row) === 'CRITICAL'"
                    class="text-red-500 mr-1"
                    :size="16"
                  >
                    <WarningFilled />
                  </el-icon>
                  <el-icon
                    v-else-if="getStockStatus(row) === 'WARNING'"
                    class="text-amber-500 mr-1"
                    :size="16"
                  >
                    <Warning />
                  </el-icon>
                  <span class="font-numeric font-bold" :class="getStockColor(row)">
                    {{ row.current_stock }}
                  </span>
                  <span class="text-xs text-slate-400 ml-1">{{ row.stock_unit }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="成本单价" width="100" align="right">
              <template #default="{ row }">
                <span class="font-numeric">¥{{ row.cost_price }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="240" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" :icon="Top" @click="showStockInDialog(row)">
                  入库
                </el-button>
                <el-button link type="warning" :icon="Bottom" @click="showStockOutDialog(row)">
                  出库
                </el-button>
                <el-button link :icon="Edit" @click="showEditDialog(row)">
                  编辑
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <!-- 创建/编辑物料对话框 -->
    <el-dialog
      :title="dialogMode === 'create' ? '新增物料' : '编辑物料'"
      v-model="dialogVisible"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="物料编码" prop="code">
          <el-input v-model="form.code" :disabled="dialogMode === 'edit'" />
        </el-form-item>

        <el-form-item label="物料分类" prop="category">
          <el-select v-model="form.category" :disabled="dialogMode === 'edit'" @change="onCategoryChange">
            <el-option
              v-for="cat in categories"
              :key="cat.value"
              :label="cat.label"
              :value="cat.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="物料名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>

        <!-- 纸张专用字段 -->
        <template v-if="form.category === 'PAPER'">
          <el-form-item label="克重 (g/m²)" prop="gram_weight">
            <el-input-number v-model="form.gram_weight" :min="50" :max="500" />
          </el-form-item>

          <el-form-item label="纸张尺寸" required>
            <div class="flex items-center space-x-2">
              <el-input-number v-model="form.spec_width" placeholder="宽" :min="100" />
              <span>×</span>
              <el-input-number v-model="form.spec_length" placeholder="长" :min="100" />
              <span class="text-xs text-slate-400">mm</span>
            </div>
          </el-form-item>
        </template>

        <el-form-item label="采购单位" prop="purchase_unit">
          <el-input v-model="form.purchase_unit" placeholder="如：令、吨、套" />
        </el-form-item>

        <el-form-item label="换算率" prop="unit_rate">
          <el-input-number v-model="form.unit_rate" :min="0.01" :precision="2" />
          <span class="text-xs text-slate-400 ml-2">1{{ form.purchase_unit }} = {{ form.unit_rate }}张</span>
        </el-form-item>

        <el-form-item label="成本单价" prop="cost_price">
          <el-input-number v-model="form.cost_price" :min="0" :precision="2" />
          <span class="text-xs text-slate-400 ml-2">元/张</span>
        </el-form-item>

        <el-form-item label="最低库存" prop="min_stock">
          <el-input-number v-model="form.min_stock" :min="0" :precision="0" class="w-full" />
          <span class="text-xs text-slate-400 ml-2">张（严重预警阈值）</span>
        </el-form-item>

        <el-form-item label="安全库存" prop="safety_stock">
          <el-input-number v-model="form.safety_stock" :min="0" :precision="0" class="w-full" />
          <span class="text-xs text-slate-400 ml-2">张（一般预警阈值）</span>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ dialogMode === 'create' ? '创建' : '保存' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 入库对话框 -->
    <el-dialog title="物料入库" v-model="stockInVisible" width="400px">
      <el-form :model="stockForm" label-width="100px">
        <el-form-item label="物料">
          <div class="text-slate-700 font-medium">{{ currentMaterial?.name }}</div>
        </el-form-item>

        <el-form-item label="入库数量">
          <el-input-number v-model="stockForm.quantity" :min="0.01" :precision="2" class="w-full" />
        </el-form-item>

        <el-form-item label="入库单位">
          <el-input v-model="stockForm.unit" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="stockInVisible = false">取消</el-button>
        <el-button type="primary" @click="handleStockIn" :loading="stockOperating">确认入库</el-button>
      </template>
    </el-dialog>

    <!-- 出库对话框 -->
    <el-dialog title="物料出库" v-model="stockOutVisible" width="400px">
      <el-form :model="stockForm" label-width="100px">
        <el-form-item label="物料">
          <div class="text-slate-700 font-medium">{{ currentMaterial?.name }}</div>
        </el-form-item>

        <el-form-item label="当前库存">
          <div class="text-slate-700">
            {{ currentMaterial?.current_stock }} {{ currentMaterial?.stock_unit }}
          </div>
        </el-form-item>

        <el-form-item label="出库数量">
          <el-input-number v-model="stockForm.quantity" :min="0.01" :precision="2" class="w-full" />
        </el-form-item>

        <el-form-item label="出库单位">
          <el-input v-model="stockForm.unit" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="stockOutVisible = false">取消</el-button>
        <el-button type="warning" @click="handleStockOut" :loading="stockOperating">确认出库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Plus,
  Refresh,
  Search,
  Edit,
  Top,
  Bottom,
  Warning,
  WarningFilled
} from '@element-plus/icons-vue'
import {
  getMaterialList,
  createMaterial,
  updateMaterial,
  stockIn,
  stockOut,
  downloadMaterialTemplate,
  exportMaterials,
  importMaterials
} from '@/api/material'

const categories = [
  { value: 'PAPER', label: '纸张' },
  { value: 'INK', label: '油墨' },
  { value: 'AUX', label: '辅料' }
]

const materials = ref([])
const loading = ref(false)
const filters = reactive({
  category: '',
  keyword: ''
})

const dialogVisible = ref(false)
const dialogMode = ref('create')
const formRef = ref(null)
const fileInputRef = ref(null)
const submitting = ref(false)

const form = reactive({
  code: '',
  category: 'PAPER',
  name: '',
  gram_weight: 157,
  spec_width: 787,
  spec_length: 1092,
  purchase_unit: '令',
  unit_rate: 500,
  cost_price: 0.35,
  min_stock: 0,
  safety_stock: 0
})

const rules = {
  code: [{ required: true, message: '请输入物料编码', trigger: 'blur' }],
  category: [{ required: true, message: '请选择物料分类', trigger: 'change' }],
  name: [{ required: true, message: '请输入物料名称', trigger: 'blur' }],
  purchase_unit: [{ required: true, message: '请输入采购单位', trigger: 'blur' }],
  unit_rate: [{ required: true, message: '请输入换算率', trigger: 'blur' }],
  cost_price: [{ required: true, message: '请输入成本单价', trigger: 'blur' }]
}

// 库存操作
const stockInVisible = ref(false)
const stockOutVisible = ref(false)
const stockOperating = ref(false)
const currentMaterial = ref(null)
const stockForm = reactive({
  quantity: 1,
  unit: '张'
})

const loadMaterials = async () => {
  loading.value = true
  try {
    const response = await getMaterialList({
      category: filters.category || undefined
    })
    if (response.code === 200) {
      materials.value = response.data
    }
  } catch (error) {
    console.error('加载物料失败:', error)
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  dialogMode.value = 'edit'
  Object.assign(form, row)
  dialogVisible.value = true
}

const resetForm = () => {
  Object.assign(form, {
    code: '',
    category: 'PAPER',
    name: '',
    gram_weight: 157,
    spec_width: 787,
    spec_length: 1092,
    purchase_unit: '令',
    unit_rate: 500,
    cost_price: 0.35,
    min_stock: 0,
    safety_stock: 0
  })
  formRef.value?.clearValidate()
}

const onCategoryChange = (value) => {
  if (value !== 'PAPER') {
    form.gram_weight = null
    form.spec_width = null
    form.spec_length = null
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const data = { ...form }
        let response

        if (dialogMode.value === 'create') {
          response = await createMaterial(data)
        } else {
          response = await updateMaterial(form.id, data)
        }

        if (response.code === 200) {
          ElMessage.success(dialogMode.value === 'create' ? '创建成功' : '更新成功')
          dialogVisible.value = false
          loadMaterials()
        }
      } catch (error) {
        console.error('操作失败:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const showStockInDialog = (row) => {
  currentMaterial.value = row
  stockForm.quantity = 1
  stockForm.unit = row.purchase_unit
  stockInVisible.value = true
}

const showStockOutDialog = (row) => {
  currentMaterial.value = row
  stockForm.quantity = 1
  stockForm.unit = row.stock_unit
  stockOutVisible.value = true
}

const handleStockIn = async () => {
  stockOperating.value = true
  try {
    const response = await stockIn({
      material_id: currentMaterial.value.id,
      quantity: stockForm.quantity,
      unit: stockForm.unit
    })

    if (response.code === 200) {
      ElMessage.success('入库成功')
      stockInVisible.value = false
      loadMaterials()
    }
  } catch (error) {
    console.error('入库失败:', error)
  } finally {
    stockOperating.value = false
  }
}

const handleStockOut = async () => {
  stockOperating.value = true
  try {
    const response = await stockOut({
      material_id: currentMaterial.value.id,
      quantity: stockForm.quantity,
      unit: stockForm.unit
    })

    if (response.code === 200) {
      ElMessage.success('出库成功')
      stockOutVisible.value = false
      loadMaterials()
    }
  } catch (error) {
    console.error('出库失败:', error)
  } finally {
    stockOperating.value = false
  }
}

const getCategoryLabel = (category) => {
  const cat = categories.find(c => c.value === category)
  return cat?.label || category
}

const getCategoryType = (category) => {
  const typeMap = {
    'PAPER': 'primary',
    'INK': 'success',
    'AUX': 'warning'
  }
  return typeMap[category] || ''
}

const getStockStatus = (material) => {
  const currentStock = parseFloat(material.current_stock || 0)
  const minStock = parseFloat(material.min_stock || 0)
  const safetyStock = parseFloat(material.safety_stock || 0)

  if (currentStock <= minStock) {
    return 'CRITICAL'
  } else if (currentStock <= safetyStock) {
    return 'WARNING'
  }
  return 'NORMAL'
}

const getStockColor = (material) => {
  const status = getStockStatus(material)
  if (status === 'CRITICAL') return 'text-red-500'
  if (status === 'WARNING') return 'text-amber-500'
  return 'text-emerald-500'
}

// ==================== Excel导入导出 ====================

// 下载导入模板
const handleDownloadTemplate = async () => {
  try {
    await downloadMaterialTemplate()
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

    const response = await importMaterials(file)
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
        const { ElMessageBox } = await import('element-plus')
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
      loadMaterials()
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
    await exportMaterials(filters)
    loading.close()

    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}

onMounted(() => {
  loadMaterials()
})
</script>
