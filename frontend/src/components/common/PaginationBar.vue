<script setup>
const props = defineProps({
  page: { type: Number, default: 1 },
  pageSize: { type: Number, default: 20 },
  total: { type: Number, default: 0 },
  pages: { type: Number, default: 0 },
  sizeOptions: { type: Array, default: () => [10, 20, 50] },
})

const emit = defineEmits(['update:page', 'update:pageSize'])
</script>

<template>
  <div class="pagination">
    <span>共 {{ total }} 条 · 第 {{ pages ? page : 0 }} / {{ pages }} 页</span>
    <div class="pagination-controls">
      <select :value="pageSize" @change="emit('update:pageSize', Number($event.target.value))">
        <option v-for="size in sizeOptions" :key="size" :value="size">{{ size }} 条 / 页</option>
      </select>
      <button class="btn btn-sm" :disabled="page <= 1" @click="emit('update:page', page - 1)">上一页</button>
      <button class="btn btn-sm" :disabled="page >= pages" @click="emit('update:page', page + 1)">下一页</button>
    </div>
  </div>
</template>

