<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { createHazard, fetchHazard, updateHazard } from '@/api/hazards'
import PageHeader from '@/components/common/PageHeader.vue'
import HazardForm from '@/components/hazard/HazardForm.vue'
import { useToastStore } from '@/stores/toast'

const route = useRoute()
const router = useRouter()
const toast = useToastStore()

const isEdit = computed(() => Boolean(route.params.id))
const presetReservoirId = computed(() => route.query.reservoir_id || null)
const presetInspectionId = computed(() => route.query.inspection_id || null)

const hazard = ref(null)
const submitting = ref(false)
const loading = ref(false)

onMounted(async () => {
  if (!isEdit.value) return
  loading.value = true
  try {
    hazard.value = await fetchHazard(route.params.id)
  } catch (error) {
    toast.error(error.message)
    router.replace({ name: 'hazard-list' })
  } finally {
    loading.value = false
  }
})

async function submit(payload) {
  submitting.value = true
  try {
    const saved = isEdit.value
      ? await updateHazard(route.params.id, payload)
      : await createHazard(payload)
    toast.success(isEdit.value ? '隐患信息已更新' : `隐患 ${saved.code} 已登记`)
    router.replace({ name: 'hazard-detail', params: { id: saved.id } })
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
      :title="isEdit ? '编辑隐患' : '登记隐患'"
      description="登记后可在隐患详情页跟踪整改、验收与销号"
    />
    <div v-if="loading" class="muted">加载中…</div>
    <HazardForm
      v-else
      :initial="hazard"
      :is-edit="isEdit"
      :submitting="submitting"
      :preset-reservoir-id="presetReservoirId"
      :preset-inspection-id="presetInspectionId"
      @submit="submit"
      @cancel="router.back()"
    />
  </div>
</template>

