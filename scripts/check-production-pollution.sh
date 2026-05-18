#!/bin/bash
# 检查并清理生产数据库中的测试数据
# Usage: ./scripts/check-production-pollution.sh [--cleanup]

set -e

PROD_URL="http://127.0.0.1:8080"
CLEANUP=${1:-""}

echo "=== 生产数据库污染检查 ==="

# 获取生产环境数据
echo "→ 检查生产数据库..."
RESPONSE=$(curl -s "$PROD_URL/api/v1/entries" 2>/dev/null || echo '{"items":[]}')

# 检查测试数据
TEST_ENTRIES=$(echo "$RESPONSE" | python3 << 'EOF'
import sys, json
try:
    d = json.load(sys.stdin)
    test_entries = [e for e in d.get('items', []) if 'e2e-' in e.get('slug', '') or 'test-' in e.get('slug', '').lower() or 'test' in e.get('summary', '').lower()]
    for e in test_entries:
        print(e['slug'])
except Exception as ex:
    pass
EOF
)

# Filter out empty lines
TEST_ENTRIES=$(echo "$TEST_ENTRIES" | grep -v '^$' || true)
TEST_COUNT=$(echo "$TEST_ENTRIES" | grep -c '^' || echo "0")
if [ -z "$TEST_ENTRIES" ]; then
    TEST_COUNT=0
fi
TOTAL_COUNT=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total',0))" 2>/dev/null || echo "unknown")

if [ "$TEST_COUNT" -eq 0 ]; then
    echo "✓ 生产数据库干净 (总条目: $TOTAL_COUNT)"
    exit 0
else
    echo "✗ 发现 $TEST_COUNT 条测试数据污染生产数据库!"
    echo ""
    echo "测试数据列表:"
    echo "$TEST_ENTRIES" | while read slug; do
        echo "  - $slug"
    done
    echo ""

    if [ "$CLEANUP" = "--cleanup" ]; then
        echo "→ 开始清理..."
        echo "$TEST_ENTRIES" | while read slug; do
            if [ -n "$slug" ]; then
                curl -s -X DELETE "$PROD_URL/api/v1/entries/$slug" > /dev/null 2>&1
                echo "  ✓ 已删除: $slug"
            fi
        done
        echo ""
        echo "✓ 清理完成"

        # 重新检查
        NEW_RESPONSE=$(curl -s "$PROD_URL/api/v1/entries" 2>/dev/null || echo '{"items":[]}')
        NEW_TEST_COUNT=$(echo "$NEW_RESPONSE" | python3 << 'EOF'
import sys, json
try:
    d = json.load(sys.stdin)
    test_count = sum(1 for e in d.get('items',[]) if 'e2e-' in e.get('slug','') or 'test-' in e.get('slug','').lower())
    print(test_count)
except:
    print("0")
EOF
)
        echo "检查后剩余测试数据: $NEW_TEST_COUNT"
    else
        echo "运行以下命令清理:"
        echo "  ./scripts/check-production-pollution.sh --cleanup"
        echo ""
        echo "或者手动删除:"
        echo "$TEST_ENTRIES" | while read slug; do
            echo "  curl -X DELETE $PROD_URL/api/v1/entries/$slug"
        done
        exit 1
    fi
fi
