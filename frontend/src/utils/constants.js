/** 标签配色：按字典类型 + 值映射到视觉语义。 */
export const TAG_TONES = {
  reservoir_status: {
    normal: 'ok',
    attention: 'warn',
    danger: 'danger',
    out_of_service: 'muted',
  },
  safety_class: {
    class_one: 'ok',
    class_two: 'info',
    class_three: 'danger',
  },
  inspection_status: {
    normal: 'ok',
    abnormal: 'danger',
  },
  item_result: {
    normal: 'ok',
    abnormal: 'danger',
  },
  hazard_status: {
    registered: 'warn',
    rectifying: 'info',
    pending_acceptance: 'accent',
    closed: 'ok',
  },
  hazard_severity: {
    general: 'muted',
    serious: 'warn',
    major: 'danger',
  },
  rectification_action: {
    register: 'muted',
    measure: 'info',
    progress: 'accent',
    verify: 'warn',
    close: 'ok',
  },
}

export const NAV_ITEMS = [
  { name: 'dashboard', label: '总览', path: '/dashboard' },
  { name: 'reservoirs', label: '水库台账', path: '/reservoirs' },
  { name: 'inspections', label: '巡查记录', path: '/inspections' },
  { name: 'hazards', label: '隐患与整改', path: '/hazards' },
]

