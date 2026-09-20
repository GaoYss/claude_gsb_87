<script setup>
import { computed } from 'vue'

import { TAG_TONES } from '@/utils/constants'

const props = defineProps({
  items: { type: Array, default: () => [] },
  toneKey: { type: String, default: '' },
})

const max = computed(() => Math.max(1, ...props.items.map((item) => item.count || 0)))

function width(item) {
  return `${Math.round(((item.count || 0) / max.value) * 100)}%`
}

function tone(item) {
  return TAG_TONES[props.toneKey]?.[item.value] || ''
}
</script>

<template>
  <div class="distribution">
    <div v-for="item in items" :key="item.value" class="distribution-row">
      <span class="distribution-name">{{ item.label }}</span>
      <span class="distribution-bar">
        <span class="distribution-fill" :class="tone(item) ? `tone-${tone(item)}` : ''" :style="{ width: width(item) }" />
      </span>
      <span class="distribution-count">{{ item.count }}</span>
    </div>
  </div>
</template>

