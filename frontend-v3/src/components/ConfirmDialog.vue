<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="visible" class="confirm-overlay" @click.self="cancel">
        <div
          class="confirm-dialog"
          role="alertdialog"
          aria-labelledby="confirm-title"
          aria-describedby="confirm-desc"
        >
          <h3 id="confirm-title" class="confirm__title">{{ title }}</h3>
          <p id="confirm-desc" class="confirm__message">{{ message }}</p>
          <div class="confirm__actions">
            <button class="confirm__btn confirm__btn--cancel" @click="cancel" ref="cancelBtn">
              Cancel
            </button>
            <button :class="['confirm__btn', `confirm__btn--${variant}`]" @click="confirm">
              {{ confirmLabel }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

defineProps<{
  title: string
  message: string
  confirmLabel?: string
  variant?: 'destructive' | 'primary'
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const visible = defineModel<boolean>('visible', { default: false })
const cancelBtn = ref<HTMLButtonElement | null>(null)

watch(visible, async (v) => {
  if (v) {
    await nextTick()
    cancelBtn.value?.focus()
  }
})

function confirm() {
  visible.value = false
  emit('confirm')
}

function cancel() {
  visible.value = false
  emit('cancel')
}
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: var(--bg-overlay);
  z-index: 9998;
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-dialog {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
}

.confirm__title {
  margin: 0 0 12px;
  font-size: 18px;
  color: var(--text-primary);
}

.confirm__message {
  margin: 0 0 20px;
  font-size: 14px;
  color: var(--text-secondary);
}

.confirm__actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.confirm__btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
}

.confirm__btn--cancel:hover {
  background: var(--bg-tertiary);
}

.confirm__btn--destructive {
  background: var(--error-bg);
  color: var(--error-text);
  border-color: var(--error-border);
}

.confirm__btn--destructive:hover {
  opacity: 0.9;
}

.confirm__btn--primary {
  background: var(--accent-color);
  color: var(--text-on-accent);
  border-color: var(--accent-color);
}

.dialog-enter-active { transition: opacity 0.2s ease; }
.dialog-leave-active { transition: opacity 0.2s ease; }
.dialog-enter-from { opacity: 0; }
.dialog-leave-to { opacity: 0; }
</style>