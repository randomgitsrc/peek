<template>
  <div class="apikey-page">
    <header class="page-header">
      <div class="header-left">
        <router-link to="/" class="back-link">&larr; Back</router-link>
        <h1>API Keys</h1>
      </div>
      <button class="btn btn-primary" @click="showCreate = true">Create Key</button>
    </header>

    <div class="page-content">
      <div v-if="loading" class="loading">Loading...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="keys.length === 0" class="empty">
        No API keys yet. Create one to automate entry creation.
      </div>
      <div v-else class="key-list">
        <div v-for="key in keys" :key="key.id" class="key-card">
          <div class="key-info">
            <div class="key-name">{{ key.name }}</div>
            <div class="key-meta">
              <span class="key-prefix">{{ key.keyPrefix }}...</span>
              <span v-if="key.expiresAt" class="key-expiry" :class="{ 'expired': isExpired(key.expiresAt) }">
                {{ isExpired(key.expiresAt) ? 'Expired' : `Expires ${formatDate(key.expiresAt)}` }}
              </span>
              <span v-else class="key-expiry">No expiry</span>
              <span class="key-last-used">
                {{ key.lastUsedAt ? `Last used ${formatRelativeTime(key.lastUsedAt)}` : 'Never used' }}
              </span>
            </div>
            <div class="key-created">Created {{ formatDate(key.createdAt) }}</div>
          </div>
          <div class="key-actions">
            <button class="btn btn-danger btn-sm" @click="confirmRevoke(key)">Revoke</button>
          </div>
        </div>
      </div>

      <button v-if="keys.some(k => k.expiresAt && isExpired(k.expiresAt))" class="btn btn-secondary cleanup-btn" @click="handleCleanup">
        Cleanup Expired Keys
      </button>
    </div>

    <!-- Create Key Dialog -->
    <Teleport to="body">
      <Transition name="dialog">
        <div v-if="showCreate" class="dialog-overlay" @click.self="showCreate = false">
          <div class="dialog" role="dialog" aria-modal="true">
            <h2 v-if="!createdKey">Create API Key</h2>
            <h2 v-else>API Key Created</h2>

            <div v-if="!createdKey">
              <div class="form-field">
                <label for="key-name">Name</label>
                <input
                  id="key-name"
                  ref="nameInput"
                  v-model="newKeyName"
                  type="text"
                  placeholder="e.g., CI Bot"
                  :disabled="creating"
                  maxlength="64"
                  @keydown.enter="handleCreate"
                />
              </div>
              <div class="form-field">
                <label for="key-expiry">Expiration</label>
                <select id="key-expiry" v-model="newKeyExpiry" :disabled="creating">
                  <option value="">Never</option>
                  <option value="7d">7 days</option>
                  <option value="30d">30 days</option>
                  <option value="90d">90 days</option>
                </select>
              </div>
              <div v-if="createError" class="error">{{ createError }}</div>
              <div class="dialog-actions">
                <button class="btn btn-secondary" @click="showCreate = false" :disabled="creating">Cancel</button>
                <button class="btn btn-primary" @click="handleCreate" :disabled="creating || !newKeyName.trim()">
                  {{ creating ? 'Creating...' : 'Create' }}
                </button>
              </div>
            </div>

            <div v-else class="created-key-section">
              <p class="warning-text">
                Copy this key now — it won't be shown again!
              </p>
              <div class="key-display">
                <code class="key-value">{{ createdKey.key }}</code>
                <button class="btn btn-secondary btn-sm" @click="copyKey" :title="copied ? 'Copied!' : 'Copy'">
                  {{ copied ? 'Copied!' : 'Copy' }}
                </button>
              </div>
              <div class="dialog-actions">
                <button class="btn btn-primary" @click="dismissCreated">I've Saved It</button>
              </div>
            </div>

            <button type="button" class="dialog-close" @click="handleCloseCreate" aria-label="Close">&times;</button>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Revoke Confirmation Dialog -->
    <ConfirmDialog
      v-model:visible="showRevokeConfirm"
      title="Revoke API Key"
      :message="revokeMessage"
      confirm-label="Revoke"
      variant="destructive"
      @confirm="handleRevoke"
      @cancel="revokeTarget = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { api } from '@/api/client'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import type { ApiKey, ApiKeyCreateResult } from '@/types'

const authStore = useAuthStore()
const toast = useToast()

