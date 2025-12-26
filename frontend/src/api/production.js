/**
 * 生产排程API
 */
import request from './request'

/**
 * 创建生产工单
 * @param {Object} data - 生产工单数据
 */
export const createProductionOrder = (data) => {
  return request({
    url: '/production/',
    method: 'post',
    data
  })
}

/**
 * 获取生产工单列表
 * @param {Object} params - 查询参数
 */
export const getProductionList = (params) => {
  return request({
    url: '/production/',
    method: 'get',
    params
  })
}

/**
 * 获取生产工单详情
 * @param {Number} id - 生产工单ID
 */
export const getProductionDetail = (id) => {
  return request({
    url: `/production/${id}`,
    method: 'get'
  })
}

/**
 * 更新生产工单
 * @param {Number} id - 生产工单ID
 * @param {Object} data - 更新数据
 */
export const updateProduction = (id, data) => {
  return request({
    url: `/production/${id}`,
    method: 'put',
    data
  })
}

/**
 * 开始生产
 * @param {Number} id - 生产工单ID
 * @param {String} operatorName - 操作员姓名
 */
export const startProduction = (id, operatorName) => {
  return request({
    url: `/production/${id}/start`,
    method: 'post',
    params: { operator_name: operatorName }
  })
}

/**
 * 完成生产
 * @param {Number} id - 生产工单ID
 * @param {String} operatorName - 操作员姓名
 */
export const completeProduction = (id, operatorName) => {
  return request({
    url: `/production/${id}/complete`,
    method: 'post',
    params: { operator_name: operatorName }
  })
}

/**
 * 取消生产工单
 * @param {Number} id - 生产工单ID
 * @param {String} reason - 取消原因
 */
export const cancelProduction = (id, reason) => {
  return request({
    url: `/production/${id}/cancel`,
    method: 'post',
    params: { reason }
  })
}

/**
 * 创建生产报工
 * @param {Object} data - 报工数据
 */
export const createProductionReport = (data) => {
  return request({
    url: '/production/reports/',
    method: 'post',
    data
  })
}

/**
 * 获取生产报工记录
 * @param {Number} productionId - 生产工单ID
 */
export const getProductionReports = (productionId) => {
  return request({
    url: `/production/${productionId}/reports/`,
    method: 'get'
  })
}

/**
 * 获取生产统计
 */
export const getProductionStatistics = () => {
  return request({
    url: '/production/statistics/summary',
    method: 'get'
  })
}
