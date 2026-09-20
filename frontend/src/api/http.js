import axios from 'axios'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
})

/** 去掉空值参数，避免把 `?status=` 这种空条件传给后端 */
export function compact(params = {}) {
  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== null && value !== undefined && value !== ''),
  )
}

function extractMessage(data) {
  if (!data) return ''
  if (typeof data === 'string') return data
  if (typeof data.detail === 'string') return data.detail
  if (Array.isArray(data.detail)) {
    return data.detail
      .map((item) => {
        const field = Array.isArray(item.loc) ? item.loc.slice(1).join('.') : ''
        return field ? `${field}: ${item.msg}` : item.msg
      })
      .join('；')
  }
  return ''
}

function toAppError(error) {
  const appError = new Error('请求失败')
  if (error.response) {
    appError.status = error.response.status
    appError.message =
      extractMessage(error.response.data) || `请求失败（HTTP ${error.response.status}）`
  } else if (error.request) {
    appError.status = 0
    appError.message = '无法连接后端服务，请确认 API 已启动'
  } else {
    appError.status = -1
    appError.message = error.message
  }
  return appError
}

// 统一返回响应体，出错时抛出带 status 的 Error，视图层只需 catch 后提示
http.interceptors.response.use((response) => response.data, (error) => Promise.reject(toAppError(error)))

