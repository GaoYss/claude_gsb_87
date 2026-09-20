import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { fetchOptions } from '@/api/meta'

/**
 * 后端下发的中文标签 / 下拉选项 / 隐患状态机。
 * 下拉值和标签只在后端维护一份，前端不再硬编码，避免前后端字典漂移。
 */
export const useDictionaryStore = defineStore('dictionary', () => {
  const dicts = ref({})
  const regions = ref([])
  const hazardTransitions = ref({})
  const loading = ref(false)
  const loaded = ref(false)

  const dictKeys = computed(() => Object.keys(dicts.value))

  async function load(force = false) {
    if (loaded.value && !force) return
    if (loading.value) return
    loading.value = true
    try {
      const data = await fetchOptions()
      dicts.value = data.dicts || {}
      regions.value = data.regions || []
      hazardTransitions.value = data.hazard_transitions || {}
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  function options(key) {
    return dicts.value[key] || []
  }

  function labelOf(key, value) {
    if (value === null || value === undefined || value === '') return '—'
    const hit = options(key).find((item) => item.value === value)
    return hit ? hit.label : String(value)
  }

  function transitionsFor(status) {
    return hazardTransitions.value[status] || []
  }

  return {
    dicts,
    dictKeys,
    regions,
    hazardTransitions,
    loading,
    loaded,
    load,
    options,
    labelOf,
    transitionsFor,
  }
})

