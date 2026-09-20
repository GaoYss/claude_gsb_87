<script setup>
import { reactive, ref, watch } from 'vue'

import FormField from '@/components/common/FormField.vue'
import InspectionChecklistEditor from '@/components/inspection/InspectionChecklistEditor.vue'
import ReservoirSelect from '@/components/reservoir/ReservoirSelect.vue'
import { useDictionaryStore } from '@/stores/dictionary'
import { cleanPayload } from '@/utils/form'
import { nowForInput, toDateTimeInput } from '@/utils/format'

const props = defineProps({
  initial: { type: Object, default: null },
  submitting: { type: Boolean, default: false },
  isEdit: { type: Boolean, default: false },
  presetReservoirId: { type: [Number, String], default: null },
})

const emit = defineEmits(['submit', 'cancel'])

const dictionary = useDictionaryStore()

// 默认按「日常巡查标准线路」预置常见的巡查部位
const DEFAULT_PARTS = ['dam_body', 'spillway', 'outlet', 'seepage', 'facility']

function buildState(source) {
  return {
    reservoir_id: source?.reservoir_id ?? props.presetReservoirId ?? null,
    inspect_type: source?.inspect_type ?? 'daily',
    inspected_at: source ? toDateTimeInput(source.inspected_at) : nowForInput(),
    inspector: source?.inspector ?? '',
    weather: source?.weather ?? '',
    water_level: source?.water_level ?? '',
    rainfall: source?.rainfall ?? '',
    route: source?.route ?? '',
    summary: source?.summary ?? '',
    remark: source?.remark ?? '',
    items: source?.items
      ? source.items.map((item) => ({
          part: item.part,
          result: item.result,
          description: item.description ?? '',
        }))
      : DEFAULT_PARTS.map((part) => ({ part, result: 'normal', description: '' })),
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
  if (!form.inspector.trim()) {
    error.value = '请填写巡查人'
    return
  }
  const invalid = form.items.find((item) => item.result === 'abnormal' && !String(item.description || '').trim())
  if (invalid) {
    error.value = '异常项需要填写情况说明'
    return
  }
  error.value = ''

  const payload = cleanPayload(form, {
    numberFields: ['water_level', 'rainfall'],
    textFields: ['inspector', 'route', 'summary', 'remark'],
  })
  payload.items = form.items.map((item) => ({
    part: item.part,
    result: item.result,
    description: String(item.description || '').trim() || null,
  }))
  emit('submit', payload)
}
</script>

<template>
  <form @submit.prevent="submit">
    <section class="card">
      <header class="card-header"><div class="card-title">巡查基本信息</div></header>
      <div class="card-body">
        <div class="form-grid">
          <FormField label="水库" required>
            <ReservoirSelect v-model="form.reservoir_id" />
          </FormField>
          <FormField label="巡查类型">
            <select v-model="form.inspect_type" class="select">
              <option v-for="item in dictionary.options('inspection_type')" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
          </FormField>
          <FormField label="巡查时间" required hint="默认取当前时间，可回填历史巡查">
            <input v-model="form.inspected_at" class="input" type="datetime-local" />
          </FormField>
          <FormField label="巡查人" required>
            <input v-model="form.inspector" class="input" placeholder="例如 陈立" />
          </FormField>
          <FormField label="天气">
            <select v-model="form.weather" class="select">
              <option value="">未填写</option>
              <option v-for="item in dictionary.options('weather')" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
          </FormField>
          <FormField label="巡查时水位（m）">
            <input v-model="form.water_level" class="input" type="number" step="0.01" min="0" />
          </FormField>
          <FormField label="降雨量（mm）">
            <input v-model="form.rainfall" class="input" type="number" step="0.1" min="0" />
          </FormField>
          <FormField label="巡查路线">
            <input v-model="form.route" class="input" placeholder="例如 坝顶→坝脚→溢洪道" />
          </FormField>
        </div>
      </div>
    </section>

    <section class="card">
      <header class="card-header">
        <div>
          <div class="card-title">巡查项明细</div>
          <div class="card-subtitle">任一项标记为异常，整条记录结论即为「发现异常」</div>
        </div>
      </header>
      <div class="card-body">
        <InspectionChecklistEditor v-model="form.items" />
      </div>
    </section>

    <section class="card">
      <header class="card-header"><div class="card-title">巡查情况小结</div></header>
      <div class="card-body">
        <div class="form-grid">
          <FormField label="巡查情况小结" class="span-2">
            <textarea v-model="form.summary" class="textarea" placeholder="记录本次巡查总体情况" />
          </FormField>
          <FormField label="备注" class="span-2">
            <textarea v-model="form.remark" class="textarea" placeholder="需要说明的其他事项" />
          </FormField>
        </div>
      </div>
    </section>

    <p v-if="error" class="muted" style="color: var(--danger)">{{ error }}</p>

    <div class="form-actions">
      <button class="btn btn-primary" type="submit" :disabled="submitting">
        {{ submitting ? '提交中…' : isEdit ? '保存修改' : '提交巡查记录' }}
      </button>
      <button class="btn" type="button" @click="emit('cancel')">取消</button>
    </div>
  </form>
</template>
