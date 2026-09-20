<script setup>
defineProps({
  label: { type: String, required: true },
  required: { type: Boolean, default: false },
  hint: { type: String, default: '' },
})
</script>

<template>
  <div class="field">
    <label>
      {{ label }}
      <span v-if="required" class="required">*</span>
    </label>
    <slot />
    <div v-if="hint" class="hint">{{ hint }}</div>
  </div>
</template>

