/**
 * 订单管理API
 */
import request from './request'
import { exportExcel } from './excel'

/**
 * 获取订单列表
 */
export function getOrderList(params) {
  return request({
    url: '/orders/',
    method: 'get',
    params
  })
}

/**
 * 获取订单详情
 */
export function getOrderDetail(id) {
  return request({
    url: `/orders/${id}`,
    method: 'get'
  })
}

/**
 * 创建订单
 */
export function createOrder(data) {
  return request({
    url: '/orders/',
    method: 'post',
    data
  })
}

/**
 * 更新订单
 */
export function updateOrder(id, data) {
  return request({
    url: `/orders/${id}`,
    method: 'put',
    data
  })
}

/**
 * 确认订单
 */
export function confirmOrder(id) {
  return request({
    url: `/orders/${id}/confirm`,
    method: 'post'
  })
}

/**
 * 删除订单
 */
export function deleteOrder(id) {
  return request({
    url: `/orders/${id}`,
    method: 'delete'
  })
}

// ==================== Excel导出 ====================

/**
 * 导出订单数据
 * @param {Object} params - 筛选参数
 * @param {string} params.status - 订单状态
 * @param {string} params.customer_name - 客户名称
 * @param {string} params.start_date - 开始日期(YYYY-MM-DD)
 * @param {string} params.end_date - 结束日期(YYYY-MM-DD)
 */
export function exportOrders(params = {}) {
  return exportExcel('/orders/excel/export', params, '订单数据.xlsx')
}
