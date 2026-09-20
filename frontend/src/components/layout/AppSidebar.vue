<script setup>
import { NAV_ITEMS } from '@/utils/constants'
</script>

<template>
  <aside class="app-sidebar">
    <div class="brand">
      <div class="brand-title">水库日常巡查记录系统</div>
      <div class="brand-subtitle">台账 · 巡查 · 隐患整改</div>
    </div>
    <nav class="nav">
      <RouterLink
        v-for="item in NAV_ITEMS"
        :key="item.name"
        class="nav-link"
        :class="{ 'is-active': $route.path.startsWith(item.path) }"
        :to="item.path"
      >
        {{ item.label }}
      </RouterLink>
    </nav>
    <div class="sidebar-footer">
      Vue 3 + FastAPI<br />
      <span class="muted">v1.0.0</span>
    </div>
  </aside>
</template>

