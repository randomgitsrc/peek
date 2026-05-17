# PeekView HTML 网页渲染 技术设计文档

> 版本: 1.0
> 日期: 2026-05-18
> 状态: 草案
> 关联: 用户需求 — Agent 生成网页的发布与浏览

---

## 1. 需求背景

### 1.1 当前状态

PeekView 目前支持两种渲染模式：

- `language === 'markdown'` → MarkdownViewer（渲染 Markdown）
- 其他所有文件 → CodeViewer（代码语法高亮）

HTML 文件（`.html`）当前被当作代码处理，只显示源码高亮，不渲染成网页。

### 1.2 目标状态

Agent 生成的 HTML 网页可以通过 `peekview create` 发布，前端像浏览 Markdown 一样，直接渲染网页效果，而不是展示源码。

```
Agent 生成 index.html
       ↓
peekview create index.html
       ↓
浏览器打开 PeekView URL → 看到渲染好的网页
```

### 1.3 典型使用场景

- Agent 生成数据可视化 HTML（ECharts、D3.js 图表）
- Agent 生成报告、简历、演示文稿的单文件 HTML
- Agent 生成交互式 Demo（带内联 JS 的小工具）
- Agent 生成单文件 Web App（Tailwind CDN + Alpine.js 等）

---

## 2. 设计决策

| 问题 | 决策 | 原因 |
|------|------|------|
| 单文件 vs 多文件 | 先支持单文件，预留多文件扩展口 | Agent 可将 CSS/JS 内联到单 HTML；多文件后续迭代 |
| 渲染方式 | `<iframe srcdoc>` | 浏览器原生能力，天然沙盒隔离，无需后端改动 |
| 是否提供源码视图 | 不提供 | HTML 关注渲染结果，源码用 Download 获取 |
| 标题栏布局 | 底部操作栏，无顶部标题行 | HTML 是富媒体内容，顶部压标题栏会破坏视觉 |
| 操作项 | Copy + Download + 返回 + 主题切换 | 与其他文件类型保持一致 |

---

## 3. 技术方案

### 3.1 渲染分支

在 `EntryDetailView.vue` 中新增第三个渲染分支：

```
language === 'html'     → HtmlViewer（iframe 渲染）
language === 'markdown' → MarkdownViewer
其他                    → CodeViewer
```

### 3.2 HtmlViewer 组件

核心实现：

```html
<iframe
  :srcdoc="content"
  sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
  referrerpolicy="no-referrer"
  class="html-frame"
/>
```

**sandbox 属性说明：**

| 权限 | 说明 |
|------|------|
| `allow-scripts` | 允许 JS 执行（图表、交互必须） |
| `allow-same-origin` | 允许 localStorage、IndexedDB（部分 App 需要）|
| `allow-forms` | 允许表单提交 |
| `allow-popups` | 允许 window.open（外链跳转）|
| ❌ `allow-top-navigation` | 禁止，防止 iframe 劫持父页面跳转 |

**iframe 高度策略：**

- 默认撑满视口剩余高度（`height: calc(100vh - bottom-bar-height)`）
- 不使用动态高度（避免 postMessage 复杂度，内容在 iframe 内自己滚动）

### 3.3 底部操作栏布局

HTML 文件详情页布局：

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│          <iframe 渲染网页>               │
│          (撑满，内部自滚动)              │
│                                         │
│                                         │
├─────────────────────────────────────────┤
│  🏠  标题（截断）        Copy  Download  🌙 │  ← 底部操作栏
└─────────────────────────────────────────┘
```

与现有移动端底部 ActionBar 设计语言保持一致，不新增组件。

### 3.4 CLI 侧

`peekview create` 无需改动，已支持任意文件上传。

用法示例：

```bash
# 单文件
peekview create report.html

# 多文件（当前阶段：只渲染第一个 .html 文件，其他文件作为代码展示）
peekview create index.html style.css main.js
```

### 3.5 多文件扩展口（预留，本期不实现）

后续可在后端提供虚拟文件系统 API：

```
GET /api/v1/entries/{slug}/serve/{path}
```

让 iframe 通过 `src` 而非 `srcdoc` 加载，从而支持多文件间的相对路径引用。

---

## 4. 前端改动范围

| 文件 | 改动 | 规模 |
|------|------|------|
| `src/views/EntryDetailView.vue` | 新增 `isHtml` 计算属性；新增 HtmlViewer 渲染分支；HTML 文件时切换为底部操作栏布局 | 中 |
| `src/components/HtmlViewer.vue` | 新建，核心是 `<iframe srcdoc>` + 样式 | 小 |
| `src/stores/entry.ts` | `canWrap` / `canCopy` 逻辑排除 html 文件 | 小 |

**后端无需改动。**

---

## 5. 边界情况

| 场景 | 处理方式 |
|------|---------|
| HTML 文件包含外部资源（CDN） | 正常加载，浏览器直接请求外部 URL |
| HTML 文件包含相对路径资源 | 本期不支持，资源加载失败静默处理 |
| HTML 文件超大（>1MB） | 沿用现有文件大小限制，不单独处理 |
| 恶意 HTML（XSS） | sandbox 隔离，无法访问父页面；已足够安全 |
| 多文件 entry 中存在多个 .html | 每个文件独立渲染，通过 FileTree 切换 |

---

## 6. 实现计划

### P0 — 问题定义（本文档）
- [x] 需求分析
- [x] 技术方案
- [x] 边界情况

### P1 — 测试设计
- [ ] `HtmlViewer` 单元测试：srcdoc 正确传入
- [ ] E2E：上传 .html 文件 → 详情页显示 iframe 而非代码高亮
- [ ] E2E：底部操作栏 Copy / Download 正常工作
- [ ] E2E：切换其他文件类型时恢复正常布局

### P2 — 代码实现
- [ ] `HtmlViewer.vue`
- [ ] `EntryDetailView.vue` 改动
- [ ] `entry.ts` store 改动

### P3 — 验证
- [ ] 截图对比：HTML 文件渲染效果
- [ ] 测试：ECharts / Tailwind CDN 等外部资源加载

### P4 — 一致性检查
- [ ] CHANGELOG 更新
- [ ] FEATURES.md 更新

---

## 7. 不在本期范围内

- 多文件 HTML 的相对路径支持（后续版本）
- 源码/预览切换视图
- HTML 文件的全文搜索索引
- iframe 内容高度自适应（动态 postMessage 方案）
