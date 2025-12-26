/**
 * 客户管理API
 */
import request from './request'

/**
 * 获取客户列表
 * @param {Object} params - 查询参数
 * @param {string} params.keyword - 搜索关键词（客户名称/编码/联系人/电话）
 * @param {string} params.status - 客户状态筛选（ACTIVE/INACTIVE）
 * @param {string} params.customer_level - 客户等级筛选（A/B/C/D）
 * @param {number} params.skip - 跳过记录数
 * @param {number} params.limit - 返回记录数
 */
export function getCustomerList(params) {
  return request({
    url: '/customers/',
    method: 'get',
    params
  })
}

/**
 * 获取客户详情
 * @param {number} id - 客户ID
 */
export function getCustomerDetail(id) {
  return request({
    url: `/customers/${id}`,
    method: 'get'
  })
}

/**
 * 创建客户
 * @param {Object} data - 客户数据
 */
export function createCustomer(data) {
  return request({
    url: '/customers/',
    method: 'post',
    data
  })
}

/**
 * 更新客户信息
 * @param {number} id - 客户ID
 * @param {Object} data - 更新数据
 */
export function updateCustomer(id, data) {
  return request({
    url: `/customers/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除客户
 * @param {number} id - 客户ID
 */
export function deleteCustomer(id) {
  return request({
    url: `/customers/${id}`,
    method: 'delete'
  })
}

/**
 * 获取客户统计信息
 * @param {number} id - 客户ID
 */
export function getCustomerStatistics(id) {
  return request({
    url: `/customers/${id}/statistics`,
    method: 'get'
  })
}

/**
 * 获取客户历史订单
 * @param {number} id - 客户ID
 * @param {Object} params - 分页参数
 * @param {number} params.skip - 跳过记录数
 * @param {number} params.limit - 返回记录数
 */
export function getCustomerOrders(id, params) {
  return request({
    url: `/customers/${id}/orders`,
    method: 'get',
    params
  })
}
