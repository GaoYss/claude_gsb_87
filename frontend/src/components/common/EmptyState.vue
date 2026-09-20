<script setup>
defineProps({
  title: { type: String, default: '暂无数据' },
  description: { type: String, default: '' },
})
</script>

<template>
  <div class="empty-state">
    <div class="empty-title">{{ title }}</div>
    <div v-if="description">{{ description }}</div>
    <div v-if="$slots.action" style="margin-top: 12px">
      <slot name="action" />
    </div>
  </div>
</template>

