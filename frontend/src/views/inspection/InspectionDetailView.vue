<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { fetchHazards } from '@/api/hazards'
import { deleteInspection, fetchInspection } from '@/api/inspections'
import BaseCard from '@/components/common/BaseCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import InspectionItemsTable from '@/components/inspection/InspectionItemsTable.vue'
import { useConfirmStore } from '@/stores/confirm'
import { useDictionaryStore } from '@/stores/dictionary'
import { useToastStore } from '@/stores/toast'
import { formatDateTime, formatNumber } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const toast = useToastStore()
const confirm = useConfirmStore()
const dictionary = useDictionaryStore()

const inspection = ref(null)
const hazards = ref([])
const loading = ref(true)

const hazardColumns = [
  { key: 'code', label: '隐患编号', width: '150px' },
  { key: 'title', label: '隐患标题' },
  { key: 'severity', label: '等级', width: '110px' },
  { key: 'status', label: '状态', width: '110px' },
]

async function load() {
  loading.value = true
  try {
    const detail = await fetchInspection(route.params.id)
    inspection.value = detail
    const related = await fetchHazards({ inspection_id: detail.id, page_size: 20 })
    hazards.value = related.items
  } catch (error) {
    toast.error(error.message)
    router.replace({ name: 'inspection-list' })
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function remove() {
  const ok = await confirm.ask(`确认删除巡查记录「${inspection.value.code}」？`)
  if (!ok) return
  try {
    await deleteInspection(inspection.value.id)
    toast.success('巡查记录已删除')
    router.replace({ name: 'inspection-list' })
  } catch (error) {
    toast.error(error.message)
  }
}
</script>

<template>
  <div v-if="loading" class="muted">加载中…</div>
  <div v-else-if="inspection">
    <PageHeader
      :title="inspection.code"
      :description="`${inspection.reservoir?.name || '未知水库'} · ${formatDateTime(inspection.inspected_at)}`"
    >
      <template #badge>
        <StatusTag kind="inspection_status" :value="inspection.status" />
      </template>
      <template #actions>
        <RouterLink class="btn" :to="`/inspections/${inspection.id}/edit`">编辑</RouterLink>
        <RouterLink
          class="btn"
          :to="{
            name: 'hazard-create',
            query: { reservoir_id: inspection.reservoir_id, inspection_id: inspection.id },
          }"
        >
          登记隐患
        </RouterLink>
        <button class="btn btn-danger" type="button" @click="remove">删除</button>
      </template>
    </PageHeader>

    <BaseCard title="巡查基本信息">
      <dl class="def-list">
        <div class="def-item">
          <dt>所属水库</dt>
          <dd>
            <RouterLink :to="`/reservoirs/${inspection.reservoir_id}`">
              {{ inspection.reservoir?.name }}
            </RouterLink>
          </dd>
        </div>
        <div class="def-item">
          <dt>巡查类型</dt>
          <dd>{{ dictionary.labelOf('inspection_type', inspection.inspect_type) }}</dd>
        </div>
        <div class="def-item">
          <dt>巡查时间</dt>
          <dd>{{ formatDateTime(inspection.inspected_at) }}</dd>
        </div>
        <div class="def-item">
          <dt>巡查人</dt>
          <dd>{{ inspection.inspector }}</dd>
        </div>
        <div class="def-item">
          <dt>天气</dt>
          <dd>{{ dictionary.labelOf('weather', inspection.weather) }}</dd>
        </div>
        <div class="def-item">
          <dt>巡查水位</dt>
          <dd>{{ formatNumber(inspection.water_level) }} m</dd>
        </div>
        <div class="def-item">
          <dt>降雨量</dt>
          <dd>{{ formatNumber(inspection.rainfall, 1) }} mm</dd>
        </div>
        <div class="def-item">
          <dt>巡查路线</dt>
          <dd>{{ inspection.route || '—' }}</dd>
        </div>
        <div class="def-item full">
          <dt>情况小结</dt>
          <dd>{{ inspection.summary || '—' }}</dd>
        </div>
        <div class="def-item full">
          <dt>备注</dt>
          <dd>{{ inspection.remark || '—' }}</dd>
        </div>
      </dl>
    </BaseCard>

    <BaseCard title="巡查项明细" :subtitle="`共 ${inspection.items.length} 项`" tight>
      <InspectionItemsTable :items="inspection.items" />
    </BaseCard>

    <BaseCard title="本次巡查登记的隐患" :subtitle="`共 ${hazards.length} 条`" tight>
      <DataTable
        v-if="hazards.length"
        :columns="hazardColumns"
        :rows="hazards"
        empty-text="暂无关联隐患"
      >
        <template #code="{ row }">
          <RouterLink class="mono" :to="`/hazards/${row.id}`">{{ row.code }}</RouterLink>
        </template>
        <template #severity="{ row }">
          <StatusTag kind="hazard_severity" :value="row.severity" />
        </template>
        <template #status="{ row }">
          <StatusTag kind="hazard_status" :value="row.status" />
        </template>
      </DataTable>
      <EmptyState
        v-else
        title="本次巡查未登记隐患"
        description="如发现异常可点击右上角「登记隐患」补充登记"
      />
    </BaseCard>
  </div>
</template>

