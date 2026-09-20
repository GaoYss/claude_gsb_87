<script setup>
import { computed, ref, watch } from 'vue'

import StatusTag from '@/components/common/StatusTag.vue'
import { useDictionaryStore } from '@/stores/dictionary'

const props = defineProps({
  status: { type: String, required: true },
  assignee: { type: String, default: '' },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['submit'])

const dictionary = useDictionaryStore()
const content = ref('')
const operator = ref(props.assignee || '')
const error = ref('')
const activeTarget = ref(null)

const transitions = computed(() => dictionary.transitionsFor(props.status))

watch(
  () => props.assignee,
  (value) => {
    if (!operator.value) operator.value = value || ''
  },
)

function activate(transition) {
  error.value = ''
  if (transition.require_content && !content.value.trim()) {
    activeTarget.value = transition.target_status
    error.value = `「${transition.label}」需要先填写处理说明`
    return
  }
  activeTarget.value = transition.target_status
  emit('submit', {
    target_status: transition.target_status,
    content: content.value.trim() || null,
    operator: operator.value.trim() || null,
  })
}
</script>

<template>
  <section class="card">
    <header class="card-header">
      <div>
        <div class="card-title">整改状态流转</div>
        <div class="card-subtitle">当前状态：<StatusTag kind="hazard_status" :value="status" /></div>
      </div>
    </header>
    <div class="card-body">
      <template v-if="transitions.length">
        <div class="row-gap" style="margin-bottom: 10px">
          <input v-model="operator" class="input" style="max-width: 200px" placeholder="操作人" />
        </div>
        <textarea
          v-model="content"
          class="textarea"
          placeholder="处理说明（提交验收、退回整改、销号时必填）"
        />
        <p v-if="error" class="muted" style="color: var(--danger); margin: 8px 0 0">{{ error }}</p>
        <div class="row-gap" style="margin-top: 12px">
          <button
            v-for="transition in transitions"
            :key="transition.target_status"
            class="btn"
            :class="transition.target_status === 'closed' ? 'btn-primary' : ''"
            type="button"
            :disabled="submitting"
            @click="activate(transition)"
          >
            {{ submitting && activeTarget === transition.target_status ? '处理中…' : transition.label }}
          </button>
        </div>
      </template>
      <p v-else class="muted" style="margin: 0">该隐患已销号，流程结束。如需处理新的问题请重新登记隐患。</p>
    </div>
  </section>
</template>

