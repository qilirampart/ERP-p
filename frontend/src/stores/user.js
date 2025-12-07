/**
 * 用户Store - 管理用户登录状态和信息
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const userInfo = ref(null)

  // 登录
  async function loginAction(username, password) {
    try {
      const response = await login({ username, password })
      if (response.code === 200) {
        token.value = response.data.access_token
        userInfo.value = {
          id: response.data.user_id,
          username: response.data.username,
          role: response.data.role
        }
        localStorage.setItem('access_token', response.data.access_token)
        localStorage.setItem('user_info', JSON.stringify(userInfo.value))
        return true
      }
      return false
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  // 登出
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
  }

  // 从localStorage恢复用户信息
  function restoreUserInfo() {
    const savedUserInfo = localStorage.getItem('user_info')
    if (savedUserInfo) {
      try {
        userInfo.value = JSON.parse(savedUserInfo)
      } catch (e) {
        console.error('恢复用户信息失败:', e)
      }
    }
  }

  return {
    token,
    userInfo,
    loginAction,
    logout,
    restoreUserInfo
  }
})
