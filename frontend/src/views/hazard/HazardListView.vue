<script setup>
import { onMounted, ref, watch } from 'vue'

import { deleteHazard, fetchHazards } from '@/api/hazards'
import DataTable from '@/components/common/DataTable.vue'
import PaginationBar from '@/components/common/PaginationBar.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import HazardFilterBar from '@/components/hazard/HazardFilterBar.vue'
import { useListQuery } from '@/composables/useListQuery'
import { useConfirmStore } from '@/stores/confirm'
import { useDictionaryStore } from '@/stores/dictionary'
import { useToastStore } from '@/stores/toast'
import { deadlineHint, formatDate } from '@/utils/format'

const dictionary = useDictionaryStore()
const toast = useToastStore()
const confirm = useConfirmStore()

const { filters, page, pageSize, syncQuery, reset } = useListQuery({
  keyword: '',
  reservoir_id: '',
  category: '',
  severity: '',
  status: '',
  overdue_only: false,
  open_only: false,
})

const rows = ref([])
const total = ref(0)
const pages = ref(0)
const loading = ref(false)

const columns = [
  { key: 'code', label: '隐患编号', width: '150px' },
  { key: 'title', label: '隐患标题' },
  { key: 'reservoir', label: '水库', width: '140px' },
  { key: 'category', label: '类别', width: '100px' },
  { key: 'severity', label: '等级', width: '110px' },
  { key: 'status', label: '整改状态', width: '110px' },
  { key: 'discovered_on', label: '发现日期', width: '120px' },
  { key: 'deadline', label: '整改期限', width: '170px' },
  { key: 'actions', label: '操作', width: '150px' },
]

async function load() {
  loading.value = true
  try {
    const data = await fetchHazards({
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
  const ok = await confirm.ask(`确认删除隐患「${row.title}」？关联的整改跟踪记录会一并删除。`)
  if (!ok) return
  try {
    await deleteHazard(row.id)
    toast.success('隐患已删除')
    if (rows.value.length === 1 && page.value > 1) page.value -= 1
    else load()
  } catch (error) {
    toast.error(error.message)
  }
}
</script>

<template>
  <div>
    <PageHeader title="隐患与整改" description="登记巡查发现的隐患，跟踪整改与验收销号全过程">
      <template #actions>
        <RouterLink class="btn btn-primary" to="/hazards/new">登记隐患</RouterLink>
      </template>
    </PageHeader>

    <HazardFilterBar v-model="filters" @reset="resetFilters" />

    <section class="card">
      <DataTable :columns="columns" :rows="rows" :loading="loading" empty-text="没有符合条件的隐患">
        <template #code="{ row }">
          <RouterLink class="mono" :to="`/hazards/${row.id}`">{{ row.code }}</RouterLink>
        </template>
        <template #title="{ row }">
          <RouterLink :to="`/hazards/${row.id}`">{{ row.title }}</RouterLink>
        </template>
        <template #reservoir="{ row }">
          <RouterLink v-if="row.reservoir" :to="`/reservoirs/${row.reservoir.id}`">
            {{ row.reservoir.name }}
          </RouterLink>
          <span v-else class="muted">—</span>
        </template>
        <template #category="{ row }">{{ dictionary.labelOf('structure_part', row.category) }}</template>
        <template #severity="{ row }">
          <StatusTag kind="hazard_severity" :value="row.severity" />
        </template>
        <template #status="{ row }">
          <StatusTag kind="hazard_status" :value="row.status" />
        </template>
        <template #discovered_on="{ row }">{{ formatDate(row.discovered_on) }}</template>
        <template #deadline="{ row }">
          <span class="nowrap">{{ formatDate(row.deadline) }}</span>
          <span v-if="row.is_overdue" class="tag tag-overdue" style="margin-left: 6px">逾期</span>
          <div class="timeline-meta">{{ deadlineHint(row.deadline, row.status === 'closed') }}</div>
        </template>
        <template #actions="{ row }">
          <div class="cell-actions">
            <RouterLink class="btn-link" :to="`/hazards/${row.id}`">跟踪</RouterLink>
            <RouterLink class="btn-link" :to="`/hazards/${row.id}/edit`">编辑</RouterLink>
            <button class="btn-link danger" type="button" @click="remove(row)">删除</button>
          </div>
        </template>
      </DataTable>
      <PaginationBar v-model:page="page" v-model:page-size="pageSize" :total="total" :pages="pages" />
    </section>
  </div>
</template>

