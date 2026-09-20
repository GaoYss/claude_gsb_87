/** 展示层格式化工具，全部基于本地时间，避免时区偏移。 */

function pad(value) {
  return String(value).padStart(2, '0')
}

export function formatDateTime(value) {
  if (!value) return '—'
  const text = String(value)
  return text.length >= 16 ? text.slice(0, 16).replace('T', ' ') : text
}

export function formatDate(value) {
  if (!value) return '—'
  return String(value).slice(0, 10)
}

export function formatNumber(value, digits = 2) {
  if (value === null || value === undefined || value === '') return '—'
  const number = Number(value)
  if (Number.isNaN(number)) return String(value)
  return number.toFixed(digits)
}

export function todayString() {
  const now = new Date()
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
}

export function nowForInput() {
  const now = new Date()
  return `${todayString()}T${pad(now.getHours())}:${pad(now.getMinutes())}`
}

export function toDateInput(value) {
  return value ? String(value).slice(0, 10) : ''
}

export function toDateTimeInput(value) {
  return value ? String(value).slice(0, 16) : ''
}

/** 日期范围查询：把 YYYY-MM-DD 补成当天的起止时间 */
export function startOfDay(dateString) {
  return dateString ? `${dateString}T00:00:00` : null
}

export function endOfDay(dateString) {
  return dateString ? `${dateString}T23:59:59` : null
}

/** 距离整改期限的天数，负数表示已逾期 */
export function daysUntil(dateString) {
  if (!dateString) return null
  const target = new Date(`${String(dateString).slice(0, 10)}T00:00:00`)
  if (Number.isNaN(target.getTime())) return null
  const now = new Date()
  const start = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  return Math.round((target - start) / 86400000)
}

export function deadlineHint(deadline, closed) {
  if (!deadline) return '未设置期限'
  if (closed) return `期限 ${formatDate(deadline)}`
  const days = daysUntil(deadline)
  if (days === null) return `期限 ${formatDate(deadline)}`
  if (days < 0) return `已逾期 ${Math.abs(days)} 天`
  if (days === 0) return '今天到期'
  return `剩余 ${days} 天`
}

