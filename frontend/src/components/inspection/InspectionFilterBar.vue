<script setup>
import { ref, watch } from 'vue'

import FilterBar from '@/components/common/FilterBar.vue'
import ReservoirSelect from '@/components/reservoir/ReservoirSelect.vue'
import { useDictionaryStore } from '@/stores/dictionary'

const filters = defineModel({ type: Object, required: true })

const emit = defineEmits(['reset'])

const dictionary = useDictionaryStore()

const keyword = ref(filters.value.keyword || '')
let timer = null

watch(keyword, (value) => {
  clearTimeout(timer)
  timer = setTimeout(() => {
    filters.value.keyword = value
  }, 350)
})

watch(
  () => filters.value.keyword,
  (value) => {
    if ((value || '') !== keyword.value) keyword.value = value || ''
  },
)
</script>

<template>
  <FilterBar>
    <div class="filter-field" style="min-width: 200px">
      <span>关键字</span>
      <input v-model="keyword" class="input" placeholder="编号 / 巡查人 / 路线 / 小结" />
    </div>
    <div class="filter-field">
      <span>水库</span>
      <ReservoirSelect v-model="filters.reservoir_id" allow-all />
    </div>
    <div class="filter-field">
      <span>巡查类型</span>
      <select v-model="filters.inspect_type" class="select">
        <option value="">全部</option>
        <option v-for="item in dictionary.options('inspection_type')" :key="item.value" :value="item.value">
          {{ item.label }}
        </option>
      </select>
    </div>
    <div class="filter-field">
      <span>巡查结论</span>
      <select v-model="filters.status" class="select">
        <option value="">全部</option>
        <option v-for="item in dictionary.options('inspection_status')" :key="item.value" :value="item.value">
          {{ item.label }}
        </option>
      </select>
    </div>
    <div class="filter-field">
      <span>巡查时间从</span>
      <input v-model="filters.date_from" class="input" type="date" />
    </div>
    <div class="filter-field">
      <span>到</span>
      <input v-model="filters.date_to" class="input" type="date" />
    </div>
    <template #actions>
      <button class="btn" type="button" @click="emit('reset')">重置筛选</button>
    </template>
  </FilterBar>
</template>

