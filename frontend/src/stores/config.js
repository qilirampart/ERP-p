/**
 * 配置Store - 管理系统配置和字典数据
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useConfigStore = defineStore('config', () => {
  // 工艺列表
  const craftList = ref([
    '覆哑膜',
    '覆亮膜',
    '局部UV',
    '满版UV',
    '烫金',
    '烫银',
    '击凸',
    '压凹',
    '模切',
    '骑马钉',
    '锁线胶装',
    '无线胶装'
  ])

  // 物料分类
  const materialCategories = ref([
    { value: 'PAPER', label: '纸张' },
    { value: 'INK', label: '油墨' },
    { value: 'AUX', label: '辅料' }
  ])

  // 订单状态
  const orderStatuses = ref([
    { value: 'DRAFT', label: '草稿', color: '#94A3B8' },
    { value: 'CONFIRMED', label: '已确认', color: '#3B82F6' },
    { value: 'PRODUCTION', label: '生产中', color: '#F59E0B' },
    { value: 'COMPLETED', label: '已完成', color: '#10B981' }
  ])

  // 用户角色
  const userRoles = ref([
    { value: 'ADMIN', label: '管理员' },
    { value: 'SALES', label: '销售人员' },
    { value: 'OPERATOR', label: '操作员' }
  ])

  return {
    craftList,
    materialCategories,
    orderStatuses,
    userRoles
  }
})
