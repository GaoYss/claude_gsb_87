import { defineStore } from 'pinia'
import { ref } from 'vue'

/** 极简确认弹窗：await confirm.ask('确认删除？') */
export const useConfirmStore = defineStore('confirm', () => {
  const pending = ref(null)

  function ask(message, options = {}) {
    return new Promise((resolve) => {
      pending.value = {
        message,
        title: options.title || '操作确认',
        confirmText: options.confirmText || '确定',
        tone: options.tone || 'danger',
        resolve,
      }
    })
  }

  function answer(value) {
    if (!pending.value) return
    pending.value.resolve(value)
    pending.value = null
  }

  return { pending, ask, answer }
})

