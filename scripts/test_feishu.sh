#!/bin/bash
# 测试飞书机器人配置

PROJECT_DIR="/home/emilyg/emilygclaws/openclaw-workspace/self-media-creator"

# 加载配置
if [ -f "$PROJECT_DIR/config/.env.feishu" ]; then
    source "$PROJECT_DIR/config/.env.feishu"
fi

FEISHU_WEBHOOK="${FEISHU_WEBHOOK_URL:-}"

echo "🔍 飞书机器人配置测试"
echo "======================"
echo ""

# 检查配置
if [ -z "$FEISHU_WEBHOOK" ]; then
    echo "❌ 未配置飞书 Webhook"
    echo ""
    echo "请按以下步骤配置："
    echo "1. 在飞书群里添加自定义机器人"
    echo "2. 复制 Webhook 地址"
    echo "3. 编辑 config/.env.feishu 文件："
    echo "   FEISHU_WEBHOOK_URL=\"你的webhook地址\""
    echo ""
    echo "详见: docs/feishu-setup.md"
    exit 1
fi

echo "✅ 已找到 Webhook 配置"
echo ""

# 构建测试消息
TIME=$(date '+%Y-%m-%d %H:%M:%S')

echo "📤 正在发送测试消息..."

JSON_PAYLOAD='{"msg_type":"text","content":{"text":"🤖 **飞书机器人测试**\n\n这是一条测试消息，如果您看到了，说明配置成功！\n\n⏰ 时间：'$TIME'\n📁 项目：自媒体创作 Agent\n✅ 状态：配置正常\n\n明天 8:30 将开始自动生成选题～"}}'

RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD" \
    "$FEISHU_WEBHOOK")

# 检查响应
if echo "$RESPONSE" | grep -q '"code":0'; then
    echo ""
    echo "✅ 测试消息发送成功！"
    echo "请检查飞书群是否收到消息"
    exit 0
else
    echo ""
    echo "❌ 发送失败"
    echo "响应: $RESPONSE"
    echo ""
    echo "可能原因："
    echo "• Webhook 地址错误"
    echo "• 机器人已被移出群聊"
    echo "• 网络连接问题"
    exit 1
fi
