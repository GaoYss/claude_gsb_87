<script setup>
import { useConfirmStore } from '@/stores/confirm'

const confirm = useConfirmStore()
</script>

<template>
  <div v-if="confirm.pending" class="modal-mask" @click.self="confirm.answer(false)">
    <div class="modal" role="dialog" aria-modal="true">
      <div class="modal-header">{{ confirm.pending.title }}</div>
      <div class="modal-body">{{ confirm.pending.message }}</div>
      <div class="modal-footer">
        <button class="btn" @click="confirm.answer(false)">取消</button>
        <button
          class="btn"
          :class="confirm.pending.tone === 'danger' ? 'btn-danger' : 'btn-primary'"
          @click="confirm.answer(true)"
        >
          {{ confirm.pending.confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

