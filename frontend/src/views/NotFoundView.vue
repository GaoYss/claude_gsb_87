<script setup>
import EmptyState from '@/components/common/EmptyState.vue'
</script>

<template>
  <section class="card">
    <EmptyState title="页面不存在" description="请检查访问地址，或从左侧导航重新进入">
      <template #action>
        <RouterLink class="btn btn-primary" to="/dashboard">返回总览</RouterLink>
      </template>
    </EmptyState>
  </section>
</template>

