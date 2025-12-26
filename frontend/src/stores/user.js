/**
 * 用户Store - 管理用户登录状态和信息
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const userInfo = ref(null)
  const tokenValidated = ref(false) // 标记token是否已验证

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
        tokenValidated.value = true // 登录成功后标记token已验证
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
    tokenValidated.value = false
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

  // 验证token是否有效
  async function validateToken() {
    if (!token.value) {
      return false
    }

    // 如果已经验证过，直接返回true
    if (tokenValidated.value) {
      return true
    }

    try {
      // 尝试调用一个需要认证的API来验证token
      const response = await fetch('http://localhost:8000/api/v1/materials/?page=1&page_size=1', {
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      })

      if (response.status === 401) {
        // Token无效，清除登录状态
        console.warn('Token已过期或无效')
        logout()
        return false
      }

      if (response.ok) {
        tokenValidated.value = true
        return true
      }

      return false
    } catch (error) {
      console.error('验证token失败:', error)
      return false
    }
  }

  return {
    token,
    userInfo,
    tokenValidated,
    loginAction,
    logout,
    restoreUserInfo,
    validateToken
  }
})
