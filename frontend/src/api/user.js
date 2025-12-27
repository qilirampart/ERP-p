/**
 * 用户管理API
 */
import request from './request'

/**
 * 获取用户列表
 * @param {number} skip - 跳过数量
 * @param {number} limit - 返回数量
 */
export const getUsers = (skip = 0, limit = 100) => {
  return request({
    url: '/users/',
    method: 'get',
    params: { skip, limit }
  })
}

/**
 * 获取用户详情
 * @param {number} userId - 用户ID
 */
export const getUser = (userId) => {
  return request({
    url: `/users/${userId}`,
    method: 'get'
  })
}

/**
 * 创建用户
 * @param {Object} userData - 用户数据
 * @param {string} userData.username - 用户名
 * @param {string} userData.password - 密码
 * @param {string} userData.role - 角色 (ADMIN/SALES/OPERATOR)
 * @param {boolean} userData.is_active - 是否激活
 */
export const createUser = (userData) => {
  return request({
    url: '/users/',
    method: 'post',
    data: userData
  })
}

/**
 * 更新用户
 * @param {number} userId - 用户ID
 * @param {Object} userData - 用户数据
 * @param {string} userData.password - 密码（可选）
 * @param {string} userData.role - 角色（可选）
 * @param {boolean} userData.is_active - 是否激活（可选）
 */
export const updateUser = (userId, userData) => {
  return request({
    url: `/users/${userId}`,
    method: 'put',
    data: userData
  })
}

/**
 * 删除用户
 * @param {number} userId - 用户ID
 */
export const deleteUser = (userId) => {
  return request({
    url: `/users/${userId}`,
    method: 'delete'
  })
}

/**
 * 修改当前用户密码
 * @param {Object} passwordData - 密码数据
 * @param {string} passwordData.old_password - 原密码
 * @param {string} passwordData.new_password - 新密码
 */
export const changePassword = (passwordData) => {
  return request({
    url: '/users/change-password',
    method: 'post',
    data: passwordData
  })
}
