/**
 * 财务报表API
 */
import request from './request'

/**
 * 获取财务概览
 */
export const getFinancialOverview = () => {
  return request({
    url: '/reports/overview',
    method: 'get'
  })
}

/**
 * 获取收款日报
 * @param {string} startDate - 开始日期 YYYY-MM-DD
 * @param {string} endDate - 结束日期 YYYY-MM-DD
 */
export const getDailyPaymentReport = (startDate, endDate) => {
  return request({
    url: '/reports/payments/daily',
    method: 'get',
    params: { start_date: startDate, end_date: endDate }
  })
}

/**
 * 获取收款月报
 * @param {number} year - 年份
 * @param {number} month - 月份
 */
export const getMonthlyPaymentReport = (year, month) => {
  return request({
    url: '/reports/payments/monthly',
    method: 'get',
    params: { year, month }
  })
}

/**
 * 获取客户欠款统计
 */
export const getCustomerReceivables = () => {
  return request({
    url: '/reports/receivables/customers',
    method: 'get'
  })
}

/**
 * 获取销售收款趋势
 * @param {number} days - 天数，默认30天
 */
export const getSalesPaymentTrend = (days = 30) => {
  return request({
    url: '/reports/trends/sales-payment',
    method: 'get',
    params: { days }
  })
}

/**
 * 获取应收账款账龄分析
 */
export const getReceivablesAging = () => {
  return request({
    url: '/reports/receivables/aging',
    method: 'get'
  })
}
