/**
 * 物料管理API
 */
import request from './request'
import { downloadTemplate, exportExcel, importExcel } from './excel'

/**
 * 获取物料列表
 */
export function getMaterialList(params) {
  return request({
    url: '/materials/',
    method: 'get',
    params
  })
}

/**
 * 获取物料详情
 */
export function getMaterialDetail(id) {
  return request({
    url: `/materials/${id}`,
    method: 'get'
  })
}

/**
 * 创建物料
 */
export function createMaterial(data) {
  return request({
    url: '/materials/',
    method: 'post',
    data
  })
}

/**
 * 更新物料
 */
export function updateMaterial(id, data) {
  return request({
    url: `/materials/${id}`,
    method: 'put',
    data
  })
}

/**
 * 入库操作
 */
export function stockIn(data) {
  return request({
    url: '/materials/stock-in',
    method: 'post',
    data
  })
}

/**
 * 出库操作
 */
export function stockOut(data) {
  return request({
    url: '/materials/stock-out',
    method: 'post',
    data
  })
}

// ==================== Excel导入导出 ====================

/**
 * 下载物料导入模板
 */
export function downloadMaterialTemplate() {
  return downloadTemplate('/materials/excel/template', '物料导入模板.xlsx')
}

/**
 * 导出物料数据
 * @param {Object} params - 筛选参数
 * @param {string} params.keyword - 搜索关键词
 * @param {string} params.category - 物料类别
 * @param {string} params.status - 物料状态
 */
export function exportMaterials(params = {}) {
  return exportExcel('/materials/excel/export', params, '物料数据.xlsx')
}

/**
 * 导入物料数据
 * @param {File} file - Excel文件
 */
export function importMaterials(file) {
  return importExcel('/materials/excel/import', file)
}

/**
 * 获取库存预警统计
 */
export function getWarningStats() {
  return request({
    url: '/materials/warnings/stats',
    method: 'get'
  })
}

/**
 * 获取库存预警物料列表
 * @param {string} warningLevel - 预警级别: CRITICAL/WARNING/ALL
 */
export function getWarningMaterials(warningLevel = null) {
  return request({
    url: '/materials/warnings',
    method: 'get',
    params: { warning_level: warningLevel }
  })
}
