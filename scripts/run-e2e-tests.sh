#!/bin/bash
# PeekView E2E 测试脚本
# 确保调试服务运行后再执行

set -e

PORT=8888
BASE_URL="http://127.0.0.1:$PORT"

echo "=== PeekView E2E 测试 ==="

# 检查服务是否运行
echo "→ 检查服务状态..."
if ! curl -s "$BASE_URL/health" > /dev/null 2>&1; then
    echo "✗ 错误: 调试服务未运行"
    echo "   请先运行: make debug-start"
    echo "   服务应运行在: $BASE_URL"
    exit 1
fi
echo "✓ 服务运行中: $BASE_URL"

# 创建测试数据目录
mkdir -p /tmp/e2e-results

cd frontend-v3

# 设置 Playwright baseURL
export BASE_URL=$BASE_URL

echo ""
echo "→ 运行 E2E 测试 (debug-server.spec.ts)..."
npx playwright test e2e/debug-server.spec.ts --reporter=line || {
    echo ""
    echo "✗ E2E 测试失败"
    echo "   查看截图: /tmp/e2e-results/"
    echo "   查看报告: npx playwright show-report"
    exit 1
}

echo ""
echo "=== ✓ 所有 E2E 测试通过 ==="
echo "截图保存位置: /tmp/e2e-results/"
echo ""
echo "请访问 $BASE_URL 进行人工验证"
echo "确认无误后运行: make debug-stop"
echo ""

# 显示测试结果摘要
echo "测试截图:"
ls -la /tmp/e2e-results/*.png 2>/dev/null | awk '{print "  - " $9}' || echo "  无截图"
