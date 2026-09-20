<script setup>
defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  tight: { type: Boolean, default: false },
})
</script>

<template>
  <section class="card">
    <header v-if="title || $slots.actions" class="card-header">
      <div>
        <div class="card-title">{{ title }}</div>
        <div v-if="subtitle" class="card-subtitle">{{ subtitle }}</div>
      </div>
      <div class="page-actions">
        <slot name="actions" />
      </div>
    </header>
    <div class="card-body" :class="{ tight }">
      <slot />
    </div>
  </section>
</template>

