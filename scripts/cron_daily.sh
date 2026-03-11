#!/bin/bash
# 自媒体创作定时任务 - 生成选题并飞书通知

PROJECT_DIR="/home/emilyg/emilygclaws/openclaw-workspace/self-media-creator"
LOG_FILE="/tmp/self-media-creator-cron.log"
FEISHU_WEBHOOK="${FEISHU_WEBHOOK_URL:-}"  # 从环境变量读取

# 内容方向（可以配置多个，每天轮换）
DIRECTIONS=("AI工具" "效率提升" "自媒体运营")
# 简单轮询：根据日期选择
DAY=$(date +%d)
INDEX=$((10#$DAY % 3))
DIRECTION=${DIRECTIONS[$INDEX]}

PLATFORM="wechat"  # 或 xiaohongshu

echo "[$(date)] 开始执行定时任务 - 方向: $DIRECTION" >> $LOG_FILE

cd $PROJECT_DIR

# 1. 生成选题
TOPIC_OUTPUT=$(python3 scripts/daily_scheduler.py --direction "$DIRECTION" --platform "$PLATFORM" 2>&1)
TOPIC_FILE=$(echo "$TOPIC_OUTPUT" | grep "选题已保存:" | awk '{print $NF}')

echo "[$(date)] 选题文件: $TOPIC_FILE" >> $LOG_FILE

# 2. 飞书通知（如果配置了webhook）
if [ -n "$FEISHU_WEBHOOK" ]; then
    # 提取飞书通知格式部分（去除文件路径信息）
    NOTIFICATION=$(echo "$TOPIC_OUTPUT" | sed 's/📁 选题已保存:.*//g' | sed 's/🤖 回复后我将自动继续创作流程//g')
    
    # 构建飞书消息JSON
    JSON_PAYLOAD=$(cat <<EOF
{
    "msg_type": "text",
    "content": {
        "text": "${NOTIFICATION}"
    }
}
EOF
)
    
    curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$JSON_PAYLOAD" \
        "$FEISHU_WEBHOOK" >> $LOG_FILE 2>&1
    
    echo "[$(date)] 飞书通知已发送" >> $LOG_FILE
else
    echo "[$(date)] 未配置飞书webhook，仅保存到日志" >> $LOG_FILE
    echo "$TOPIC_OUTPUT" >> $LOG_FILE
fi

echo "[$(date)] 定时任务完成" >> $LOG_FILE
echo "---" >> $LOG_FILE
