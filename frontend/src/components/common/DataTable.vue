<script setup>
defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  rowKey: { type: String, default: 'id' },
  emptyText: { type: String, default: '暂无数据' },
})
</script>

<template>
  <div class="table-wrap">
    <table class="data-table">
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key" :style="column.width ? { width: column.width } : null">
            {{ column.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td class="table-state" :colspan="columns.length">加载中…</td>
        </tr>
        <tr v-else-if="!rows.length">
          <td class="table-state" :colspan="columns.length">{{ emptyText }}</td>
        </tr>
        <tr v-else v-for="row in rows" :key="row[rowKey]">
          <td v-for="column in columns" :key="column.key">
            <slot :name="column.key" :row="row">
              {{ row[column.key] === null || row[column.key] === undefined || row[column.key] === '' ? '—' : row[column.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

