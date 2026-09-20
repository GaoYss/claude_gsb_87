<script setup>
import { onMounted, ref } from 'vue'

import { fetchInspections } from '@/api/inspections'
import BaseCard from '@/components/common/BaseCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import { useDictionaryStore } from '@/stores/dictionary'
import { useToastStore } from '@/stores/toast'
import { formatDateTime, formatNumber } from '@/utils/format'

const props = defineProps({
  reservoirId: { type: [Number, String], required: true },
})

const dictionary = useDictionaryStore()
const toast = useToastStore()

const rows = ref([])
const loading = ref(true)

const columns = [
  { key: 'code', label: '巡查编号', width: '150px' },
  { key: 'inspected_at', label: '巡查时间', width: '160px' },
  { key: 'inspect_type', label: '类型', width: '110px' },
  { key: 'inspector', label: '巡查人', width: '100px' },
  { key: 'water_level', label: '水位(m)', width: '90px' },
  { key: 'status', label: '结论', width: '110px' },
]

onMounted(async () => {
  try {
    const page = await fetchInspections({ reservoir_id: props.reservoirId, page_size: 8 })
    rows.value = page.items
  } catch (error) {
    toast.error(error.message)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <BaseCard title="该水库的巡查记录" subtitle="最近 8 次">
    <template #actions>
      <RouterLink class="btn btn-sm" :to="{ name: 'inspection-list', query: { reservoir_id: reservoirId } }">
        查看全部
      </RouterLink>
      <RouterLink
        class="btn btn-sm btn-primary"
        :to="{ name: 'inspection-create', query: { reservoir_id: reservoirId } }"
      >
        录入巡查记录
      </RouterLink>
    </template>
    <DataTable
      v-if="loading || rows.length"
      :columns="columns"
      :rows="rows"
      :loading="loading"
      empty-text="该水库暂无巡查记录"
    >
      <template #code="{ row }">
        <RouterLink class="mono" :to="`/inspections/${row.id}`">{{ row.code }}</RouterLink>
      </template>
      <template #inspected_at="{ row }">{{ formatDateTime(row.inspected_at) }}</template>
      <template #inspect_type="{ row }">
        {{ dictionary.labelOf('inspection_type', row.inspect_type) }}
      </template>
      <template #water_level="{ row }">{{ formatNumber(row.water_level, 2) }}</template>
      <template #status="{ row }">
        <StatusTag kind="inspection_status" :value="row.status" />
      </template>
    </DataTable>
    <EmptyState v-else title="该水库暂无巡查记录" description="可点击右上角录入第一条巡查记录" />
  </BaseCard>
</template>

