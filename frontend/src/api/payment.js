/**
 * 收款管理API
 */
import request from './request'

/**
 * 创建收款记录
 * @param {Object} data - 收款数据
 */
export const createPayment = (data) => {
  return request({
    url: '/payments/',
    method: 'post',
    data
  })
}

/**
 * 获取收款记录列表
 * @param {Object} params - 查询参数
 */
export const getPaymentList = (params) => {
  return request({
    url: '/payments/',
    method: 'get',
    params
  })
}

/**
 * 获取收款记录详情
 * @param {Number} id - 收款记录ID
 */
export const getPaymentDetail = (id) => {
  return request({
    url: `/payments/${id}`,
    method: 'get'
  })
}

/**
 * 更新收款记录
 * @param {Number} id - 收款记录ID
 * @param {Object} data - 更新数据
 */
export const updatePayment = (id, data) => {
  return request({
    url: `/payments/${id}`,
    method: 'put',
    data
  })
}

/**
 * 取消收款记录
 * @param {Number} id - 收款记录ID
 * @param {String} reason - 取消原因
 */
export const cancelPayment = (id, reason) => {
  return request({
    url: `/payments/${id}/cancel`,
    method: 'post',
    params: { reason }
  })
}

/**
 * 获取订单收款汇总
 * @param {Number} orderId - 订单ID
 */
export const getOrderPaymentSummary = (orderId) => {
  return request({
    url: `/payments/orders/${orderId}/summary`,
    method: 'get'
  })
}

/**
 * 获取收款统计
 */
export const getPaymentStatistics = () => {
  return request({
    url: '/payments/statistics/summary',
    method: 'get'
  })
}
