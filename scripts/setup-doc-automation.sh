#!/bin/bash
# Setup script for documentation consistency automation

echo "=== Setting up documentation consistency automation ==="

# Install git hooks
echo "→ Installing Git hooks..."
if [ ! -d .git ]; then
    echo "✗ Not a git repository. Aborting."
    exit 1
fi

# Create hooks directory if not exists
mkdir -p .git/hooks

# Link pre-commit hook
if [ -f scripts/git-hooks/pre-commit.sh ]; then
    ln -sf ../../scripts/git-hooks/pre-commit.sh .git/hooks/pre-commit
    echo "  ✓ pre-commit hook installed"
else
    echo "  ✗ pre-commit.sh not found"
fi

# Make scripts executable
chmod +x scripts/check_doc_consistency.sh 2>/dev/null || true
chmod +x scripts/git-hooks/pre-commit.sh 2>/dev/null || true

echo ""
echo "=== Setup complete ==="
echo ""
echo "The following automation is now active:"
echo "  1. Pre-commit hook: Automatically checks doc consistency on commit"
echo "  2. CI/CD: GitHub Actions will check on PR and push"
echo "  3. Makefile: Run 'make check-docs' anytime"
echo ""
echo "To manually check documentation:"
echo "  make check-docs"
echo "  make check-env-vars"
echo "  make doc-audit"
echo ""
echo "To bypass pre-commit hook (emergency only):"
echo "  git commit --no-verify"
