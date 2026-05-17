#!/bin/bash
# Git pre-commit hook — 文档同步检查
#
# 安装方法：
#   make setup-hooks
# 或手动：
#   ln -sf ../../scripts/git-hooks/pre-commit.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# 功能：
#   1. 检查版本号一致性（版本文件变更时强制，不通过则阻断提交）
#   2. 输出文档更新 checklist（提示性，不阻断）
#   3. 检查旧格式环境变量（提示性，不阻断）

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   Pre-commit: 文档同步检查           ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── 获取已暂存文件 ────────────────────────────────
STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || true)

if [ -z "$STAGED_FILES" ]; then
    echo "✅ 无暂存文件，跳过检查"
    exit 0
fi

# ── 判断是否涉及版本文件 ──────────────────────────
VERSION_CHANGED=0
for file in $STAGED_FILES; do
    case "$file" in
        backend/pyproject.toml|\
        backend/peekview/__init__.py|\
        frontend-v3/package.json)
            VERSION_CHANGED=1
            ;;
    esac
done

# ── 1. 版本一致性检查（版本文件变更时强制） ────────
if [ $VERSION_CHANGED -eq 1 ]; then
    echo "→ 检测到版本文件变更，执行版本一致性检查..."
    echo ""

    # 获取真实版本（pyproject.toml 为准）
    CURRENT_VERSION=$(grep '^version = ' backend/pyproject.toml | sed 's/version = "\(.*\)"/\1/')

    CHECK_FAILED=0

    # 检查 __init__.py
    INIT_VERSION=$(grep '__version__' backend/peekview/__init__.py | sed 's/.*"\(.*\)".*/\1/')
    if [ "$INIT_VERSION" != "$CURRENT_VERSION" ]; then
        echo "  ❌ backend/peekview/__init__.py: $INIT_VERSION ≠ $CURRENT_VERSION"
        CHECK_FAILED=1
    else
        echo "  ✅ backend/peekview/__init__.py: $INIT_VERSION"
    fi

    # 检查 package.json
    PKG_VERSION=$(grep '"version":' frontend-v3/package.json | sed 's/.*"\(.*\)".*/\1/' | tr -d ' ')
    if [ "$PKG_VERSION" != "$CURRENT_VERSION" ]; then
        echo "  ❌ frontend-v3/package.json: $PKG_VERSION ≠ $CURRENT_VERSION"
        CHECK_FAILED=1
    else
        echo "  ✅ frontend-v3/package.json: $PKG_VERSION"
    fi

    # 检查文档版本引用
    check_doc_version() {
        local file="$1"
        local desc="$2"
        if [ ! -f "$file" ]; then
            echo "  ⚠️  $file: 文件不存在"
            return
        fi
        if grep -qF "$CURRENT_VERSION" "$file"; then
            echo "  ✅ $file: 包含 $CURRENT_VERSION"
        else
            echo "  ❌ $file: 未找到 $CURRENT_VERSION（$desc）"
            CHECK_FAILED=1
        fi
    }

    check_doc_version "README.md" "需更新 badge 版本号"
    check_doc_version "CLAUDE.md" "需更新 Current Version"
    check_doc_version "INDEX.md" "需更新 当前版本"
    check_doc_version "docs/process/active-tasks.md" "需更新 当前版本已发布"

    # 检查 CHANGELOG
    if grep -qF "## [$CURRENT_VERSION]" CHANGELOG.md 2>/dev/null; then
        echo "  ✅ CHANGELOG.md: 包含 [$CURRENT_VERSION] 记录"
    else
        echo "  ❌ CHANGELOG.md: 缺少 [$CURRENT_VERSION] 版本记录"
        CHECK_FAILED=1
    fi

    if [ $CHECK_FAILED -eq 1 ]; then
        echo ""
        echo "┌──────────────────────────────────────────────────┐"
        echo "│  ❌ 提交被阻止：版本号不一致                      │"
        echo "│                                                   │"
        echo "│  修复方法：                                       │"
        echo "│    make sync-version-docs                        │"
        echo "│  然后重新 git add 更新的文档文件后再提交          │"
        echo "└──────────────────────────────────────────────────┘"
        echo ""
        exit 1
    fi
    echo ""
    echo "  ✅ 版本一致性检查通过（v$CURRENT_VERSION）"
fi

# ── 2. 文档 Checklist 提示（不阻断） ─────────────
echo ""
echo "→ 生成文档更新 checklist..."
echo ""

if command -v python3 &>/dev/null && [ -f "scripts/doc-sync/doc_checklist.py" ]; then
    python3 scripts/doc-sync/doc_checklist.py --staged 2>/dev/null || true
else
    echo "  ⚠️  Python3 不可用，跳过 checklist 生成"
fi

# ── 3. 旧格式环境变量检查（不阻断） ──────────────
if [ -f "scripts/check_doc_consistency.sh" ]; then
    ENV_ISSUES=$(bash scripts/check_doc_consistency.sh 2>&1 | grep "✗" || true)
    if [ -n "$ENV_ISSUES" ]; then
        echo ""
        echo "⚠️  发现旧格式环境变量（不阻断，建议修复）："
        echo "$ENV_ISSUES"
    fi
fi

echo ""
echo "✅ Pre-commit 检查完成，提交继续"
echo ""
exit 0
