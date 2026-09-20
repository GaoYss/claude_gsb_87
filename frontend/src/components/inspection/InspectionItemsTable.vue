<script setup>
import StatusTag from '@/components/common/StatusTag.vue'
import { useDictionaryStore } from '@/stores/dictionary'

defineProps({
  items: { type: Array, default: () => [] },
})

const dictionary = useDictionaryStore()
</script>

<template>
  <div class="table-wrap">
    <table class="data-table">
      <thead>
        <tr>
          <th style="width: 160px">检查部位</th>
          <th style="width: 110px">检查结果</th>
          <th>情况说明</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="!items.length">
          <td class="table-state" colspan="3">本次巡查未录入巡查项明细</td>
        </tr>
        <tr v-for="item in items" :key="item.id">
          <td>{{ dictionary.labelOf('structure_part', item.part) }}</td>
          <td><StatusTag kind="item_result" :value="item.result" /></td>
          <td>{{ item.description || '—' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

