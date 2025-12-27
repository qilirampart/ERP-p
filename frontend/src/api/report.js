/**
 * 财务报表API
 */
import request from './request'
import { exportExcel } from './excel'

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

// ==================== Excel导出 ====================

/**
 * 导出收款日报
 * @param {string} startDate - 开始日期 YYYY-MM-DD
 * @param {string} endDate - 结束日期 YYYY-MM-DD
 */
export function exportDailyPayments(startDate, endDate) {
  return exportExcel(
    '/reports/excel/daily-payments',
    { start_date: startDate, end_date: endDate },
    '收款日报.xlsx'
  )
}

/**
 * 导出客户欠款统计
 */
export function exportCustomerReceivables() {
  return exportExcel('/reports/excel/customer-receivables', {}, '客户欠款统计.xlsx')
}

/**
 * 导出应收账款账龄分析
 */
export function exportReceivablesAging() {
  return exportExcel('/reports/excel/receivables-aging', {}, '应收账款账龄分析.xlsx')
}

/**
 * 导出财务概览
 */
export function exportFinancialOverview() {
  return exportExcel('/reports/excel/financial-overview', {}, '财务概览.xlsx')
}
