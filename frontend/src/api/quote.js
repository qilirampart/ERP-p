/**
 * 报价计算API
 */
import request from './request'

/**
 * 计算报价
 */
export function calculateQuote(data) {
  return request({
    url: '/api/v1/quotes/calculate',
    method: 'post',
    data
  })
}
