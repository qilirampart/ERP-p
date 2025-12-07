/**
 * 物料管理API
 */
import request from './request'

/**
 * 获取物料列表
 */
export function getMaterialList(params) {
  return request({
    url: '/api/v1/materials/',
    method: 'get',
    params
  })
}

/**
 * 获取物料详情
 */
export function getMaterialDetail(id) {
  return request({
    url: `/api/v1/materials/${id}`,
    method: 'get'
  })
}

/**
 * 创建物料
 */
export function createMaterial(data) {
  return request({
    url: '/api/v1/materials/',
    method: 'post',
    data
  })
}

/**
 * 更新物料
 */
export function updateMaterial(id, data) {
  return request({
    url: `/api/v1/materials/${id}`,
    method: 'put',
    data
  })
}

/**
 * 入库操作
 */
export function stockIn(data) {
  return request({
    url: '/api/v1/materials/stock-in',
    method: 'post',
    data
  })
}

/**
 * 出库操作
 */
export function stockOut(data) {
  return request({
    url: '/api/v1/materials/stock-out',
    method: 'post',
    data
  })
}
