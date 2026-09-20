<script setup>
import { computed } from 'vue'

import { useDictionaryStore } from '@/stores/dictionary'
import { TAG_TONES } from '@/utils/constants'

const props = defineProps({
  /** 字典类型，如 hazard_status */
  kind: { type: String, required: true },
  value: { type: String, default: '' },
  fallback: { type: String, default: '—' },
})

const dictionary = useDictionaryStore()

const tone = computed(() => TAG_TONES[props.kind]?.[props.value] || 'muted')
const label = computed(() => dictionary.labelOf(props.kind, props.value))
</script>

<template>
  <span v-if="value" class="tag" :class="`tag-${tone}`">{{ label }}</span>
  <span v-else class="muted">{{ fallback }}</span>
</template>

