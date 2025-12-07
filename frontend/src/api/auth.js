/**
 * 认证相关API
 */
import request from './request'

/**
 * 用户登录
 */
export function login(data) {
  return request({
    url: '/api/v1/auth/login',
    method: 'post',
    data
  })
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser() {
  return request({
    url: '/api/v1/auth/me',
    method: 'get'
  })
}
