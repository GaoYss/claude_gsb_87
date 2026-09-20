import { defineStore } from 'pinia'
import { ref } from 'vue'

let seed = 0

export const useToastStore = defineStore('toast', () => {
  const items = ref([])

  function dismiss(id) {
    items.value = items.value.filter((item) => item.id !== id)
  }

  function push(message, type = 'info', timeout = 3200) {
    const id = (seed += 1)
    items.value.push({ id, message, type })
    if (timeout) setTimeout(() => dismiss(id), timeout)
    return id
  }

  return {
    items,
    push,
    dismiss,
    success: (message) => push(message, 'success'),
    error: (message) => push(message, 'error', 6000),
    info: (message) => push(message, 'info'),
  }
})

