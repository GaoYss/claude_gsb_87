<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { createInspection, fetchInspection, updateInspection } from '@/api/inspections'
import PageHeader from '@/components/common/PageHeader.vue'
import InspectionForm from '@/components/inspection/InspectionForm.vue'
import { useConfirmStore } from '@/stores/confirm'
import { useToastStore } from '@/stores/toast'

const route = useRoute()
const router = useRouter()
const toast = useToastStore()
const confirm = useConfirmStore()

const isEdit = computed(() => Boolean(route.params.id))
const presetReservoirId = computed(() => route.query.reservoir_id || null)

const inspection = ref(null)
const submitting = ref(false)
const loading = ref(false)

onMounted(async () => {
  if (!isEdit.value) return
  loading.value = true
  try {
    inspection.value = await fetchInspection(route.params.id)
  } catch (error) {
    toast.error(error.message)
    router.replace({ name: 'inspection-list' })
  } finally {
    loading.value = false
  }
})

async function submit(payload) {
  submitting.value = true
  try {
    const saved = isEdit.value
      ? await updateInspection(route.params.id, payload)
      : await createInspection(payload)
    toast.success(isEdit.value ? '巡查记录已更新' : `巡查记录 ${saved.code} 已提交`)

    // 巡查发现异常时，顺着业务流程引导用户登记隐患
    const abnormalItems = (saved.items || []).filter((item) => item.result === 'abnormal')
    if (!isEdit.value && abnormalItems.length) {
      const ok = await confirm.ask(
        `本次巡查有 ${abnormalItems.length} 项异常，是否立即登记隐患？`,
        { title: '发现异常', confirmText: '登记隐患', tone: 'primary' },
      )
      if (ok) {
        router.replace({
          name: 'hazard-create',
          query: { reservoir_id: saved.reservoir_id, inspection_id: saved.id },
        })
        return
      }
    }
    router.replace({ name: 'inspection-detail', params: { id: saved.id } })
  } catch (error) {
    toast.error(error.message)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <PageHeader
      :title="isEdit ? '编辑巡查记录' : '录入巡查记录'"
      description="按部位逐项记录检查结果；存在异常项时建议同时登记隐患"
    />
    <div v-if="loading" class="muted">加载中…</div>
    <InspectionForm
      v-else
      :initial="inspection"
      :is-edit="isEdit"
      :submitting="submitting"
      :preset-reservoir-id="presetReservoirId"
      @submit="submit"
      @cancel="router.back()"
    />
  </div>
</template>

