<template>
  <div class="flex-1 flex flex-col">
    <!-- 头部 -->
    <header class="h-20 flex items-center justify-between px-8 lg:px-12 flex-shrink-0">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">智能报价计算</h1>
        <p class="text-sm text-slate-500 mt-1">开纸算法 / 自动报价</p>
      </div>
      <div class="flex items-center space-x-4">
        <el-button @click="resetForm">重置</el-button>
      </div>
    </header>

    <!-- 内容区 -->
    <div class="flex-1 overflow-y-auto px-8 lg:px-12 pb-12">
      <div class="max-w-7xl mx-auto grid grid-cols-12 gap-6">

        <!-- 左侧：输入表单 -->
        <div class="col-span-12 lg:col-span-8 bento-card">
          <h3 class="text-lg font-bold text-slate-800 mb-6">产品规格</h3>

          <el-form :model="form" label-width="120px" class="space-y-4">
            <!-- 纸张选择 -->
            <el-form-item label="选择纸张">
              <el-select
                v-model="form.paper_id"
                placeholder="请选择纸张"
                filterable
                @change="onPaperChange"
                class="w-full"
              >
                <el-option
                  v-for="paper in paperList"
                  :key="paper.id"
                  :label="`${paper.name} - ${paper.spec_width}×${paper.spec_length}mm`"
                  :value="paper.id"
                >
                  <div class="flex justify-between items-center">
                    <span>{{ paper.name }}</span>
                    <span class="text-xs text-slate-400">
                      {{ paper.spec_width }}×{{ paper.spec_length }}mm {{ paper.gram_weight }}g
                    </span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>

            <!-- 成品尺寸 -->
            <el-form-item label="成品尺寸">
              <div class="flex items-center space-x-2">
                <el-input-number
                  v-model="form.target_w"
                  :min="10"
                  :max="2000"
                  placeholder="宽"
                  class="flex-1"
                />
                <span>×</span>
                <el-input-number
                  v-model="form.target_h"
                  :min="10"
                  :max="2000"
                  placeholder="高"
                  class="flex-1"
                />
                <span class="text-xs text-slate-400">mm</span>
              </div>
            </el-form-item>

            <!-- 印数 -->
            <el-form-item label="印数">
              <el-input-number
                v-model="form.quantity"
                :min="1"
                :step="100"
                class="w-full"
              />
            </el-form-item>

            <!-- 页数 -->
            <el-form-item label="页数 (P数)">
              <el-input-number
                v-model="form.page_count"
                :min="1"
                :max="500"
                class="w-full"
              />
            </el-form-item>

            <!-- 修边尺寸 -->
            <el-form-item label="修边尺寸">
              <el-input-number
                v-model="form.trim_margin"
                :min="0"
                :max="50"
                class="w-full"
              />
              <span class="text-xs text-slate-400 ml-2">咬口位预留 (mm)</span>
            </el-form-item>

            <!-- 工艺选择 -->
            <el-form-item label="后道工艺">
              <div class="flex flex-wrap gap-2">
                <el-tag
                  v-for="craft in configStore.craftList"
                  :key="craft"
                  :type="selectedCrafts.includes(craft) ? 'primary' : 'info'"
                  :effect="selectedCrafts.includes(craft) ? 'dark' : 'plain'"
                  class="cursor-pointer"
                  @click="toggleCraft(craft)"
                >
                  {{ craft }}
                </el-tag>
              </div>
            </el-form-item>

            <!-- 计算按钮 -->
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="calculating"
                @click="handleCalculate"
                :disabled="!canCalculate"
                class="w-full"
              >
                <el-icon class="mr-2"><Calculator /></el-icon>
                智能计算报价
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 右侧：报价结果 -->
        <div
          class="col-span-12 lg:col-span-4 bento-card bg-slate-900 text-white border-0 flex flex-col justify-between relative overflow-hidden group"
        >
          <div class="absolute top-0 right-0 w-64 h-64 bg-indigo-600 rounded-full blur-[80px] opacity-20 group-hover:opacity-30 transition-opacity"></div>

          <div class="relative z-10">
            <div v-if="!quoteResult" class="flex flex-col items-center justify-center py-12 text-center">
              <el-icon :size="64" class="text-indigo-400 mb-4"><PriceTag /></el-icon>
              <p class="text-slate-400">填写产品规格后</p>
              <p class="text-slate-400">点击计算获取报价</p>
            </div>

            <div v-else>
              <div class="flex justify-between items-start mb-8">
                <div>
                  <p class="text-indigo-300 text-xs font-bold uppercase tracking-wider">Estimated Cost</p>
                  <h2 class="text-4xl font-bold mt-2 tracking-tight font-numeric">
                    ¥ {{ quoteResult.total_cost }}
                  </h2>
                </div>
                <div class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center backdrop-blur-sm">
                  <el-icon><Money /></el-icon>
                </div>
              </div>

              <!-- 开纸方案 -->
              <div class="bg-white/5 rounded-xl p-4 border border-white/10 mb-6 backdrop-blur-md">
                <div class="flex justify-between text-xs text-gray-400 mb-2">
                  <span>开纸利用率</span>
                  <span :class="getUtilizationColor(quoteResult.utilization)" class="font-bold">
                    {{ (quoteResult.utilization * 100).toFixed(1) }}%
                    {{ getUtilizationLabel(quoteResult.utilization) }}
                  </span>
                </div>
                <div class="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    class="h-full bg-gradient-to-r from-indigo-500 to-emerald-400"
                    :style="{ width: `${quoteResult.utilization * 100}%` }"
                  ></div>
                </div>
                <div class="mt-3 space-y-1">
                  <p class="text-xs text-gray-400">
                    开纸方案: <span class="text-white">{{ getCutMethodLabel(quoteResult.cut_method) }}</span>
                  </p>
                  <p class="text-xs text-gray-400">
                    开数: <span class="text-white font-bold">{{ quoteResult.cut_count }} 开</span>
                  </p>
                  <p class="text-xs text-gray-400">
                    纸张消耗: <span class="text-white font-bold">{{ quoteResult.paper_usage }} 张</span>
                  </p>
                </div>
              </div>

              <!-- 费用明细 -->
              <ul class="space-y-4 text-sm text-gray-300">
                <li class="flex justify-between items-center">
                  <span>📄 纸张成本</span>
                  <span class="text-white font-medium font-numeric">¥ {{ quoteResult.paper_cost }}</span>
                </li>
                <li class="flex justify-between items-center">
                  <span>🖨️ 印刷工费</span>
                  <span class="text-white font-medium font-numeric">¥ {{ quoteResult.print_cost }}</span>
                </li>
                <li class="flex justify-between items-center">
                  <span>✨ 工艺费用</span>
                  <span class="text-white font-medium font-numeric">¥ {{ quoteResult.craft_cost }}</span>
                </li>
              </ul>

              <!-- 纸张信息 -->
              <div class="mt-6 pt-6 border-t border-white/10">
                <p class="text-xs text-gray-400">纸张: {{ quoteResult.paper_name }}</p>
                <p class="text-xs text-gray-400 mt-1">规格: {{ quoteResult.paper_spec }}</p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Calculator,
  Money,
  PriceTag
} from '@element-plus/icons-vue'
import { getMaterialList } from '@/api/material'
import { calculateQuote } from '@/api/quote'
import { useConfigStore } from '@/stores/config'

