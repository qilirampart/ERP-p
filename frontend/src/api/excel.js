/**
 * Excel导入导出通用工具
 */
import request from './request'
import axios from 'axios'

// 创建专门用于文件下载的axios实例（不使用响应拦截器）
const fileRequest = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 60000 // 文件下载可能需要更长时间
})

// 只添加请求拦截器来添加token
fileRequest.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * 下载文件通用方法
 * @param {Blob} blob - 文件Blob对象
 * @param {String} filename - 文件名
 */
export function downloadFile(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

/**
 * 从Content-Disposition响应头中提取文件名
 * @param {String} disposition - Content-Disposition响应头
 * @returns {String} 文件名
 */
export function getFilenameFromDisposition(disposition) {
  if (!disposition) return 'download.xlsx'

  // 尝试匹配 filename*=UTF-8''xxx 格式
  const filenameRegex = /filename\*=UTF-8''(.+)/i
  const matches = filenameRegex.exec(disposition)

  if (matches && matches[1]) {
    return decodeURIComponent(matches[1])
  }

  // 尝试匹配 filename="xxx" 格式
  const filenameRegex2 = /filename="(.+)"/i
  const matches2 = filenameRegex2.exec(disposition)

  if (matches2 && matches2[1]) {
    return matches2[1]
  }

  return 'download.xlsx'
}

/**
 * 下载Excel模板
 * @param {String} url - 模板下载URL
 * @param {String} defaultFilename - 默认文件名
 */
export async function downloadTemplate(url, defaultFilename = 'template.xlsx') {
  try {
    const response = await fileRequest.get(url, { responseType: 'blob' })

    // 从响应头获取文件名
    const disposition = response.headers['content-disposition']
    const filename = getFilenameFromDisposition(disposition) || defaultFilename

    downloadFile(response.data, filename)
    return { success: true }
  } catch (error) {
    console.error('下载模板失败:', error)
    throw error
  }
}

/**
 * 导出Excel数据
 * @param {String} url - 导出URL
 * @param {Object} params - 查询参数
 * @param {String} defaultFilename - 默认文件名
 */
export async function exportExcel(url, params = {}, defaultFilename = 'export.xlsx') {
  try {
    const response = await fileRequest.get(url, {
      params,
      responseType: 'blob'
    })

    // 检查是否是JSON错误响应
    if (response.data.type === 'application/json') {
      const text = await response.data.text()
      const error = JSON.parse(text)
      throw new Error(error.detail || '导出失败')
    }

    // 从响应头获取文件名
    const disposition = response.headers['content-disposition']
    const filename = getFilenameFromDisposition(disposition) || defaultFilename

    downloadFile(response.data, filename)
    return { success: true, filename }
  } catch (error) {
    console.error('导出Excel失败:', error)
    throw error
  }
}

/**
 * 导入Excel数据
 * @param {String} url - 导入URL
 * @param {File} file - Excel文件对象
 * @param {Object} additionalData - 额外的表单数据
 */
export async function importExcel(url, file, additionalData = {}) {
  try {
    const formData = new FormData()
    formData.append('file', file)

    // 添加额外数据
    Object.keys(additionalData).forEach(key => {
      formData.append(key, additionalData[key])
    })

    const response = await request.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    return response.data
  } catch (error) {
    console.error('导入Excel失败:', error)
    throw error
  }
}
