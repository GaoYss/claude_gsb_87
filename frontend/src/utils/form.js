/** 表单值清洗：把空串转成 null，数字字段转成数值。 */

export function nullify(value) {
  if (value === '' || value === undefined) return null
  return value
}

export function toNumberOrNull(value) {
  if (value === '' || value === null || value === undefined) return null
  const number = Number(value)
  return Number.isNaN(number) ? null : number
}

export function trimOrNull(value) {
  if (value === null || value === undefined) return null
  const text = String(value).trim()
  return text === '' ? null : text
}

/**
 * 按字段类型清洗提交数据：numberFields 转数值、其余空串转 null、文本去空格。
 */
export function cleanPayload(source, { numberFields = [], intFields = [], textFields = [] } = {}) {
  const payload = { ...source }
  for (const key of numberFields) payload[key] = toNumberOrNull(payload[key])
  for (const key of intFields) {
    const value = toNumberOrNull(payload[key])
    payload[key] = value === null ? null : Math.trunc(value)
  }
  for (const key of textFields) payload[key] = trimOrNull(payload[key])
  for (const key of Object.keys(payload)) {
    if (payload[key] === '') payload[key] = null
  }
  return payload
}

