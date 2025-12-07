/**
 * 订单管理API
 */
import request from './request'

/**
 * 获取订单列表
 */
export function getOrderList(params) {
  return request({
    url: '/api/v1/orders/',
    method: 'get',
    params
  })
}

/**
 * 获取订单详情
 */
export function getOrderDetail(id) {
  return request({
    url: `/api/v1/orders/${id}`,
    method: 'get'
  })
}

/**
 * 创建订单
 */
export function createOrder(data) {
  return request({
    url: '/api/v1/orders/',
    method: 'post',
    data
  })
}

/**
 * 更新订单
 */
export function updateOrder(id, data) {
  return request({
    url: `/api/v1/orders/${id}`,
    method: 'put',
    data
  })
}

/**
 * 确认订单
 */
export function confirmOrder(id) {
  return request({
    url: `/api/v1/orders/${id}/confirm`,
    method: 'post'
  })
}

/**
 * 删除订单
 */
export function deleteOrder(id) {
  return request({
    url: `/api/v1/orders/${id}`,
    method: 'delete'
  })
}
