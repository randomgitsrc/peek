# 归档文档

> 此目录包含已完成或废弃的文档，保留供历史参考。

## 目录结构

```
docs/archived/
├── specs/                         # MVP 阶段规格文档（已完成）
│   ├── spec-requirements.md       # 需求规格 v2.1（已由 spec-user-auth.md 接续）
│   ├── spec-design.md             # 技术设计 v2.0（数据模型已过时）
│   ├── spec-test-plan.md          # 测试计划 v3.0（不含认证测试）
│   ├── spec-design-review.md      # 架构师评审
│   ├── spec-review-report.md      # PM 评审
│   ├── spec-test-review.md        # QA 评审
│   └── VERSIONS.md                # 版本追踪
├── plans/                         # 已完成的实现计划
│   ├── impl-plan.md               # MVP 16 任务实现计划
│   ├── impl-plan-user-auth.md     # 用户认证实现计划
│   ├── impl-plan-remote-cli.md    # 远程 CLI 实现计划
│   ├── impl-plan-apikey.md        # API Key 管理实现计划
│   └── work-plan.md               # 软件工程化工作计划
├── reviews/                       # 已解决的评审
│   ├── eng-review.md              # Eng 架构评审（CRITICAL/HIGH 已全部修复）
│   ├── pre-impl-audit.md          # 编码前审查汇总（已修复）
│   ├── apikey-design-review.md    # API Key 设计评审 v1（已由 v2 接续）
│   └── apikey-design-review-v2.md # API Key 设计评审 v2（已实现）
├── P0-T19/ ~ P4-T19/             # 软件工程化检查点文档
├── superpowers/                   # AI 辅助设计历史
├── design/                        # UI 设计规范 v1.0（已过时）
├── test-results/                  # 历史 E2E 测试结果
├── impl-plan.restore.md           # v1 计划还原点
├── RELEASE_CHECKLIST.md           # 发布检查清单（已合并到 release.md）
└── P0_*.md ~ P3_*.md              # P0-P3 阶段过程文档
```

## 归档说明

| 子目录 | 归档原因 | 归档日期 |
|--------|----------|----------|
| `specs/` | MVP 阶段规格，数据模型和 API 端点已过时（缺少 auth/apikeys 表、visibility 字段） | 2026-05-17 |
| `plans/` | 所有计划已实现完成 | 2026-05-17 |
| `reviews/` | Eng 评审和预实现审计中的 CRITICAL/HIGH 问题已全部修复；API Key 评审已实现 | 2026-05-17 |
| `P0-T19/` ~ `P4-T19/` | 软件工程化流程的过程产物 | 2026-05-08 |
| `superpowers/` | AI 辅助设计历史 | 2026-05-08 |
| `design/` | UI 设计规范 v1.0 已过时 | 2026-05-08 |
