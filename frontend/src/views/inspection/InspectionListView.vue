<script setup>
import { onMounted, ref, watch } from 'vue'

import { deleteInspection, fetchInspections } from '@/api/inspections'
import DataTable from '@/components/common/DataTable.vue'
import PaginationBar from '@/components/common/PaginationBar.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import InspectionFilterBar from '@/components/inspection/InspectionFilterBar.vue'
import { useListQuery } from '@/composables/useListQuery'
import { useConfirmStore } from '@/stores/confirm'
import { useDictionaryStore } from '@/stores/dictionary'
import { useToastStore } from '@/stores/toast'
import { endOfDay, formatDateTime, formatNumber, startOfDay } from '@/utils/format'

const dictionary = useDictionaryStore()
const toast = useToastStore()
const confirm = useConfirmStore()

const { filters, page, pageSize, syncQuery, reset } = useListQuery({
  keyword: '',
  reservoir_id: '',
  inspect_type: '',
  status: '',
  date_from: '',
  date_to: '',
})

const rows = ref([])
const total = ref(0)
const pages = ref(0)
const loading = ref(false)

const columns = [
  { key: 'code', label: '巡查编号', width: '150px' },
  { key: 'reservoir', label: '水库', width: '150px' },
  { key: 'inspect_type', label: '巡查类型', width: '110px' },
  { key: 'inspected_at', label: '巡查时间', width: '160px' },
  { key: 'inspector', label: '巡查人', width: '100px' },
  { key: 'weather', label: '天气', width: '100px' },
  { key: 'water_level', label: '水位(m)', width: '90px' },
  { key: 'status', label: '结论', width: '110px' },
  { key: 'actions', label: '操作', width: '150px' },
]

async function load() {
  loading.value = true
  try {
    const data = await fetchInspections({
      ...filters.value,
      date_from: startOfDay(filters.value.date_from),
      date_to: endOfDay(filters.value.date_to),
      page: page.value,
      page_size: pageSize.value,
    })
    rows.value = data.items
    total.value = data.total
    pages.value = data.pages
  } catch (error) {
    toast.error(error.message)
  } finally {
    loading.value = false
  }
}

watch(
  [filters, page, pageSize],
  () => {
    syncQuery()
    load()
  },
  { deep: true },
)

onMounted(load)

function resetFilters() {
  reset()
  load()
}

async function remove(row) {
  const ok = await confirm.ask(`确认删除巡查记录「${row.code}」？删除后不可恢复。`)
  if (!ok) return
  try {
    await deleteInspection(row.id)
    toast.success('巡查记录已删除')
    if (rows.value.length === 1 && page.value > 1) page.value -= 1
    else load()
  } catch (error) {
    toast.error(error.message)
  }
}
</script>

<template>
  <div>
    <PageHeader title="巡查记录" description="按次记录水库日常、汛期、专项与应急巡查情况">
      <template #actions>
        <RouterLink class="btn btn-primary" to="/inspections/new">录入巡查记录</RouterLink>
      </template>
    </PageHeader>

    <InspectionFilterBar v-model="filters" @reset="resetFilters" />

    <section class="card">
      <DataTable
        :columns="columns"
        :rows="rows"
        :loading="loading"
        empty-text="没有符合条件的巡查记录"
      >
        <template #code="{ row }">
          <RouterLink class="mono" :to="`/inspections/${row.id}`">{{ row.code }}</RouterLink>
        </template>
        <template #reservoir="{ row }">
          <RouterLink v-if="row.reservoir" :to="`/reservoirs/${row.reservoir.id}`">
            {{ row.reservoir.name }}
          </RouterLink>
          <span v-else class="muted">—</span>
        </template>
        <template #inspect_type="{ row }">
          {{ dictionary.labelOf('inspection_type', row.inspect_type) }}
        </template>
        <template #inspected_at="{ row }">{{ formatDateTime(row.inspected_at) }}</template>
        <template #weather="{ row }">{{ dictionary.labelOf('weather', row.weather) }}</template>
        <template #water_level="{ row }">{{ formatNumber(row.water_level) }}</template>
        <template #status="{ row }">
          <StatusTag kind="inspection_status" :value="row.status" />
        </template>
        <template #actions="{ row }">
          <div class="cell-actions">
            <RouterLink class="btn-link" :to="`/inspections/${row.id}`">详情</RouterLink>
            <RouterLink class="btn-link" :to="`/inspections/${row.id}/edit`">编辑</RouterLink>
            <button class="btn-link danger" type="button" @click="remove(row)">删除</button>
          </div>
        </template>
      </DataTable>
      <PaginationBar v-model:page="page" v-model:page-size="pageSize" :total="total" :pages="pages" />
    </section>
  </div>
</template>

