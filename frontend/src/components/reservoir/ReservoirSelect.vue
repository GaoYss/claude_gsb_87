<script setup>
import { onMounted, ref } from 'vue'

import { fetchReservoirs } from '@/api/reservoirs'
import { useToastStore } from '@/stores/toast'

const model = defineModel({ type: [Number, String], default: null })

defineProps({
  placeholder: { type: String, default: '请选择水库' },
  allowAll: { type: Boolean, default: false },
  allowEmpty: { type: Boolean, default: false },
})

const toast = useToastStore()
const reservoirs = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const page = await fetchReservoirs({ page_size: 100 })
    reservoirs.value = page.items
  } catch (error) {
    toast.error(error.message)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <select v-model="model" class="select" :disabled="loading">
    <option v-if="allowAll" :value="''">全部水库</option>
    <option v-else :value="null">{{ loading ? '加载中…' : placeholder }}</option>
    <option v-for="item in reservoirs" :key="item.id" :value="item.id">
      {{ item.name }}（{{ item.code }}）
    </option>
  </select>
</template>

