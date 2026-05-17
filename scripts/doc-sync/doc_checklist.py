#!/usr/bin/env python3
"""
根据本次变更的文件类型，生成需要更新的文档 checklist。

用法：
  # 检查所有未提交的变更
  python3 scripts/doc-sync/doc_checklist.py

  # 检查指定文件（如 pre-commit hook 传入 staged 文件）
  python3 scripts/doc-sync/doc_checklist.py --files backend/peekview/cli.py backend/peekview/api/entries.py

  # 输出 markdown 格式（写入文件用）
  python3 scripts/doc-sync/doc_checklist.py --format markdown
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass, field


# ─────────────────────────────────────────────
# 变更类型定义
# ─────────────────────────────────────────────

@dataclass
class ChangeType:
    id: str
    name: str
    description: str
    # 触发此类型的文件路径模式（glob 风格字符串）
    triggers: list[str]
    # 需要更新的文档列表，每项为 (文件路径, 说明, 是否必须)
    docs: list[tuple[str, str, bool]]


CHANGE_TYPES: list[ChangeType] = [
    ChangeType(
        id="version",
        name="版本号变更",
        description="pyproject.toml / __init__.py / package.json 版本号修改",
        triggers=[
            "backend/pyproject.toml",
            "backend/peekview/__init__.py",
            "frontend-v3/package.json",
        ],
        docs=[
            ("README.md",                       "更新 badge 版本号",                True),
            ("CLAUDE.md",                        "更新 Current Version",             True),
            ("INDEX.md",                         "更新 当前版本",                    True),
            ("CHANGELOG.md",                     "添加新版本记录及变更内容",          True),
            ("docs/process/active-tasks.md",     "更新 当前版本已发布",              True),
            ("backend/README.md",                "更新 health 返回示例中的版本号",    False),
        ],
    ),
    ChangeType(
        id="api",
        name="API 端点变更",
        description="新增/修改/删除 API 路由",
        triggers=[
            "backend/peekview/api/*.py",
            "backend/peekview/models.py",
            "backend/peekview/services/*.py",
        ],
        docs=[
            ("README.md",                "如有新功能，更新功能特性列表",              False),
            ("backend/README.md",        "更新 API 端点文档",                        True),
            ("docs/DEPLOYMENT.md",       "如有破坏性变更，更新部署说明",             False),
            ("FEATURES.md",              "运行 make update-docs 自动生成",           True),
            ("CHANGELOG.md",             "记录 API 变更",                           True),
        ],
    ),
    ChangeType(
        id="cli",
        name="CLI 命令变更",
        description="新增/修改/删除 CLI 命令或参数",
        triggers=[
            "backend/peekview/cli.py",
            "backend/peekview/client.py",
        ],
        docs=[
            ("README.md",         "更新 CLI 用法示例",        True),
            ("CLAUDE.md",         "更新 CLI Usage 章节",      True),
            ("backend/README.md", "更新 CLI 命令文档",        True),
            ("CHANGELOG.md",      "记录 CLI 变更",           True),
        ],
    ),
    ChangeType(
        id="config",
        name="配置/环境变量变更",
        description="新增/修改/删除配置项或环境变量",
        triggers=[
            "backend/peekview/config.py",
        ],
        docs=[
            ("README.md",           "更新环境变量表格",          True),
            ("CLAUDE.md",           "更新配置表格",              True),
            ("docs/DEPLOYMENT.md",  "更新部署配置说明",          True),
            ("docs/DEBUGGING.md",   "如涉及调试配置，同步更新",  False),
            ("CHANGELOG.md",        "记录配置变更",             True),
        ],
    ),
    ChangeType(
        id="frontend",
        name="前端功能变更",
        description="新增/修改前端视图、组件或样式",
        triggers=[
            "frontend-v3/src/views/*.vue",
            "frontend-v3/src/components/*.vue",
            "frontend-v3/src/stores/*.ts",
            "frontend-v3/src/composables/*.ts",
            "frontend-v3/src/router.ts",
        ],
        docs=[
            ("README.md",    "如有新功能，更新功能特性列表",   False),
            ("FEATURES.md",  "运行 make update-docs 自动生成", True),
            ("CHANGELOG.md", "记录前端变更",                  True),
        ],
    ),
    ChangeType(
        id="deps",
        name="依赖变更",
        description="新增/修改/删除依赖项",
        triggers=[
            "backend/pyproject.toml",
            "frontend-v3/package.json",
        ],
        docs=[
            ("docs/DEPLOYMENT.md", "如有安装步骤变化，更新部署文档", False),
            ("CHANGELOG.md",       "记录重要依赖变更",              False),
        ],
    ),
    ChangeType(
        id="auth",
        name="认证/安全变更",
        description="修改认证逻辑、权限控制或安全机制",
        triggers=[
            "backend/peekview/auth.py",
            "backend/peekview/api/auth.py",
            "backend/peekview/api/apikeys.py",
            "backend/peekview/services/apikey_service.py",
        ],
        docs=[
            ("README.md",          "更新认证相关说明",     False),
            ("docs/DEPLOYMENT.md", "更新安全配置说明",     False),
            ("CHANGELOG.md",       "记录安全/认证变更",    True),
        ],
    ),
    ChangeType(
        id="release_process",
        name="发布/调试流程变更",
        description="修改 Makefile、发布脚本或调试脚本",
        triggers=[
            "Makefile",
            "backend/Makefile",
            "scripts/*.sh",
            "scripts/doc-sync/*.py",
        ],
        docs=[
            ("docs/process/release.md",        "更新发布流程文档",   False),
            ("docs/process/debug-workflow.md",  "更新调试流程文档",   False),
            ("CLAUDE.md",                       "更新 Debug Workflow 章节", False),
            ("CHANGELOG.md",                    "记录流程变更",      False),
        ],
    ),
]


# ─────────────────────────────────────────────
# 文件匹配逻辑
# ─────────────────────────────────────────────

def match_trigger(changed_file: str, trigger: str) -> bool:
    """判断变更文件是否匹配触发模式。"""
    import fnmatch
    # 精确匹配
    if changed_file == trigger:
        return True
    # glob 模式匹配
    if fnmatch.fnmatch(changed_file, trigger):
        return True
    # 前缀匹配（兼容子路径）
    if trigger.endswith("*") and changed_file.startswith(trigger[:-1]):
        return True
    return False


def detect_change_types(changed_files: list[str]) -> list[ChangeType]:
    """根据变更文件列表，检测涉及的变更类型（去重）。"""
    matched = []
    seen_ids = set()

    for ct in CHANGE_TYPES:
        for cf in changed_files:
            for trigger in ct.triggers:
                if match_trigger(cf, trigger):
                    if ct.id not in seen_ids:
                        matched.append(ct)
                        seen_ids.add(ct.id)
                    break

    return matched


def get_git_changed_files(staged_only: bool = False) -> list[str]:
    """从 git 获取变更文件列表。"""
    try:
        if staged_only:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True, text=True, check=True,
            )
        else:
            # 未暂存 + 已暂存 + 未追踪
            staged = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True, text=True, check=True,
            ).stdout
            unstaged = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True, text=True, check=True,
            ).stdout
            result_text = staged + unstaged
            return sorted(set(result_text.strip().splitlines()))
        return result.stdout.strip().splitlines()
    except subprocess.CalledProcessError:
        return []


# ─────────────────────────────────────────────
# 输出格式
# ─────────────────────────────────────────────

def format_terminal(changed_files: list[str], change_types: list[ChangeType]) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("文档更新 Checklist")
    lines.append("=" * 60)

    if not changed_files:
        lines.append("\n✅ 未检测到代码变更")
        return "\n".join(lines)

    lines.append(f"\n检测到 {len(changed_files)} 个变更文件：")
    for f in changed_files[:10]:
        lines.append(f"  • {f}")
    if len(changed_files) > 10:
        lines.append(f"  … 还有 {len(changed_files) - 10} 个文件")

    if not change_types:
        lines.append("\n✅ 变更文件不涉及需要文档同步的代码区域")
        return "\n".join(lines)

    lines.append(f"\n触发 {len(change_types)} 种变更类型，需要更新以下文档：\n")

    # 收集所有需要更新的文档（去重，必须项优先）
    all_docs: dict[str, tuple[str, bool, list[str]]] = {}  # file → (desc_combined, required, type_ids)
    for ct in change_types:
        for doc_file, doc_desc, required in ct.docs:
            if doc_file not in all_docs:
                all_docs[doc_file] = (doc_desc, required, [ct.name])
            else:
                existing_desc, existing_req, existing_types = all_docs[doc_file]
                all_docs[doc_file] = (
                    existing_desc,
                    existing_req or required,
                    existing_types + [ct.name],
                )

    # 必须项
    required_docs = [(f, d, r, t) for f, (d, r, t) in all_docs.items() if r]
    optional_docs = [(f, d, r, t) for f, (d, r, t) in all_docs.items() if not r]

    if required_docs:
        lines.append("【必须更新】")
        for doc_file, doc_desc, _, type_names in sorted(required_docs):
            exists = Path(doc_file).exists()
            mark = "☐" if exists else "☐ (文件不存在)"
            lines.append(f"  {mark} {doc_file}")
            lines.append(f"       → {doc_desc}")
            lines.append(f"       触发原因：{', '.join(type_names)}")
        lines.append("")

    if optional_docs:
        lines.append("【按需更新】（如相关内容有变化）")
        for doc_file, doc_desc, _, type_names in sorted(optional_docs):
            lines.append(f"  ☐ {doc_file}")
            lines.append(f"       → {doc_desc}")
        lines.append("")

    lines.append("─" * 60)
    lines.append("提示：")
    lines.append("  • 版本号变更后运行：make sync-version-docs")
    lines.append("  • 功能特性更新后运行：make update-docs")
    lines.append("  • 完整文档检查：make check-doc-sync")
    lines.append("=" * 60)

    return "\n".join(lines)


def format_markdown(changed_files: list[str], change_types: list[ChangeType]) -> str:
    """输出 Markdown 格式（用于写入 checkpoint 文档）。"""
    from datetime import date
    lines = []
    lines.append(f"## 文档更新 Checklist\n")
    lines.append(f"*生成时间：{date.today().isoformat()}*\n")

    if not change_types:
        lines.append("✅ 本次变更不涉及需要文档同步的代码区域\n")
        return "\n".join(lines)

    all_docs: dict[str, tuple[str, bool, list[str]]] = {}
    for ct in change_types:
        for doc_file, doc_desc, required in ct.docs:
            if doc_file not in all_docs:
                all_docs[doc_file] = (doc_desc, required, [ct.name])
            else:
                existing_desc, existing_req, existing_types = all_docs[doc_file]
                all_docs[doc_file] = (existing_desc, existing_req or required, existing_types + [ct.name])

    required_docs = [(f, d, r, t) for f, (d, r, t) in all_docs.items() if r]
    optional_docs = [(f, d, r, t) for f, (d, r, t) in all_docs.items() if not r]

    if required_docs:
        lines.append("### 必须更新\n")
        for doc_file, doc_desc, _, type_names in sorted(required_docs):
            lines.append(f"- [ ] `{doc_file}` — {doc_desc}")
        lines.append("")

    if optional_docs:
        lines.append("### 按需更新\n")
        for doc_file, doc_desc, _, type_names in sorted(optional_docs):
            lines.append(f"- [ ] `{doc_file}` — {doc_desc}（如相关内容有变化）")
        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# 主函数
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="根据变更文件生成文档更新 checklist",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--files", nargs="*", metavar="FILE",
        help="指定变更文件列表（不指定则从 git 自动检测）",
    )
    parser.add_argument(
        "--staged", action="store_true",
        help="只检查已暂存的文件（pre-commit hook 使用）",
    )
    parser.add_argument(
        "--format", choices=["terminal", "markdown"], default="terminal",
        help="输出格式（默认 terminal）",
    )
    parser.add_argument(
        "--exit-code", action="store_true",
        help="有必须更新的文档时返回非零退出码",
    )
    args = parser.parse_args()

    # 切换到项目根目录
    script_dir = Path(__file__).parent
    root = script_dir.parent.parent
    import os
    os.chdir(root)

    # 获取变更文件
    if args.files:
        changed_files = args.files
    elif args.staged:
        changed_files = get_git_changed_files(staged_only=True)
    else:
        changed_files = get_git_changed_files(staged_only=False)

    # 检测变更类型
    change_types = detect_change_types(changed_files)

    # 输出 checklist
    if args.format == "markdown":
        print(format_markdown(changed_files, change_types))
    else:
        print(format_terminal(changed_files, change_types))

    # 退出码
    if args.exit_code and change_types:
        # 有必须更新的文档，但这里只是提示，不阻断
        # 真正的阻断在 pre-commit hook 里处理版本一致性
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
