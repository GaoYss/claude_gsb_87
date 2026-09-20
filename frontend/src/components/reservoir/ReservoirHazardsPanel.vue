<script setup>
import { onMounted, ref } from 'vue'

import { fetchHazards } from '@/api/hazards'
import BaseCard from '@/components/common/BaseCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import { useDictionaryStore } from '@/stores/dictionary'
import { useToastStore } from '@/stores/toast'
import { deadlineHint, formatDate } from '@/utils/format'

const props = defineProps({
  reservoirId: { type: [Number, String], required: true },
})

const dictionary = useDictionaryStore()
const toast = useToastStore()

const rows = ref([])
const loading = ref(true)

const columns = [
  { key: 'code', label: '隐患编号', width: '150px' },
  { key: 'title', label: '隐患标题' },
  { key: 'category', label: '类别', width: '110px' },
  { key: 'severity', label: '等级', width: '110px' },
  { key: 'status', label: '状态', width: '110px' },
  { key: 'deadline', label: '整改期限', width: '150px' },
]

onMounted(async () => {
  try {
    const page = await fetchHazards({ reservoir_id: props.reservoirId, page_size: 8 })
    rows.value = page.items
  } catch (error) {
    toast.error(error.message)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <BaseCard title="该水库的隐患台账" subtitle="最近 8 条">
    <template #actions>
      <RouterLink class="btn btn-sm" :to="{ name: 'hazard-list', query: { reservoir_id: reservoirId } }">
        查看全部
      </RouterLink>
      <RouterLink
        class="btn btn-sm btn-primary"
        :to="{ name: 'hazard-create', query: { reservoir_id: reservoirId } }"
      >
        登记隐患
      </RouterLink>
    </template>
    <DataTable
      v-if="loading || rows.length"
      :columns="columns"
      :rows="rows"
      :loading="loading"
      empty-text="该水库暂无隐患记录"
    >
      <template #code="{ row }">
        <RouterLink class="mono" :to="`/hazards/${row.id}`">{{ row.code }}</RouterLink>
      </template>
      <template #category="{ row }">{{ dictionary.labelOf('structure_part', row.category) }}</template>
      <template #severity="{ row }">
        <StatusTag kind="hazard_severity" :value="row.severity" />
      </template>
      <template #status="{ row }">
        <StatusTag kind="hazard_status" :value="row.status" />
      </template>
      <template #deadline="{ row }">
        <span>{{ formatDate(row.deadline) }}</span>
        <span v-if="row.is_overdue" class="muted"> · {{ deadlineHint(row.deadline, false) }}</span>
      </template>
    </DataTable>
    <EmptyState v-else title="该水库暂无隐患记录" description="可点击右上角登记隐患" />
  </BaseCard>
</template>

