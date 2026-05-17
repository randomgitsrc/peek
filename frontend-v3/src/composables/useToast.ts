import { ref } from 'vue'

export interface ToastMessage {
  id: number
  message: string
  variant: 'success' | 'warning' | 'error'
  createdAt: number
}

const messages = ref<ToastMessage[]>([])
let nextId = 0

function show(message: string, variant: ToastMessage['variant'] = 'success'): void {
  const id = nextId++
  const toast: ToastMessage = { id, message, variant, createdAt: Date.now() }
  messages.value.push(toast)

  // Auto-dismiss after 3 seconds
  setTimeout(() => {
    messages.value = messages.value.filter(t => t.id !== id)
  }, 3000)
}

function remove(id: number): void {
  messages.value = messages.value.filter(t => t.id !== id)
}

export function useToast() {
  return { messages, show, remove }
}