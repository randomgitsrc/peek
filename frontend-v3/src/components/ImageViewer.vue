<template>
  <div class="image-viewer" data-testid="image-viewer">
    <!-- 性能警告（5MB ~ 10MB） -->
    <div
      v-if="showSizeWarning"
      data-testid="size-warning"
      class="image-warning"
    >
      <span class="warning-icon">⚡</span>
      <span class="warning-text">
        文件较大（{{ fileSizeLabel }}），加载可能需要一点时间。
      </span>
    </div>

    <!-- 手动触发（> 10MB） -->
    <div v-if="showManualRender" class="image-manual-render">
      <div class="manual-render-info">
        <span class="file-size-icon">📄</span>
        <p>文件较大（{{ fileSizeLabel }}），自动加载已关闭以防止页面卡顿。</p>
        <button
          data-testid="manual-render-btn"
          class="btn btn-primary"
          @click="triggerManualRender"
        >
          点击加载
        </button>
      </div>
    </div>

    <!-- Loading 态 -->
    <div
      v-if="isLoading"
      data-testid="image-loading"
      class="image-loading"
    >
      <div class="loading-spinner" />
      <span>加载中...</span>
    </div>

    <!-- Error 态 -->
    <div
      v-if="hasError"
      data-testid="image-error"
      class="image-error"
    >
      <span>图片加载失败</span>
    </div>

    <!-- 图片 -->
    <div v-if="dataUri" class="image-container" :class="{ 'image-zoomed': isZoomed }">
      <img
        :src="dataUri"
        :alt="filename"
        data-testid="image-content"
        class="image-content"
        :class="{ 'image-content-zoomed': isZoomed }"
        @load="onLoad"
        @error="onError"
        @click="toggleZoom"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '@/api/client'
import { guessMimeType } from '@/utils/mime'

const props = defineProps<{
  filename: string
  slug: string
  fileId: number
}>()

// ── 大文件阈值 ──────────────────────────────────────────────────
const SIZE_WARN = 5 * 1024 * 1024   // 5MB
const SIZE_BLOCK = 10 * 1024 * 1024  // 10MB

// ── 状态 ────────────────────────────────────────────────────────
const dataUri = ref<string | null>(null)
const isLoading = ref(false)
const hasError = ref(false)
const isZoomed = ref(false)
const manuallyTriggered = ref(false)
const fileSize = ref(0)

// ── 大文件策略 ──────────────────────────────────────────────────
const fileSizeLabel = computed(() => {
  const size = fileSize.value
  if (size >= SIZE_BLOCK) return `${(size / (1024 * 1024)).toFixed(1)} MB`
  return `${(size / 1024).toFixed(0)} KB`
})

const showSizeWarning = computed(() => fileSize.value >= SIZE_WARN && fileSize.value < SIZE_BLOCK)
const isBlockedBySize = computed(() => fileSize.value >= SIZE_BLOCK)
const showManualRender = computed(() => isBlockedBySize.value && !manuallyTriggered.value)

function triggerManualRender() {
  manuallyTriggered.value = true
}

function toggleZoom() {
  isZoomed.value = !isZoomed.value
}

// ── 加载图片 ────────────────────────────────────────────────────
async function loadImage() {
  const mimeType = guessMimeType(props.filename)
  if (!mimeType) {
    hasError.value = true
    return
  }

  isLoading.value = true
  hasError.value = false

  try {
    const base64 = await api.getFileAsBase64(props.slug, props.fileId)
    dataUri.value = `data:${mimeType};base64,${base64}`
    // Estimate file size from base64 length (base64 ≈ 1.33x original)
    fileSize.value = Math.round(base64.length * 3 / 4)
  } catch {
    hasError.value = true
    isLoading.value = false
  }
}

onMounted(() => {
  loadImage()
})

watch(() => props.fileId, () => {
  dataUri.value = null
  isZoomed.value = false
  manuallyTriggered.value = false
  loadImage()
})

watch(manuallyTriggered, (triggered) => {
  if (triggered) loadImage()
})

// ── 事件处理 ────────────────────────────────────────────────────
function onLoad() {
  isLoading.value = false
}

function onError() {
  isLoading.value = false
  hasError.value = true
}
</script>

<style scoped>
.image-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.image-warning {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  font-size: var(--font-xs);
  background: var(--accent-light);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary);
  flex-shrink: 0;
}

.warning-icon {
  flex-shrink: 0;
}

.warning-text {
  flex: 1;
}

.image-manual-render {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.manual-render-info {
  text-align: center;
  color: var(--text-secondary);
}

.file-size-icon {
  font-size: 48px;
  display: block;
  margin-bottom: var(--space-3);
}

.manual-render-info p {
  margin-bottom: var(--space-4);
  font-size: var(--font-sm);
}

.btn-primary {
  padding: var(--space-2) var(--space-4);
  background: var(--accent-color);
  color: var(--text-on-accent);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--font-sm);
}

.btn-primary:hover {
  opacity: 0.9;
}

.image-loading {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: var(--font-sm);
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.image-error {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--error-text);
  font-size: var(--font-sm);
}

.image-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.image-container.image-zoomed {
  overflow: auto;
  align-items: flex-start;
  justify-content: flex-start;
}

.image-content {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  cursor: zoom-in;
  transition: none;
}

.image-content-zoomed {
  max-width: none;
  max-height: none;
  object-fit: none;
  cursor: zoom-out;
}
</style>