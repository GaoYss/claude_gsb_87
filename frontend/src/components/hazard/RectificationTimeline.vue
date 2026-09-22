<script setup>
import StatusTag from '@/components/common/StatusTag.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { formatDate, formatDateTime } from '@/utils/format'

defineProps({
  records: { type: Array, default: () => [] },
})

function isCloseRecord(record) {
  return record.status_to === 'closed'
}
</script>

<template>
  <EmptyState v-if="!records.length" title="暂无整改跟踪记录" />
  <ol v-else class="timeline">
    <li v-for="record in records" :key="record.id" class="timeline-item">
      <div class="timeline-head">
        <StatusTag kind="rectification_action" :value="record.action" />
        <span class="timeline-meta">{{ formatDateTime(record.recorded_at) }}</span>
        <span v-if="record.operator" class="timeline-meta">· {{ record.operator }}</span>
        <span v-if="record.status_from || record.status_to" class="row-gap">
          <StatusTag v-if="record.status_from" kind="hazard_status" :value="record.status_from" />
          <span class="timeline-meta">→</span>
          <StatusTag v-if="record.status_to" kind="hazard_status" :value="record.status_to" />
        </span>
      </div>
      <div class="timeline-body">{{ record.content }}</div>

      <!-- 销号审计信息：验收依据 + 业务销号日期，随流水固化、随时可回看 -->
      <div v-if="isCloseRecord(record)" class="close-audit">
        <div v-if="record.acceptance_opinion" class="close-audit-row">
          <span class="close-audit-label">验收意见</span>
          <span>{{ record.acceptance_opinion }}</span>
        </div>
        <div class="close-audit-row">
          <span class="close-audit-label">销号日期</span>
          <span>{{ formatDate(record.closed_on) }}</span>
        </div>
        <div class="close-audit-row">
          <span class="close-audit-label">销号经办</span>
          <span>{{ record.operator || '—' }}（{{ formatDateTime(record.recorded_at) }}）</span>
        </div>
      </div>
    </li>
  </ol>
</template>

<style scoped>
.close-audit {
  margin-top: 8px;
  padding: 8px 10px;
  border: 1px solid var(--border-color, #e3e6eb);
  border-radius: 6px;
  background: var(--surface-muted, #f7f8fa);
  font-size: 13px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.close-audit-row {
  display: flex;
  gap: 8px;
}

.close-audit-label {
  flex: none;
  width: 64px;
  color: var(--text-muted, #8a9099);
}
</style>
