<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchHealth } from '@/api/meta'

const route = useRoute()
const health = ref(null)

onMounted(async () => {
  try {
    health.value = await fetchHealth()
  } catch {
    health.value = { status: 'down' }
  }
})
</script>

<template>
  <header class="app-topbar">
    <div>
      <h1>{{ route.meta.title || '总览' }}</h1>
      <div class="topbar-sub">水库工程日常巡查与隐患整改闭环管理</div>
    </div>
    <div class="health-badge">
      <span class="health-dot" :class="{ 'is-down': health && health.status !== 'ok' }" />
      <span v-if="health && health.status === 'ok'">接口正常 · v{{ health.version }}</span>
      <span v-else-if="health">接口不可用</span>
      <span v-else>检查中…</span>
    </div>
  </header>
</template>

