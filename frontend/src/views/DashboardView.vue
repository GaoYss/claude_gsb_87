<script setup>
import { onMounted, ref } from 'vue'

import { fetchSummary } from '@/api/overview'
import BaseCard from '@/components/common/BaseCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import DistributionList from '@/components/common/DistributionList.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import StatCard from '@/components/common/StatCard.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import { useDictionaryStore } from '@/stores/dictionary'
import { useToastStore } from '@/stores/toast'
import { deadlineHint, formatDateTime } from '@/utils/format'

const dictionary = useDictionaryStore()
const toast = useToastStore()

const summary = ref(null)
const loading = ref(true)

const inspectionColumns = [
  { key: 'code', label: '巡查编号', width: '150px' },
  { key: 'reservoir_name', label: '水库' },
  { key: 'inspect_type', label: '类型', width: '110px' },
  { key: 'inspected_at', label: '巡查时间', width: '160px' },
  { key: 'inspector', label: '巡查人', width: '100px' },
  { key: 'status', label: '结论', width: '110px' },
]

const hazardColumns = [
  { key: 'code', label: '隐患编号', width: '150px' },
  { key: 'title', label: '隐患标题' },
  { key: 'severity', label: '等级', width: '110px' },
  { key: 'status', label: '状态', width: '110px' },
  { key: 'deadline', label: '整改期限', width: '140px' },
]

onMounted(async () => {
  try {
    summary.value = await fetchSummary()
  } catch (error) {
    toast.error(error.message)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div v-if="loading" class="muted">加载中…</div>
  <div v-else-if="!summary" class="muted">暂无统计数据</div>
  <div v-else>
    <div class="stat-grid">
      <StatCard
        label="水库总数"
        :value="summary.reservoir_total"
        :hint="`需关注 / 存在险情 ${summary.reservoir_attention} 座`"
      />
      <StatCard
        label="巡查记录"
        :value="summary.inspection_total"
        :hint="`近 30 天 ${summary.inspection_last_30_days} 次`"
      />
      <StatCard
        label="未销号隐患"
        :value="summary.hazard_open"
        :hint="`隐患总数 ${summary.hazard_total} 条`"
        :tone="summary.hazard_open ? 'warn' : 'ok'"
      />
      <StatCard
        label="逾期未整改"
        :value="summary.hazard_overdue"
        hint="超过整改期限且未销号"
        :tone="summary.hazard_overdue ? 'danger' : 'ok'"
      />
    </div>

    <div class="split-2">
      <BaseCard title="隐患状态分布" subtitle="按整改流程统计">
        <DistributionList :items="summary.hazard_by_status" tone-key="hazard_status" />
      </BaseCard>
      <BaseCard title="隐患等级分布" subtitle="重大 / 较大隐患需重点跟踪">
        <DistributionList :items="summary.hazard_by_severity" tone-key="hazard_severity" />
      </BaseCard>
      <BaseCard title="巡查类型分布" subtitle="日常、汛期、专项与应急巡查">
        <DistributionList :items="summary.inspection_by_type" />
      </BaseCard>
      <BaseCard title="水库运行状态" subtitle="按台账运行状态统计">
        <DistributionList :items="summary.reservoir_by_status" tone-key="reservoir_status" />
      </BaseCard>
    </div>

    <BaseCard title="待办隐患" subtitle="优先展示逾期与临近整改期限的隐患">
      <template #actions>
        <RouterLink class="btn btn-sm" to="/hazards?open_only=true">查看全部</RouterLink>
      </template>
      <DataTable
        v-if="summary.urgent_hazards.length"
        :columns="hazardColumns"
        :rows="summary.urgent_hazards"
        empty-text="暂无未销号隐患"
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
        <template #deadline="{ row }">
          <span class="nowrap">{{ deadlineHint(row.deadline, row.status === 'closed') }}</span>
          <span v-if="row.is_overdue" class="tag tag-overdue" style="margin-left: 6px">逾期</span>
        </template>
      </DataTable>
      <EmptyState v-else title="暂无未销号隐患" description="所有隐患均已整改销号" />
    </BaseCard>

    <BaseCard title="最近巡查" subtitle="最新录入的巡查记录">
      <template #actions>
        <RouterLink class="btn btn-sm" to="/inspections">查看全部</RouterLink>
      </template>
      <DataTable
        v-if="summary.recent_inspections.length"
        :columns="inspectionColumns"
        :rows="summary.recent_inspections"
        empty-text="暂无巡查记录"
      >
        <template #code="{ row }">
          <RouterLink class="mono" :to="`/inspections/${row.id}`">{{ row.code }}</RouterLink>
        </template>
        <template #inspect_type="{ row }">
          {{ dictionary.labelOf('inspection_type', row.inspect_type) }}
        </template>
        <template #inspected_at="{ row }">{{ formatDateTime(row.inspected_at) }}</template>
        <template #status="{ row }">
          <StatusTag kind="inspection_status" :value="row.status" />
        </template>
      </DataTable>
      <EmptyState v-else title="暂无巡查记录" description="可前往「巡查记录」录入第一份巡查台账" />
    </BaseCard>
  </div>
</template>

