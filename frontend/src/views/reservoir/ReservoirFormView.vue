<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { createReservoir, fetchReservoir, updateReservoir } from '@/api/reservoirs'
import PageHeader from '@/components/common/PageHeader.vue'
import ReservoirForm from '@/components/reservoir/ReservoirForm.vue'
import { useToastStore } from '@/stores/toast'

const route = useRoute()
const router = useRouter()
const toast = useToastStore()

const isEdit = computed(() => Boolean(route.params.id))
const reservoir = ref(null)
const submitting = ref(false)
const loading = ref(false)

onMounted(async () => {
  if (!isEdit.value) return
  loading.value = true
  try {
    reservoir.value = await fetchReservoir(route.params.id)
  } catch (error) {
    toast.error(error.message)
    router.replace({ name: 'reservoir-list' })
  } finally {
    loading.value = false
  }
})

async function submit(payload) {
  submitting.value = true
  try {
    const saved = isEdit.value
      ? await updateReservoir(route.params.id, payload)
      : await createReservoir(payload)
    toast.success(isEdit.value ? '水库信息已更新' : '水库已创建')
    router.replace({ name: 'reservoir-detail', params: { id: saved.id } })
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
      :title="isEdit ? '编辑水库' : '新增水库'"
      description="水库编码创建后不可修改；带 * 的字段为必填项"
    />
    <div v-if="loading" class="muted">加载中…</div>
    <ReservoirForm
      v-else
      :initial="reservoir"
      :is-edit="isEdit"
      :submitting="submitting"
      @submit="submit"
      @cancel="router.back()"
    />
  </div>
</template>

