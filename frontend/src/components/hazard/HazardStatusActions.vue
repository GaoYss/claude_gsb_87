<script setup>
import { computed, ref, watch } from 'vue'

import StatusTag from '@/components/common/StatusTag.vue'
import { useDictionaryStore } from '@/stores/dictionary'
import { todayString } from '@/utils/format'

const props = defineProps({
  status: { type: String, required: true },
  assignee: { type: String, default: '' },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['submit'])

const dictionary = useDictionaryStore()
const content = ref('')
const operator = ref(props.assignee || '')
const closedOn = ref(todayString())
const error = ref('')
const activeTarget = ref(null)

const transitions = computed(() => dictionary.transitionsFor(props.status))
// 当前可选流转里包含销号时，才需要展示销号日期输入
const hasClosureOption = computed(() => transitions.value.some((item) => item.require_closed_on))

watch(
  () => props.assignee,
  (value) => {
    if (!operator.value) operator.value = value || ''
  },
)

function activate(transition) {
  error.value = ''
  activeTarget.value = transition.target_status

  if (transition.require_closed_on) {
    // 与后端一致的销号前置校验：验收意见、销号日期缺一不可
    const missing = []
    if (!content.value.trim()) missing.push('验收意见')
    if (!closedOn.value) missing.push('销号日期')
    if (missing.length) {
      error.value = `销号需要同时提供验收意见和销号日期，缺少：${missing.join('、')}`
      return
    }
  } else if (transition.require_content && !content.value.trim()) {
    error.value = `「${transition.label}」需要先填写处理说明`
    return
  }

  emit('submit', {
    target_status: transition.target_status,
    content: content.value.trim() || null,
    operator: operator.value.trim() || null,
    closed_on: transition.require_closed_on ? closedOn.value || null : null,
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
          <template v-if="hasClosureOption">
            <label class="muted" style="align-self: center" for="closed-on-input">销号日期</label>
            <input
              id="closed-on-input"
              v-model="closedOn"
              class="input"
              style="max-width: 180px"
              type="date"
            />
          </template>
        </div>
        <textarea
          v-model="content"
          class="textarea"
          :placeholder="
            hasClosureOption
              ? '处理说明（销号时填写验收意见；提交验收、退回整改时必填）'
              : '处理说明（提交验收、退回整改时必填）'
          "
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
