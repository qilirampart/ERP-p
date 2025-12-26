import request from './request'

/**
 * 下载销售订单PDF
 */
export const downloadOrderPDF = (orderId) => {
  return request({
    url: `/print/order/${orderId}`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 下载生产工单PDF
 */
export const downloadProductionPDF = (productionId) => {
  return request({
    url: `/print/production/${productionId}`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 下载送货单PDF
 */
export const downloadDeliveryPDF = (orderId) => {
  return request({
    url: `/print/delivery/${orderId}`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 下载收款凭证PDF
 */
export const downloadPaymentReceiptPDF = (paymentId) => {
  return request({
    url: `/print/payment/${paymentId}`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 下载文件工具函数
 */
export const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(new Blob([blob]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
