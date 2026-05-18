<template>
  <li>
    <!-- 目录节点 -->
    <div
      v-if="node.isDir"
      class="dir-item"
      :style="{ paddingLeft: `calc(${depth} * var(--space-3))` }"
      @click="toggleDir(node.fullPath)"
    >
      <span class="dir-toggle">{{ isExpanded ? '▾' : '▸' }}</span>
      <span class="dir-icon">📁</span>
      <span class="dir-name">{{ node.name }}</span>
    </div>

    <!-- 文件节点 -->
    <div
      v-else
      :class="['file-item', { active: node.file?.id === activeFileId }]"
      :style="{ paddingLeft: `calc(${depth} * var(--space-3))` }"
      @click="node.file && $emit('select', node.file)"
    >
      <span class="file-icon">{{ getFileIcon(node.file!) }}</span>
      <span class="file-name">{{ node.name }}</span>
    </div>

    <!-- 目录子节点（展开时） -->
    <ul v-if="node.isDir && isExpanded" class="dir-children">
      <TreeNodeItem
        v-for="child in node.children"
        :key="child.fullPath"
        :node="child"
        :depth="depth + 1"
        :active-file-id="activeFileId"
        @select="$emit('select', $event)"
      />
    </ul>
  </li>
</template>

<script setup lang="ts">
import { inject, computed, type Ref } from 'vue'
import type { File, TreeNode } from '@/types'
import { EXPAND_KEY } from '@/components/FileTree.vue'

const props = defineProps<{
  node: TreeNode
  depth: number
  activeFileId: number | null
}>()

defineEmits<{
  select: [file: File]
}>()

interface ExpandContext {
  expandedPaths: Ref<Set<string>>
  toggleDir: (path: string) => void
}

const { expandedPaths, toggleDir } = inject<ExpandContext>(EXPAND_KEY)!
const isExpanded = computed(() => expandedPaths.value.has(props.node.fullPath))

function getFileIcon(file: File): string {
  if (file.isBinary) return '📦'
  if (file.language === 'markdown') return '📝'
  if (file.language === 'python') return '🐍'
  if (file.language === 'javascript' || file.language === 'typescript') return '📜'
  if (file.language === 'html') return '🌐'
  if (file.language === 'css') return '🎨'
  return '📄'
}
</script>

<style scoped>
.dir-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding-top: var(--space-2);
  padding-bottom: var(--space-2);
  padding-right: var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
  font-weight: 600;
}

.dir-item:hover { background: var(--bg-tertiary); }

.dir-toggle { font-size: var(--font-xs); color: var(--text-secondary); flex-shrink: 0; }
.dir-icon { font-size: var(--font-md); flex-shrink: 0; }

.dir-name {
  font-size: var(--font-sm);
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding-top: var(--space-2);
  padding-bottom: var(--space-2);
  padding-right: var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.file-item:hover { background: var(--bg-tertiary); }
.file-item.active { background: var(--accent-light); }
.file-item.active .file-name { color: var(--accent-color); font-weight: 500; }
.file-icon { font-size: var(--font-md); flex-shrink: 0; }

.file-name {
  font-size: var(--font-sm);
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dir-children { list-style: none; padding: 0; margin: 0; }
</style>