<script setup>
import { ref, watch } from 'vue'

import FilterBar from '@/components/common/FilterBar.vue'
import { useDictionaryStore } from '@/stores/dictionary'

const filters = defineModel({ type: Object, required: true })

const emit = defineEmits(['reset'])

const dictionary = useDictionaryStore()

// 关键字做 350ms 防抖，避免每敲一个字就请求一次
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
    <div class="filter-field" style="min-width: 220px">
      <span>关键字</span>
      <input v-model="keyword" class="input" placeholder="名称 / 编码 / 位置 / 管理单位" />
    </div>
    <div class="filter-field">
      <span>所在行政区</span>
      <select v-model="filters.region" class="select">
        <option value="">全部</option>
        <option v-for="region in dictionary.regions" :key="region" :value="region">{{ region }}</option>
      </select>
    </div>
    <div class="filter-field">
      <span>运行状态</span>
      <select v-model="filters.status" class="select">
        <option value="">全部</option>
        <option v-for="item in dictionary.options('reservoir_status')" :key="item.value" :value="item.value">
          {{ item.label }}
        </option>
      </select>
    </div>
    <div class="filter-field">
      <span>大坝安全类别</span>
      <select v-model="filters.safety_class" class="select">
        <option value="">全部</option>
        <option v-for="item in dictionary.options('safety_class')" :key="item.value" :value="item.value">
          {{ item.label }}
        </option>
      </select>
    </div>
    <template #actions>
      <button class="btn" type="button" @click="emit('reset')">重置筛选</button>
    </template>
  </FilterBar>
</template>

