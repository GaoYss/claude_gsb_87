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
const operator = ref(props.assignee || '')
const content = ref('')
const acceptanceOpinion = ref('')
const closedOn = ref(todayISO())
const activeTarget = ref(null)
const formError = ref('')
const fieldErrors = ref({})

const transitions = computed(() => dictionary.transitionsFor(props.status))
const isCloseExpanded = ref(false)

watch(
  () => props.assignee,
  (value) => {
    if (!operator.value) operator.value = value || ''
  },
)

// 状态变化（流转成功 / 页面刷新）后收起销号表单并清空输入
watch(
  () => props.status,
  () => {
    isCloseExpanded.value = false
    activeTarget.value = null
    content.value = ''
    acceptanceOpinion.value = ''
    closedOn.value = todayISO()
    formError.value = ''
    fieldErrors.value = {}
  },
)

function todayISO() {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}

function activate(transition) {
  if (transition.target_status === 'closed') {
    // 销号需要验收意见与销号日期，展开专用表单而不是直接提交
    formError.value = ''
    fieldErrors.value = {}
    isCloseExpanded.value = true
    return
  }

  // 销号面板展开时点其它流转（如退回整改）：先收起销号表单，
  // 回到带「处理说明」输入框的常规表单，避免必填说明无处填写
  if (isCloseExpanded.value) {
    isCloseExpanded.value = false
    formError.value = ''
    return
  }

  formError.value = ''
  if (transition.require_content && !content.value.trim()) {
    formError.value = `「${transition.label}」需要先填写处理说明`
    return
  }
  activeTarget.value = transition.target_status
  emit('submit', {
    target_status: transition.target_status,
    content: content.value.trim() || null,
    operator: operator.value.trim() || null,
  })
}

function confirmClose() {
  fieldErrors.value = {}
  const missing = []
  if (!acceptanceOpinion.value.trim()) {
    fieldErrors.value.acceptance_opinion = '请填写验收意见'
    missing.push('验收意见')
  }
  if (!closedOn.value) {
    fieldErrors.value.closed_on = '请选择销号日期'
    missing.push('销号日期')
  }
  if (missing.length) {
    formError.value = `销号失败：缺少${missing.join('、')}，补齐后才能销号`
    return
  }
  if (closedOn.value > todayISO()) {
    fieldErrors.value.closed_on = '销号日期不能晚于今天'
    formError.value = '销号日期不能晚于今天'
    return
  }

  formError.value = ''
  activeTarget.value = 'closed'
  emit('submit', {
    target_status: 'closed',
    content: content.value.trim() || null,
    operator: operator.value.trim() || null,
    acceptance_opinion: acceptanceOpinion.value.trim(),
    closed_on: closedOn.value,
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

        <!-- 非销号流转：填写处理说明 -->
        <template v-if="!isCloseExpanded">
          <textarea
            v-model="content"
            class="textarea"
            placeholder="处理说明（提交验收、退回整改时必填）"
          />
        </template>

        <!-- 销号专用表单：验收意见 + 销号日期缺一不可 -->
        <div v-if="isCloseExpanded" class="close-panel">
          <div class="field">
            <label>验收意见 <span class="required">*</span></label>
            <textarea
              v-model="acceptanceOpinion"
              class="textarea"
              placeholder="填写现场复核、整改到位情况等验收结论，作为销号依据留存"
            />
            <p v-if="fieldErrors.acceptance_opinion" class="field-error">
              {{ fieldErrors.acceptance_opinion }}
            </p>
          </div>
          <div class="field">
            <label>销号日期 <span class="required">*</span></label>
            <input v-model="closedOn" class="input" type="date" :max="todayISO()" />
            <p v-if="fieldErrors.closed_on" class="field-error">{{ fieldErrors.closed_on }}</p>
          </div>
          <div class="field">
            <label>补充说明</label>
            <textarea
              v-model="content"
              class="textarea"
              placeholder="选填，其他需要随销号流水一并留存的说明"
            />
          </div>
        </div>

        <p v-if="formError" class="muted form-error-text">{{ formError }}</p>

        <div class="row-gap" style="margin-top: 12px">
          <template v-for="transition in transitions" :key="transition.target_status">
            <button
              v-if="transition.target_status !== 'closed' || !isCloseExpanded"
              class="btn"
              :class="transition.target_status === 'closed' ? 'btn-primary' : ''"
              type="button"
              :disabled="submitting"
              @click="activate(transition)"
            >
              {{ submitting && activeTarget === transition.target_status ? '处理中…' : transition.label }}
            </button>
          </template>
          <template v-if="isCloseExpanded">
            <button class="btn btn-primary" type="button" :disabled="submitting" @click="confirmClose">
              {{ submitting ? '处理中…' : '确认销号' }}
            </button>
            <button class="btn" type="button" :disabled="submitting" @click="isCloseExpanded = false">
              取消
            </button>
          </template>
        </div>
      </template>
      <p v-else class="muted" style="margin: 0">该隐患已销号，流程结束。如需处理新的问题请重新登记隐患。</p>
    </div>
  </section>
</template>

<style scoped>
.close-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field-error {
  color: var(--danger);
  margin: 4px 0 0;
  font-size: 13px;
}

.form-error-text {
  color: var(--danger);
  margin: 8px 0 0;
}
</style>
