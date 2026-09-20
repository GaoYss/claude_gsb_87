<script setup>
import { ref, watch } from 'vue'

import { fetchInspections } from '@/api/inspections'
import { useDictionaryStore } from '@/stores/dictionary'
import { useToastStore } from '@/stores/toast'
import { formatDateTime } from '@/utils/format'

const model = defineModel({ type: [Number, String], default: null })

const props = defineProps({
  reservoirId: { type: [Number, String], default: null },
})

const dictionary = useDictionaryStore()
const toast = useToastStore()
const inspections = ref([])
const loading = ref(false)

// 隐患与巡查记录必须属于同一水库，因此水库变化时重新拉取候选巡查记录
watch(
  () => props.reservoirId,
  async (reservoirId, previous) => {
    if (previous !== undefined && reservoirId !== previous) model.value = null
    if (!reservoirId) {
      inspections.value = []
      return
    }
    loading.value = true
    try {
      const page = await fetchInspections({ reservoir_id: reservoirId, page_size: 50 })
      inspections.value = page.items
    } catch (error) {
      toast.error(error.message)
    } finally {
      loading.value = false
    }
  },
  { immediate: true },
)
</script>

<template>
  <select v-model="model" class="select" :disabled="!reservoirId || loading">
    <option :value="null">
      {{ !reservoirId ? '请先选择水库' : loading ? '加载中…' : '不关联巡查记录' }}
    </option>
    <option v-for="item in inspections" :key="item.id" :value="item.id">
      {{ formatDateTime(item.inspected_at) }} · {{ dictionary.labelOf('inspection_type', item.inspect_type) }} ·
      {{ item.code }}{{ item.status === 'abnormal' ? '（发现异常）' : '' }}
    </option>
  </select>
</template>

