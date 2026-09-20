<script setup>
import { onMounted } from 'vue'

import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import ToastHost from '@/components/common/ToastHost.vue'
import AppLayout from '@/layouts/AppLayout.vue'
import { useDictionaryStore } from '@/stores/dictionary'
import { useToastStore } from '@/stores/toast'

const dictionary = useDictionaryStore()
const toast = useToastStore()

// 字典（下拉选项 / 中文标签 / 隐患状态机）全局只拉一次
onMounted(async () => {
  try {
    await dictionary.load()
  } catch (error) {
    toast.error(error.message)
  }
})
</script>

<template>
  <AppLayout />
  <ToastHost />
  <ConfirmDialog />
</template>

