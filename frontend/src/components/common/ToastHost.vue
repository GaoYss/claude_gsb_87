<script setup>
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
</script>

<template>
  <div class="toast-host">
    <div
      v-for="item in toast.items"
      :key="item.id"
      class="toast"
      :class="`toast-${item.type}`"
      @click="toast.dismiss(item.id)"
    >
      {{ item.message }}
    </div>
  </div>
</template>

