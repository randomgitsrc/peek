#!/bin/bash
# Git pre-commit hook for documentation consistency
# Install: ln -s ../../scripts/git-hooks/pre-commit.sh .git/hooks/pre-commit

set -e

echo "=== Pre-commit: Documentation Consistency Check ==="

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only)

# Check if relevant files are staged
NEEDS_DOC_CHECK=0

for file in $STAGED_FILES; do
    case "$file" in
        backend/peekview/config.py|\
        backend/peekview/api/*.py|\
        backend/peekview/cli.py|\
        Makefile|\
        scripts/*.sh)
            NEEDS_DOC_CHECK=1
            echo "→ Detected change in: $file"
            ;;
    esac
done

if [ $NEEDS_DOC_CHECK -eq 0 ]; then
    echo "✓ No code changes requiring doc sync check"
    exit 0
fi

# Run doc consistency check
echo "→ Running documentation consistency check..."
if [ -f scripts/check_doc_consistency.sh ]; then
    if ! bash scripts/check_doc_consistency.sh; then
        echo ""
        echo "✗ Documentation consistency check FAILED"
        echo ""
        echo "Please fix the issues above before committing."
        echo "See docs/process/doc-sync-guide.md for guidelines."
        exit 1
    fi
else
    echo "⚠ scripts/check_doc_consistency.sh not found, skipping"
fi

echo "✓ Documentation consistency check PASSED"
exit 0
