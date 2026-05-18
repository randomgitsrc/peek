/**
 * FileTree 单元测试
 *
 * 覆盖 spec-file-tree.md UT-TREE-01~13：
 * - buildTree 层级/扁平/混合/边界场景
 * - 折叠状态管理
 * - 文件选择事件
 */

import { describe, it, expect } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import FileTree from '@/components/FileTree.vue'
import type { File } from '@/types'

// ─── 测试数据工厂 ──────────────────────────────────────────────────────

function makeFile(id: number, filename: string, path: string | null, language: string | null = null, isBinary = false): File {
  return { id, filename, path, language, isBinary, size: 100, lineCount: 10 }
}

// ─── buildTree 逻辑验证 ─────────────────────────────────────────────────

describe('buildTree 逻辑', () => {
  // 直接测试组件 computed 输出
  function getTreeNodes(files: File[]): any[] {
    const wrapper = mount(FileTree, {
      props: { files, activeFileId: null },
    })
    // treeNodes 是 computed，通过 vm 访问
    return (wrapper.vm as any).treeNodes
  }

  it('UT-TREE-01: 层级文件 → 正确嵌套树', () => {
    const files = [
      makeFile(1, 'layout.css', 'css/layout.css', 'css'),
      makeFile(2, 'app.js', 'js/app.js', 'javascript'),
      makeFile(3, 'hero.png', 'assets/images/hero.png', null, true),
      makeFile(4, 'index.html', null, 'html'),
    ]
    const tree = getTreeNodes(files)

    // 根节点：3 dirs + 1 file
    expect(tree.length).toBe(4)
    // dirs: assets, css, js (sorted)
    const dirNames = tree.filter(n => n.isDir).map(n => n.name)
    expect(dirNames).toEqual(['assets', 'css', 'js'])
    // file: index.html
    const fileNames = tree.filter(n => !n.isDir).map(n => n.name)
    expect(fileNames).toEqual(['index.html'])

    // css dir has 1 child
    const cssDir = tree.find(n => n.name === 'css')
    expect(cssDir!.children.length).toBe(1)
    expect(cssDir!.children[0].name).toBe('layout.css')
    expect(cssDir!.children[0].isDir).toBe(false)

    // assets/images nested
    const assetsDir = tree.find(n => n.name === 'assets')
    expect(assetsDir!.children.length).toBe(1)
    expect(assetsDir!.children[0].name).toBe('images')
    expect(assetsDir!.children[0].isDir).toBe(true)
    expect(assetsDir!.children[0].children[0].name).toBe('hero.png')
  })

  it('UT-TREE-02: 扁平文件（path 全 null） → 纯文件节点', () => {
    const files = [
      makeFile(1, 'index.html', null, 'html'),
      makeFile(2, 'style.css', null, 'css'),
      makeFile(3, 'app.js', null, 'javascript'),
    ]
    const tree = getTreeNodes(files)

    expect(tree.every(n => !n.isDir)).toBe(true)
    expect(tree.map(n => n.name)).toEqual(['app.js', 'index.html', 'style.css'])
  })

  it('UT-TREE-03: 混合层级 + 根级文件 → 根文件在顶层', () => {
    const files = [
      makeFile(1, 'index.html', null, 'html'),
      makeFile(2, 'style.css', 'css/style.css', 'css'),
    ]
    const tree = getTreeNodes(files)

    // 1 dir (css) + 1 file (index.html)
    expect(tree.length).toBe(2)
    const dirNode = tree.find(n => n.isDir)
    const fileNode = tree.find(n => !n.isDir)
    expect(dirNode!.name).toBe('css')
    expect(fileNode!.name).toBe('index.html')
  })

  it('UT-TREE-04: 排序：目录优先 + name 升序', () => {
    const files = [
      makeFile(1, 'z.js', 'z/z.js', 'javascript'),
      makeFile(2, 'a.css', 'a/a.css', 'css'),
      makeFile(3, 'root.txt', null),
      makeFile(4, 'm.html', 'm/m.html', 'html'),
    ]
    const tree = getTreeNodes(files)

    // dirs first: a, m, z
    // then files: root.txt
    expect(tree.map(n => n.name)).toEqual(['a', 'm', 'z', 'root.txt'])
  })

  it('UT-TREE-08: 空字符串 path → 降级到 filename', () => {
    const files = [
      makeFile(1, 'index.html', '', 'html'),
    ]
    const tree = getTreeNodes(files)
    expect(tree.length).toBe(1)
    expect(tree[0].name).toBe('index.html')
    expect(tree[0].isDir).toBe(false)
  })

  it('UT-TREE-09: 前导斜杠 path → 清洗后正确树', () => {
    const files = [
      makeFile(1, 'style.css', '/css/style.css', 'css'),
    ]
    const tree = getTreeNodes(files)
    expect(tree.length).toBe(1)
    expect(tree[0].name).toBe('css')
    expect(tree[0].children[0].name).toBe('style.css')
  })

  it('UT-TREE-10: 尾部斜杠 path → 清洗后正确树', () => {
    const files = [
      makeFile(1, 'style.css', 'css/style.css/', 'css'),
    ]
    const tree = getTreeNodes(files)
    expect(tree[0].name).toBe('css')
    expect(tree[0].children[0].name).toBe('style.css')
  })

  it('UT-TREE-11: 不同目录同名文件（a/x.js + b/x.js）→ 两个独立节点', () => {
    const files = [
      makeFile(1, 'x.js', 'a/x.js', 'javascript'),
      makeFile(2, 'x.js', 'b/x.js', 'javascript'),
    ]
    const tree = getTreeNodes(files)
    expect(tree.length).toBe(2)
    // Both dirs have x.js
    expect(tree[0].children[0].name).toBe('x.js')
    expect(tree[1].children[0].name).toBe('x.js')
    // Different IDs
    expect(tree[0].children[0].file.id).toBe(1)
    expect(tree[1].children[0].file.id).toBe(2)
  })

  it('UT-TREE-12: 深层嵌套（5 级） → 正确层级结构', () => {
    const files = [
      makeFile(1, 'leaf.txt', 'a/b/c/d/e/leaf.txt'),
    ]
    const tree = getTreeNodes(files)

    let current = tree
    for (const expected of ['a', 'b', 'c', 'd', 'e']) {
      expect(current.length).toBe(1)
      expect(current[0].name).toBe(expected)
      expect(current[0].isDir).toBe(true)
      current = current[0].children
    }
    expect(current.length).toBe(1)
    expect(current[0].name).toBe('leaf.txt')
    expect(current[0].isDir).toBe(false)
  })
})

