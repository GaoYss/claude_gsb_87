<script setup>
import { onMounted, ref, watch } from 'vue'

import { deleteReservoir, fetchReservoirs } from '@/api/reservoirs'
import DataTable from '@/components/common/DataTable.vue'
import PaginationBar from '@/components/common/PaginationBar.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import ReservoirFilterBar from '@/components/reservoir/ReservoirFilterBar.vue'
import { useListQuery } from '@/composables/useListQuery'
import { useConfirmStore } from '@/stores/confirm'
import { useDictionaryStore } from '@/stores/dictionary'
import { useToastStore } from '@/stores/toast'
import { formatDateTime, formatNumber } from '@/utils/format'

const dictionary = useDictionaryStore()
const toast = useToastStore()
const confirm = useConfirmStore()

const { filters, page, pageSize, syncQuery, reset } = useListQuery({
  keyword: '',
  region: '',
  status: '',
  safety_class: '',
})

const rows = ref([])
const total = ref(0)
const pages = ref(0)
const loading = ref(false)

const columns = [
  { key: 'code', label: '水库编码', width: '130px' },
  { key: 'name', label: '水库名称', width: '150px' },
  { key: 'region', label: '行政区', width: '100px' },
  { key: 'dam_type', label: '坝型', width: '110px' },
  { key: 'total_capacity', label: '总库容(万m³)', width: '120px' },
  { key: 'safety_class', label: '安全类别', width: '100px' },
  { key: 'status', label: '运行状态', width: '110px' },
  { key: 'last_inspected_at', label: '最近巡查', width: '160px' },
  { key: 'open_hazard_count', label: '未销号隐患', width: '110px' },
  { key: 'actions', label: '操作', width: '150px' },
]

async function load() {
  loading.value = true
  try {
    const data = await fetchReservoirs({
      ...filters.value,
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
  const ok = await confirm.ask(`确认删除水库「${row.name}」？删除后不可恢复。`)
  if (!ok) return
  try {
    await deleteReservoir(row.id)
    toast.success('水库已删除')
    if (rows.value.length === 1 && page.value > 1) page.value -= 1
    else load()
  } catch (error) {
    toast.error(error.message)
  }
}
</script>

<template>
  <div>
    <PageHeader title="水库台账" description="维护水库工程基本信息、安全类别与运行状态">
      <template #actions>
        <RouterLink class="btn btn-primary" to="/reservoirs/new">新增水库</RouterLink>
      </template>
    </PageHeader>

    <ReservoirFilterBar v-model="filters" @reset="resetFilters" />

    <section class="card">
      <DataTable :columns="columns" :rows="rows" :loading="loading" empty-text="没有符合条件的水库">
        <template #code="{ row }">
          <RouterLink class="mono" :to="`/reservoirs/${row.id}`">{{ row.code }}</RouterLink>
        </template>
        <template #name="{ row }">
          <RouterLink :to="`/reservoirs/${row.id}`">{{ row.name }}</RouterLink>
        </template>
        <template #dam_type="{ row }">{{ dictionary.labelOf('dam_type', row.dam_type) }}</template>
        <template #total_capacity="{ row }">{{ formatNumber(row.total_capacity) }}</template>
        <template #safety_class="{ row }">
          <StatusTag kind="safety_class" :value="row.safety_class" />
        </template>
        <template #status="{ row }">
          <StatusTag kind="reservoir_status" :value="row.status" />
        </template>
        <template #last_inspected_at="{ row }">
          {{ row.last_inspected_at ? formatDateTime(row.last_inspected_at) : '尚未巡查' }}
        </template>
        <template #open_hazard_count="{ row }">
          <RouterLink
            v-if="row.open_hazard_count"
            :to="{ name: 'hazard-list', query: { reservoir_id: row.id, open_only: 'true' } }"
          >
            {{ row.open_hazard_count }} 条
          </RouterLink>
          <span v-else class="muted">0</span>
        </template>
        <template #actions="{ row }">
          <div class="cell-actions">
            <RouterLink class="btn-link" :to="`/reservoirs/${row.id}`">详情</RouterLink>
            <RouterLink class="btn-link" :to="`/reservoirs/${row.id}/edit`">编辑</RouterLink>
            <button class="btn-link danger" type="button" @click="remove(row)">删除</button>
          </div>
        </template>
      </DataTable>
      <PaginationBar
        v-model:page="page"
        v-model:page-size="pageSize"
        :total="total"
        :pages="pages"
      />
    </section>
  </div>
</template>

