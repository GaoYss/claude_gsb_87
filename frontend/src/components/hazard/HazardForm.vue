<script setup>
import { reactive, ref, watch } from 'vue'

import FormField from '@/components/common/FormField.vue'
import InspectionSelect from '@/components/inspection/InspectionSelect.vue'
import ReservoirSelect from '@/components/reservoir/ReservoirSelect.vue'
import { useDictionaryStore } from '@/stores/dictionary'
import { cleanPayload } from '@/utils/form'
import { todayString, toDateInput } from '@/utils/format'

const props = defineProps({
  initial: { type: Object, default: null },
  submitting: { type: Boolean, default: false },
  isEdit: { type: Boolean, default: false },
  presetReservoirId: { type: [Number, String], default: null },
  presetInspectionId: { type: [Number, String], default: null },
})

const emit = defineEmits(['submit', 'cancel'])

const dictionary = useDictionaryStore()

function buildState(source) {
  return {
    reservoir_id: source?.reservoir_id ?? props.presetReservoirId ?? null,
    inspection_id: source?.inspection_id ?? props.presetInspectionId ?? null,
    title: source?.title ?? '',
    category: source?.category ?? 'dam_body',
    severity: source?.severity ?? 'general',
    source: source?.source ?? 'inspection',
    discovered_on: source ? toDateInput(source.discovered_on) : todayString(),
    discoverer: source?.discoverer ?? '',
    deadline: source?.deadline ? toDateInput(source.deadline) : '',
    assignee: source?.assignee ?? '',
    description: source?.description ?? '',
    plan: source?.plan ?? '',
  }
}

const form = reactive(buildState(props.initial))
const error = ref('')

watch(
  () => props.initial,
  (value) => Object.assign(form, buildState(value)),
)

function submit() {
  if (!form.reservoir_id) {
    error.value = '请选择水库'
    return
  }
  if (!form.title.trim()) {
    error.value = '请填写隐患标题'
    return
  }
  if (!form.category) {
    error.value = '请选择隐患类别'
    return
  }
  if (form.deadline && form.discovered_on && form.deadline < form.discovered_on) {
    error.value = '整改期限不能早于发现日期'
    return
  }
  error.value = ''

  const payload = cleanPayload(form, {
    textFields: ['title', 'discoverer', 'assignee', 'description', 'plan'],
  })
  if (props.isEdit) delete payload.reservoir_id
  emit('submit', payload)
}
</script>

<template>
  <form @submit.prevent="submit">
    <section class="card">
      <header class="card-header"><div class="card-title">隐患基本信息</div></header>
      <div class="card-body">
        <div class="form-grid">
          <FormField label="所属水库" required>
            <ReservoirSelect v-model="form.reservoir_id" />
          </FormField>
          <FormField label="来源巡查记录" hint="可关联巡查记录，便于追溯发现过程">
            <InspectionSelect v-model="form.inspection_id" :reservoir-id="form.reservoir_id" />
          </FormField>
          <FormField label="隐患标题" required>
            <input v-model="form.title" class="input" placeholder="例如 背水面坝脚局部渗水" />
          </FormField>
          <FormField label="隐患类别" required>
            <select v-model="form.category" class="select">
              <option v-for="item in dictionary.options('structure_part')" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
          </FormField>
          <FormField label="隐患等级" required>
            <select v-model="form.severity" class="select">
              <option v-for="item in dictionary.options('hazard_severity')" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
          </FormField>
          <FormField label="隐患来源">
            <select v-model="form.source" class="select">
              <option v-for="item in dictionary.options('hazard_source')" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
          </FormField>
        </div>
      </div>
    </section>

    <section class="card">
      <header class="card-header"><div class="card-title">责任与时限</div></header>
      <div class="card-body">
        <div class="form-grid">
          <FormField label="发现日期" required>
            <input v-model="form.discovered_on" class="input" type="date" />
          </FormField>
          <FormField label="发现人">
            <input v-model="form.discoverer" class="input" placeholder="例如 王海涛" />
          </FormField>
          <FormField label="整改期限" hint="超过期限且未销号会自动标记为逾期">
            <input v-model="form.deadline" class="input" type="date" />
          </FormField>
          <FormField label="整改责任人">
            <input v-model="form.assignee" class="input" placeholder="单位或责任人" />
          </FormField>
        </div>
      </div>
    </section>

    <section class="card">
      <header class="card-header"><div class="card-title">隐患描述与整改要求</div></header>
      <div class="card-body">
        <div class="form-grid">
          <FormField label="隐患描述" class="span-2">
            <textarea v-model="form.description" class="textarea" placeholder="位置、范围、程度等" />
          </FormField>
          <FormField label="整改方案 / 要求" class="span-2">
            <textarea v-model="form.plan" class="textarea" placeholder="处理措施、验收要求等" />
          </FormField>
        </div>
      </div>
    </section>

    <p v-if="error" class="muted" style="color: var(--danger)">{{ error }}</p>

    <div class="form-actions">
      <button class="btn btn-primary" type="submit" :disabled="submitting">
        {{ submitting ? '提交中…' : isEdit ? '保存修改' : '登记隐患' }}
      </button>
      <button class="btn" type="button" @click="emit('cancel')">取消</button>
    </div>
  </form>
</template>