// ─── 折叠与交互 ──────────────────────────────────────────────────────

describe('折叠与交互', () => {
  const files = [
    makeFile(1, 'layout.css', 'css/layout.css', 'css'),
    makeFile(2, 'app.js', 'js/app.js', 'javascript'),
    makeFile(3, 'index.html', null, 'html'),
  ]

  it('UT-TREE-05: 点击目录切换折叠', async () => {
    const wrapper = mount(FileTree, {
      props: { files, activeFileId: null },
    })
    await flushPromises()

    // 默认全部展开
    const expanded = (wrapper.vm as any).expandedPaths
    expect(expanded.has('css')).toBe(true)
    expect(expanded.has('js')).toBe(true)

    // 点击目录折叠
    const dirItem = wrapper.find('.dir-item')
    await dirItem.trigger('click')
    await flushPromises()

    // css should now be collapsed (or js — whichever is first dir-item)
    // Since dirs are sorted: css first, js second
    expect(expanded.has('css')).toBe(false)
  })

  it('UT-TREE-06: activeFile 在折叠目录内 → 自动展开', async () => {
    const wrapper = mount(FileTree, {
      props: { files, activeFileId: null },
    })
    await flushPromises()

    // Collapse css directory first
    const expanded = (wrapper.vm as any).expandedPaths
    expanded.delete('css')

    // Select a file inside css dir
    await wrapper.setProps({ activeFileId: 1 })
    await flushPromises()

    expect(expanded.has('css')).toBe(true)
  })

  it('UT-TREE-07: 点击文件 emit select 事件', async () => {
    const wrapper = mount(FileTree, {
      props: { files, activeFileId: null },
    })
    await flushPromises()

    // 找到 index.html 的文件行（在顶层，不在目录内）
    const fileItems = wrapper.findAll('.file-item')
    // layout.css 在 css 目录内（已展开），app.js 在 js 目录内，index.html 在顶层
    // 树排序：css(dir) → js(dir) → index.html(file)
    // 所以最后一个 .file-item 是 index.html
    const indexItem = fileItems[fileItems.length - 1]
    await indexItem.trigger('click')

    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')![0][0]).toMatchObject({ id: 3, filename: 'index.html' })
  })

  it('UT-TREE-13: files 变化 → expandedPaths 重置', async () => {
    const wrapper = mount(FileTree, {
      props: { files, activeFileId: null },
    })
    await flushPromises()

    // Check initial expanded state
    const expanded = (wrapper.vm as any).expandedPaths
    expect(expanded.size).toBe(2) // css + js

    // Collapse a directory
    expanded.delete('css')
    expect(expanded.size).toBe(1) // js only

    // Change files prop + activeFileId (simulate entry switch)
    const newFiles = [
      makeFile(10, 'main.py', null, 'python'),
    ]
    await wrapper.setProps({ files: newFiles, activeFileId: null })
    await flushPromises()

    // After setProps, expandedPaths ref's inner value was replaced
    // Re-read from vm to get the latest reference
    const newExpanded = (wrapper.vm as any).expandedPaths
    expect(newExpanded.size).toBe(0)
  })
})