const configStore = useConfigStore()

const paperList = ref([])
const calculating = ref(false)
const quoteResult = ref(null)
const selectedCrafts = ref([])

const form = reactive({
  paper_id: null,
  target_w: 210,
  target_h: 285,
  quantity: 1000,
  page_count: 1,
  trim_margin: 0
})

const canCalculate = computed(() => {
  return form.paper_id && form.target_w > 0 && form.target_h > 0 && form.quantity > 0
})

const loadPapers = async () => {
  try {
    const response = await getMaterialList({ category: 'PAPER' })
    if (response.code === 200) {
      paperList.value = response.data
    }
  } catch (error) {
    console.error('加载纸张失败:', error)
  }
}

const onPaperChange = () => {
  // 清空之前的报价结果
  quoteResult.value = null
}

const toggleCraft = (craft) => {
  const index = selectedCrafts.value.indexOf(craft)
  if (index > -1) {
    selectedCrafts.value.splice(index, 1)
  } else {
    selectedCrafts.value.push(craft)
  }
}

const handleCalculate = async () => {
  calculating.value = true
  try {
    // 构建工艺费用对象
    const craft_costs = {}
    selectedCrafts.value.forEach(craft => {
      // 简化处理，每个工艺固定费用
      craft_costs[craft] = 300
    })

    const response = await calculateQuote({
      paper_id: form.paper_id,
      target_w: form.target_w,
      target_h: form.target_h,
      quantity: form.quantity,
      page_count: form.page_count,
      trim_margin: form.trim_margin,
      craft_costs: Object.keys(craft_costs).length > 0 ? craft_costs : null
    })

    if (response.code === 200) {
      quoteResult.value = response.data
      ElMessage.success('报价计算成功')
    }
  } catch (error) {
    console.error('计算失败:', error)
    ElMessage.error('计算失败，请检查输入参数')
  } finally {
    calculating.value = false
  }
}

const resetForm = () => {
  Object.assign(form, {
    paper_id: null,
    target_w: 210,
    target_h: 285,
    quantity: 1000,
    page_count: 1,
    trim_margin: 0
  })
  selectedCrafts.value = []
  quoteResult.value = null
}

const getCutMethodLabel = (method) => {
  return method === 'DIRECT' ? '直切（纹路对应）' : '横切（旋转90°）'
}

const getUtilizationColor = (utilization) => {
  if (utilization >= 0.85) return 'text-emerald-400'
  if (utilization >= 0.70) return 'text-amber-400'
  return 'text-red-400'
}

const getUtilizationLabel = (utilization) => {
  if (utilization >= 0.85) return '(优)'
  if (utilization >= 0.70) return '(良)'
  return '(差)'
}

onMounted(() => {
  loadPapers()
})
</script>