const keys = ref<ApiKey[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

// Create dialog
const showCreate = ref(false)
const newKeyName = ref('')
const newKeyExpiry = ref('')
const creating = ref(false)
const createError = ref<string | null>(null)
const createdKey = ref<ApiKeyCreateResult | null>(null)
const nameInput = ref<HTMLInputElement | null>(null)
const copied = ref(false)

// Revoke dialog
const showRevokeConfirm = ref(false)
const revokeTarget = ref<ApiKey | null>(null)
const revokeMessage = computed(() =>
  revokeTarget.value
    ? `Are you sure you want to revoke "${revokeTarget.value.name}"? Any scripts using this key will stop working.`
    : ''
)

watch(showCreate, async (v) => {
  if (v && !createdKey.value) {
    newKeyName.value = ''
    newKeyExpiry.value = ''
    createError.value = null
    await nextTick()
    nameInput.value?.focus()
  }
})

onMounted(() => {
  // Load keys immediately if already authenticated, or watch for auth state
  if (authStore.authState === 'authenticated') {
    loadKeys()
  }
})

// Watch auth state — load keys once authenticated
watch(() => authStore.authState, (state) => {
  if (state === 'authenticated' && keys.value.length === 0 && !loading.value && !error.value) {
    loadKeys()
  }
})

async function loadKeys() {
  loading.value = true
  error.value = null
  try {
    keys.value = await api.listApiKeys()
  } catch (err: any) {
    error.value = err?.response?.data?.error?.message || 'Failed to load API keys'
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!newKeyName.value.trim()) return
  creating.value = true
  createError.value = null
  try {
    const result = await api.createApiKey(newKeyName.value.trim(), newKeyExpiry.value || undefined)
    createdKey.value = result
    await loadKeys()
  } catch (err: any) {
    createError.value = err?.response?.data?.error?.message || 'Failed to create API key'
  } finally {
    creating.value = false
  }
}

async function copyKey() {
  if (!createdKey.value) return
  try {
    await navigator.clipboard.writeText(createdKey.value.key)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // Fallback: select text for manual copy
  }
}

function dismissCreated() {
  createdKey.value = null
  showCreate.value = false
  copied.value = false
}

function handleCloseCreate() {
  if (createdKey.value) {
    // Warn user they haven't confirmed saving the key
    if (confirm("Have you saved your API key? It won't be shown again.")) {
      dismissCreated()
    }
  } else {
    showCreate.value = false
  }
}

function confirmRevoke(key: ApiKey) {
  revokeTarget.value = key
  showRevokeConfirm.value = true
}

async function handleRevoke() {
  if (!revokeTarget.value) return
  try {
    await api.revokeApiKey(revokeTarget.value.id)
    toast.show(`Revoked "${revokeTarget.value.name}"`, 'success')
    await loadKeys()
  } catch (err: any) {
    toast.show(err?.response?.data?.error?.message || 'Failed to revoke key', 'error')
  }
  revokeTarget.value = null
}

async function handleCleanup() {
  try {
    const count = await api.cleanupExpiredKeys()
    toast.show(`Cleaned up ${count} expired key(s)`, 'success')
    await loadKeys()
  } catch (err: any) {
    toast.show(err?.response?.data?.error?.message || 'Failed to cleanup', 'error')
  }
}

function isExpired(dateStr: string | null): boolean {
  if (!dateStr) return false
  return new Date(dateStr) < new Date()
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)

  if (diffSec < 60) return 'just now'
  if (diffMin < 60) return `${diffMin}m ago`
  if (diffHour < 24) return `${diffHour}h ago`
  return `${diffDay}d ago`
}
</script>

<style scoped>
.apikey-page { min-height: 100vh; background: var(--bg-primary); display: flex; flex-direction: column; }

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-color);
}

.header-left { display: flex; align-items: center; gap: var(--space-3); }
.header-left h1 { font-size: var(--font-xl); font-weight: 700; }

.back-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: var(--font-sm);
  transition: color var(--transition-fast);
}
.back-link:hover { color: var(--accent-color); }

.page-content { padding: var(--space-4); max-width: 800px; margin: 0 auto; width: 100%; flex: 1; }
.loading, .error, .empty { text-align: center; padding: var(--space-7); color: var(--text-secondary); }
.error { color: var(--error-color); }

/* Buttons */
.btn {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  cursor: pointer;
  font-size: var(--font-sm);
  transition: all var(--transition-fast);
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--accent-color); color: var(--text-on-accent); border-color: var(--accent-color); }
.btn-primary:hover:not(:disabled) { opacity: 0.9; }
.btn-secondary { background: var(--bg-secondary); color: var(--text-primary); }
.btn-secondary:hover:not(:disabled) { background: var(--bg-tertiary); }
.btn-danger { background: var(--error-bg); color: var(--error-text); border-color: var(--error-border); }
.btn-danger:hover:not(:disabled) { opacity: 0.9; }
.btn-sm { padding: 2px 8px; font-size: var(--font-xs); }

/* Key list */
.key-list { display: flex; flex-direction: column; gap: var(--space-3); }

.key-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  gap: var(--space-3);
}

.key-name { font-weight: 600; font-size: var(--font-md); }

.key-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  font-size: var(--font-xs);
  color: var(--text-secondary);
  margin-top: 2px;
}

.key-prefix { font-family: var(--font-mono); color: var(--text-tertiary); }
.key-expiry { }
.key-expiry.expired { color: var(--error-text); font-weight: 500; }
.key-created { font-size: var(--font-xs); color: var(--text-tertiary); margin-top: 2px; }

.cleanup-btn { margin-top: var(--space-4); }

/* Dialog */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: var(--bg-overlay);
  z-index: 9997;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  max-width: 480px;
  width: 90%;
  position: relative;
}

.dialog h2 { margin: 0 0 20px; font-size: 20px; color: var(--text-primary); }

.form-field { margin-bottom: 16px; }
.form-field label { display: block; font-size: 13px; color: var(--text-secondary); margin-bottom: 4px; }

.form-field input,
.form-field select {
  width: 100%;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
}

.form-field input:focus,
.form-field select:focus {
  outline: 2px solid var(--accent-color);
  outline-offset: -1px;
}

.dialog-actions { display: flex; gap: var(--space-2); justify-content: flex-end; margin-top: 20px; }

.dialog-close {
  position: absolute;
  top: 12px;
  right: 12px;
  background: none;
  border: none;
  font-size: 20px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
}

.warning-text {
  color: var(--warning-color);
  font-weight: 500;
  font-size: var(--font-sm);
  margin-bottom: var(--space-3);
}

.key-display {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.key-value {
  flex: 1;
  font-family: var(--font-mono);
  font-size: var(--font-sm);
  word-break: break-all;
  user-select: all;
}

.dialog-enter-active { transition: opacity 0.2s ease; }
.dialog-leave-active { transition: opacity 0.2s ease; }
.dialog-enter-from { opacity: 0; }
.dialog-leave-to { opacity: 0; }
</style>
