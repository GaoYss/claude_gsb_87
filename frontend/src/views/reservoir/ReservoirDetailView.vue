<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { deleteReservoir, fetchReservoir, fetchReservoirStats } from '@/api/reservoirs'
import BaseCard from '@/components/common/BaseCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatCard from '@/components/common/StatCard.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import ReservoirHazardsPanel from '@/components/reservoir/ReservoirHazardsPanel.vue'
import ReservoirInfoPanel from '@/components/reservoir/ReservoirInfoPanel.vue'
import ReservoirInspectionsPanel from '@/components/reservoir/ReservoirInspectionsPanel.vue'
import { useConfirmStore } from '@/stores/confirm'
import { useToastStore } from '@/stores/toast'
import { formatDateTime } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const toast = useToastStore()
const confirm = useConfirmStore()

const reservoir = ref(null)
const stats = ref(null)
const loading = ref(true)
const activeTab = ref('info')

const tabs = [
  { key: 'info', label: '工程台账' },
  { key: 'inspections', label: '巡查记录' },
  { key: 'hazards', label: '隐患台账' },
]

const description = computed(() => {
  if (!reservoir.value) return ''
  const parts = [reservoir.value.code, reservoir.value.region]
  if (reservoir.value.manager) parts.push(reservoir.value.manager)
  return parts.join(' · ')
})

async function load() {
  loading.value = true
  try {
    const [detail, statistics] = await Promise.all([
      fetchReservoir(route.params.id),
      fetchReservoirStats(route.params.id),
    ])
    reservoir.value = detail
    stats.value = statistics
  } catch (error) {
    toast.error(error.message)
    router.replace({ name: 'reservoir-list' })
  } finally {
    loading.value = false
  }
}

onMounted(load)

// 路由参数变化时组件会被复用，需要重新拉取详情
watch(
  () => route.params.id,
  (id) => {
    // 仅在仍处于水库详情路由时刷新，避免跳转到其它详情页时误触发
    if (id && route.name === 'reservoir-detail') load()
  },
)

async function remove() {
  const ok = await confirm.ask(`确认删除水库「${reservoir.value.name}」？删除后不可恢复。`)
  if (!ok) return
  try {
    await deleteReservoir(reservoir.value.id)
    toast.success('水库已删除')
    router.replace({ name: 'reservoir-list' })
  } catch (error) {
    toast.error(error.message)
  }
}
</script>

<template>
  <div v-if="loading" class="muted">加载中…</div>
  <div v-else-if="reservoir && stats">
    <PageHeader :title="reservoir.name" :description="description">
      <template #badge>
        <StatusTag kind="reservoir_status" :value="reservoir.status" />
      </template>
      <template #actions>
        <RouterLink
          class="btn"
          :to="{ name: 'inspection-create', query: { reservoir_id: reservoir.id } }"
        >
          录入巡查
        </RouterLink>
        <RouterLink class="btn" :to="{ name: 'hazard-create', query: { reservoir_id: reservoir.id } }">
          登记隐患
        </RouterLink>
        <RouterLink class="btn" :to="`/reservoirs/${reservoir.id}/edit`">编辑</RouterLink>
        <button class="btn btn-danger" type="button" @click="remove">删除</button>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <StatCard
        label="巡查记录"
        :value="stats.inspection_total"
        :hint="`近 30 天 ${stats.inspection_last_30_days} 次`"
      />
      <StatCard
        label="最近巡查时间"
        :value="stats.last_inspected_at ? formatDateTime(stats.last_inspected_at).slice(5, 16) : '—'"
        :hint="stats.last_inspected_at ? '按最新巡查时间统计' : '尚未开展巡查'"
      />
      <StatCard
        label="未销号隐患"
        :value="stats.hazard_open"
        :hint="`隐患总数 ${stats.hazard_total} 条`"
        :tone="stats.hazard_open ? 'warn' : 'ok'"
      />
      <StatCard
        label="逾期未整改"
        :value="stats.hazard_overdue"
        :hint="`已销号 ${stats.hazard_closed} 条`"
        :tone="stats.hazard_overdue ? 'danger' : 'ok'"
      />
    </div>

    <div class="tabs card">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab"
        :class="{ 'is-active': activeTab === tab.key }"
        type="button"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <ReservoirInfoPanel v-if="activeTab === 'info'" :reservoir="reservoir" />
    <ReservoirInspectionsPanel
      v-else-if="activeTab === 'inspections'"
      :key="`inspections-${reservoir.id}`"
      :reservoir-id="reservoir.id"
    />
    <ReservoirHazardsPanel v-else :key="`hazards-${reservoir.id}`" :reservoir-id="reservoir.id" />
  </div>
  <BaseCard v-else title="水库不存在">
    <RouterLink class="btn" to="/reservoirs">返回水库台账</RouterLink>
  </BaseCard>
</template>
