<script setup>
import { computed, reactive, ref, watch } from 'vue'

import { useDictionaryStore } from '@/stores/dictionary'

const props = defineProps({
  submitting: { type: Boolean, default: false },
  assignee: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  disabledHint: { type: String, default: '隐患已销号，无法追加记录' },
})

const emit = defineEmits(['submit'])

const dictionary = useDictionaryStore()
const error = ref('')

const form = reactive({ action: 'progress', content: '', operator: props.assignee || '' })

watch(
  () => props.assignee,
  (value) => {
    if (!form.operator) form.operator = value || ''
  },
)

// 登记记录由系统自动生成，不由人工选择
const actionOptions = computed(() =>
  dictionary.options('rectification_action').filter((item) => item.value !== 'register'),
)

function submit() {
  if (!form.content.trim()) {
    error.value = '请填写记录内容'
    return
  }
  error.value = ''
  emit('submit', {
    action: form.action,
    content: form.content.trim(),
    operator: form.operator.trim() || null,
  })
  form.content = ''
}
</script>

<template>
  <div v-if="disabled" class="muted">{{ disabledHint }}</div>
  <form v-else @submit.prevent="submit">
    <div class="form-grid">
      <div class="field">
        <label>记录类型</label>
        <select v-model="form.action" class="select">
          <option v-for="item in actionOptions" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
      </div>
      <div class="field">
        <label>记录人</label>
        <input v-model="form.operator" class="input" placeholder="例如 王海涛" />
      </div>
      <div class="field span-2">
        <label>记录内容 <span class="required">*</span></label>
        <textarea v-model="form.content" class="textarea" placeholder="记录整改措施、进展或验收情况" />
      </div>
    </div>
    <p v-if="error" class="muted" style="color: var(--danger); margin: 8px 0 0">{{ error }}</p>
    <div class="form-actions">
      <button class="btn btn-primary" type="submit" :disabled="submitting">
        {{ submitting ? '提交中…' : '追加记录' }}
      </button>
      <span class="muted" style="align-self: center">记录「整改措施」会自动把隐患推进到整改中</span>
    </div>
  </form>
</template>
