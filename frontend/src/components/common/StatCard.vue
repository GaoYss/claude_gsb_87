<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], default: 0 },
  hint: { type: String, default: '' },
  tone: { type: String, default: '' },
})
</script>

<template>
  <div class="stat-card">
    <div class="stat-label">{{ label }}</div>
    <div class="stat-value" :class="tone ? `tone-${tone}` : ''">{{ value }}</div>
    <div class="stat-hint">{{ hint }}</div>
  </div>
</template>

