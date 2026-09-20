<script setup>
import StatusTag from '@/components/common/StatusTag.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { formatDateTime } from '@/utils/format'

defineProps({
  records: { type: Array, default: () => [] },
})
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
    </li>
  </ol>
</template>

