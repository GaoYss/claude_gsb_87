<script setup>
import { reactive, ref, watch } from 'vue'

import FormField from '@/components/common/FormField.vue'
import { useDictionaryStore } from '@/stores/dictionary'
import { cleanPayload } from '@/utils/form'

const props = defineProps({
  initial: { type: Object, default: null },
  submitting: { type: Boolean, default: false },
  isEdit: { type: Boolean, default: false },
})

const emit = defineEmits(['submit', 'cancel'])

const dictionary = useDictionaryStore()

function buildState(source) {
  return {
    code: source?.code ?? '',
    name: source?.name ?? '',
    region: source?.region ?? '',
    basin: source?.basin ?? '',
    dam_type: source?.dam_type ?? '',
    safety_class: source?.safety_class ?? 'class_two',
    status: source?.status ?? 'normal',
    total_capacity: source?.total_capacity ?? '',
    normal_level: source?.normal_level ?? '',
    flood_limit_level: source?.flood_limit_level ?? '',
    dam_height: source?.dam_height ?? '',
    dam_length: source?.dam_length ?? '',
    build_year: source?.build_year ?? '',
    manager: source?.manager ?? '',
    manager_phone: source?.manager_phone ?? '',
    location: source?.location ?? '',
    remark: source?.remark ?? '',
  }
}

const form = reactive(buildState(props.initial))
const error = ref('')

watch(
  () => props.initial,
  (value) => Object.assign(form, buildState(value)),
)

function submit() {
  if (!form.name.trim()) {
    error.value = '请填写水库名称'
    return
  }
  if (!form.region.trim()) {
    error.value = '请填写所在行政区'
    return
  }
  if (!props.isEdit && !/^[A-Za-z0-9][A-Za-z0-9_-]{1,31}$/.test(form.code.trim())) {
    error.value = '水库编码需为 2-32 位字母、数字、下划线或短横线'
    return
  }
  error.value = ''

  const payload = cleanPayload(form, {
    numberFields: ['total_capacity', 'normal_level', 'flood_limit_level', 'dam_height', 'dam_length'],
    intFields: ['build_year'],
    textFields: ['code', 'name', 'region', 'basin', 'manager', 'manager_phone', 'location', 'remark'],
  })
  if (props.isEdit) delete payload.code
  emit('submit', payload)
}
</script>

<template>
  <form @submit.prevent="submit">
    <section class="card">
      <header class="card-header"><div class="card-title">基本信息</div></header>
      <div class="card-body">
        <div class="form-grid">
          <FormField label="水库编码" required hint="全局唯一，例如 SK-3301001">
            <input v-model="form.code" class="input" :disabled="isEdit" placeholder="SK-3301001" />
          </FormField>
          <FormField label="水库名称" required>
            <input v-model="form.name" class="input" placeholder="例如 青龙湾水库" />
          </FormField>
          <FormField label="所在行政区" required>
            <input v-model="form.region" class="input" placeholder="例如 临江区" />
          </FormField>
          <FormField label="所属流域">
            <input v-model="form.basin" class="input" placeholder="例如 清溪流域" />
          </FormField>
          <FormField label="坝址位置">
            <input v-model="form.location" class="input" placeholder="例如 青溪镇青龙湾村" />
          </FormField>
        </div>
      </div>
    </section>

    <section class="card">
      <header class="card-header"><div class="card-title">工程参数</div></header>
      <div class="card-body">
        <div class="form-grid">
          <FormField label="坝型">
            <select v-model="form.dam_type" class="select">
              <option value="">未填写</option>
              <option v-for="item in dictionary.options('dam_type')" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
          </FormField>
          <FormField label="大坝安全类别">
            <select v-model="form.safety_class" class="select">
              <option v-for="item in dictionary.options('safety_class')" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
          </FormField>
          <FormField label="总库容（万 m³）">
            <input v-model="form.total_capacity" class="input" type="number" step="0.01" min="0" />
          </FormField>
          <FormField label="正常蓄水位（m）">
            <input v-model="form.normal_level" class="input" type="number" step="0.01" min="0" />
          </FormField>
          <FormField label="汛限水位（m）">
            <input v-model="form.flood_limit_level" class="input" type="number" step="0.01" min="0" />
          </FormField>
          <FormField label="最大坝高（m）">
            <input v-model="form.dam_height" class="input" type="number" step="0.01" min="0" />
          </FormField>
          <FormField label="坝顶长度（m）">
            <input v-model="form.dam_length" class="input" type="number" step="0.01" min="0" />
          </FormField>
          <FormField label="建成年份">
            <input v-model="form.build_year" class="input" type="number" min="1900" max="2100" />
          </FormField>
        </div>
      </div>
    </section>

    <section class="card">
      <header class="card-header"><div class="card-title">运行管理</div></header>
      <div class="card-body">
        <div class="form-grid">
          <FormField label="运行状态">
            <select v-model="form.status" class="select">
              <option v-for="item in dictionary.options('reservoir_status')" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
          </FormField>
          <FormField label="管理单位">
            <input v-model="form.manager" class="input" placeholder="例如 临江区水利工程管理所" />
          </FormField>
          <FormField label="责任人电话">
            <input v-model="form.manager_phone" class="input" placeholder="0571-88880001" />
          </FormField>
          <FormField label="备注" class="span-2">
            <textarea v-model="form.remark" class="textarea" placeholder="工程特征、注意事项等" />
          </FormField>
        </div>
      </div>
    </section>

    <p v-if="error" class="muted" style="color: var(--danger)">{{ error }}</p>

    <div class="form-actions">
      <button class="btn btn-primary" type="submit" :disabled="submitting">
        {{ submitting ? '提交中…' : isEdit ? '保存修改' : '创建水库' }}
      </button>
      <button class="btn" type="button" @click="emit('cancel')">取消</button>
    </div>
  </form>
</template>

