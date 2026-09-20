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
    <div class="filter-field" style="min-width: 190px">
      <span>关键字</span>
      <input v-model="keyword" class="input" placeholder="标题 / 编号 / 描述 / 责任人" />
    </div>
    <div class="filter-field">
      <span>水库</span>
      <ReservoirSelect v-model="filters.reservoir_id" allow-all />
    </div>
    <div class="filter-field">
      <span>隐患类别</span>
      <select v-model="filters.category" class="select">
        <option value="">全部</option>
        <option v-for="item in dictionary.options('structure_part')" :key="item.value" :value="item.value">
          {{ item.label }}
        </option>
      </select>
    </div>
    <div class="filter-field">
      <span>隐患等级</span>
      <select v-model="filters.severity" class="select">
        <option value="">全部</option>
        <option v-for="item in dictionary.options('hazard_severity')" :key="item.value" :value="item.value">
          {{ item.label }}
        </option>
      </select>
    </div>
    <div class="filter-field">
      <span>整改状态</span>
      <select v-model="filters.status" class="select">
        <option value="">全部</option>
        <option v-for="item in dictionary.options('hazard_status')" :key="item.value" :value="item.value">
          {{ item.label }}
        </option>
      </select>
    </div>
    <div class="filter-field" style="min-width: 120px">
      <span>范围</span>
      <label class="row-gap" style="font-size: 13px">
        <input v-model="filters.overdue_only" type="checkbox" />
        仅看逾期
      </label>
      <label class="row-gap" style="font-size: 13px">
        <input v-model="filters.open_only" type="checkbox" />
        仅看未销号
      </label>
    </div>
    <template #actions>
      <button class="btn" type="button" @click="emit('reset')">重置筛选</button>
    </template>
  </FilterBar>
</template>

