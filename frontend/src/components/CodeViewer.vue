<template>
  <div class="code-viewer" ref="container">
    <!-- Header with filename only -->
    <div class="code-header">
      <span class="filename">{{ filename }}</span>
      <span class="line-count" v-if="lineCount">{{ lineCount }} lines</span>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="code-loading">
      <div class="code-skeleton" v-for="i in 8" :key="i">
        <span class="skeleton-line-number"></span>
        <span class="skeleton-line-content"></span>
      </div>
    </div>

    <!-- Shiki highlighted code -->
    <div
      v-else-if="highlighted"
      class="code-content"
      :class="{ wrap }"
      v-html="highlighted"
    ></div>

    <!-- Safe fallback -->
    <div v-else class="code-content fallback" :class="{ wrap }">
      <pre><code>{{ content }}</code></pre>
    </div>

    <div v-if="isEmpty" class="empty-file">Empty file</div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import { useShiki } from '../composables/useShiki'

const props = defineProps<{
  content: string
  filename: string
  language: string | null
  lineCount: number | null
  wrap: boolean
}>()

const { highlight } = useShiki()

const highlighted = ref('')
const isLoading = ref(true)

const isEmpty = computed(() => props.content.length === 0)

async function doHighlight() {
  if (isEmpty.value) {
    highlighted.value = ''
    isLoading.value = false
    return
  }

  isLoading.value = true
  try {
    highlighted.value = await highlight(
      props.content,
      props.language || 'text',
    )
  } catch {
    highlighted.value = ''
  } finally {
    isLoading.value = false
  }
}

// Re-highlight when content or language changes
watch(
  () => [props.content, props.language],
  () => doHighlight(),
  { immediate: true },
)

onMounted(() => {
  // Line selection from URL hash
  const hash = window.location.hash
  if (hash.startsWith('#L')) {
    setTimeout(() => {
      const el = document.querySelector(hash)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' })
        el.classList.add('line-highlight')
      }
    }, 100)
  }
})
</script>

<style scoped>
.code-viewer {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: auto;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 200px);
}

.code-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  font-size: var(--font-sm);
}

.filename {
  font-weight: 600;
  color: var(--text-primary);
}

.line-count {
  color: var(--text-secondary);
  font-size: var(--font-xs);
}

/* Code content - Shiki output */
.code-content {
  padding: var(--space-3);
  overflow: auto;
  font-size: var(--font-sm);
  line-height: var(--line-height-code);
  background: var(--bg-secondary);
  flex: 1;
}

.code-content :deep(pre) {
  margin: 0;
  background: transparent !important;
  overflow: visible;
}

.code-content :deep(code) {
  font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace;
  font-size: var(--font-sm);
  line-height: var(--line-height-code);
}

/* Ensure Shiki tokens use CSS variables */
.code-content :deep(.shiki) {
  background: transparent !important;
}

.code-content :deep(.shiki code) {
  background: transparent !important;
}

/* Token colors using CSS variables */
.code-content :deep(.token.keyword) { color: var(--shiki-token-keyword); }
.code-content :deep(.token.string) { color: var(--shiki-token-string); }
.code-content :deep(.token.number) { color: var(--shiki-token-number); }
.code-content :deep(.token.comment) { color: var(--shiki-token-comment); }
.code-content :deep(.token.function) { color: var(--shiki-token-function); }
.code-content :deep(.token.class-name) { color: var(--shiki-token-class); }
.code-content :deep(.token.operator) { color: var(--shiki-token-operator); }
.code-content :deep(.token.punctuation) { color: var(--shiki-token-punctuation); }
.code-content :deep(.token.property) { color: var(--shiki-token-property); }
.code-content :deep(.token.variable) { color: var(--shiki-token-variable); }
.code-content :deep(.token.constant) { color: var(--shiki-token-constant); }
.code-content :deep(.token.builtin) { color: var(--shiki-token-builtin); }
.code-content :deep(.token.tag) { color: var(--shiki-token-tag); }
.code-content :deep(.token.attr-name) { color: var(--shiki-token-attribute); }

/* Line highlight for hash selection */
:deep(.line-highlight),
.line-highlight {
  background: var(--accent-subtle);
  border-radius: var(--radius-sm);
}

/* Word wrap */
.code-content.wrap {
  white-space: pre-wrap;
  word-break: break-all;
}

.code-content.wrap :deep(pre) {
  white-space: pre-wrap;
}

/* Fallback styling */
.fallback pre {
  margin: 0;
  font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace;
}

.empty-file {
  padding: var(--space-6);
  text-align: center;
  color: var(--text-secondary);
}

/* Loading skeleton */
.code-loading {
  padding: var(--space-3);
}

.code-skeleton {
  display: flex;
  gap: var(--space-3);
  padding: 2px 0;
}

.skeleton-line-number {
  width: 30px;
  height: 14px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.skeleton-line-content {
  flex: 1;
  height: 14px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  max-width: 60%;
}
</style>
