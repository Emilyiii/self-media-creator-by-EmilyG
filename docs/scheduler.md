# 定时任务配置

## 工作流程

```
每天 8:30 ──→ 生成选题 ──→ 飞书通知用户 ──→ 等待回复
                                          ↓
                    用户回复 1/2/3 ──→ 自动执行创作流程
                         或 skip ──→ 跳过今日
                       或新方向 ──→ 重新生成选题
```

## 配置方式

### 方式一：OpenClaw Heartbeat（推荐）

在 `HEARTBEAT.md` 中添加检查：

```markdown
## 每日定时任务检查
- [ ] 检查是否 08:30
  - 是 → 执行选题任务
  - 否 → 跳过
```

### 方式二：系统 Cron

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天 8:30）
30 8 * * * cd /path/to/self-media-creator && python3 scripts/daily_scheduler.py --direction "AI工具" --platform wechat
```

### 方式三：OpenClaw Sessions Spawn

通过主 agent 的定时任务 spawn 子 agent：

```python
# 每天 8:30 执行
sessions_spawn(
    mode="run",
    task="cd self-media-creator && python3 scripts/daily_scheduler.py --direction 'AI工具' --platform wechat"
)
```

## 用户交互流程

### 1. 生成选题（8:30 自动执行）

```bash
python3 scripts/daily_scheduler.py --direction "AI工具" --platform wechat
```

输出示例：
```
🎯 【今日选题推荐 | 公众号】
📍 内容方向：AI工具

请回复数字 (1/2/3) 选择您想要的选题：

【1】深度解析：AI工具的2026年最新趋势
   💡 从技术、市场、用户三个维度全面分析
   📝 预计字数：1500-2000字 | 角度：趋势分析

【2】我用了一个月AI工具，这是我的真实体验
   💡 第一手体验报告，真实使用感受
   📝 预计字数：1200-1500字 | 角度：体验分享

【3】AI工具入门指南：从零到精通的完整路径
   💡 适合新手的系统性教程
   📝 预计字数：1800-2500字 | 角度：教程指南

───────────────
💬 回复格式：
• 回复数字 1/2/3 选择对应选题
• 回复 'skip' 跳过今日
• 回复新方向可重新生成（如：换成'AI工具'）

📁 选题已保存: output/daily_topics/topics_20260311.json
🤖 回复后我将自动继续创作流程
```

### 2. 处理用户回复

```bash
# 用户选择 1
python3 scripts/daily_scheduler.py --response "1"

# 输出：
# ✅ 已选择选题 1: 深度解析：AI工具的2026年最新趋势
# 📁 选题文件: output/daily_topics/topics_20260311.json
# 🚀 可以继续执行创作流程:
#    python3 scripts/create_content.py --topic-file output/daily_topics/topics_20260311.json
```

### 3. 执行创作流程

```bash
# 方式1：直接传入选题文件
python3 scripts/create_content.py \
  --topic-file output/daily_topics/topics_20260311.json \
  --platform wechat \
  --style professional \
  --max-images 3

# 方式2：直接指定主题（跳过选题阶段）
python3 scripts/create_content.py \
  --topic "深度解析：AI工具的2026年最新趋势" \
  --platform wechat \
  --style professional \
  --max-images 3
```

## 文件存储结构

```
output/
├── daily_topics/           # 每日选题存储
│   ├── topics_20260311.json
│   ├── topics_20260312.json
│   └── ...
└── article_20260311_083045/  # 创作结果
    ├── article.md
    ├── meta.json
    └── workflow.json
```

## 选题文件格式

```json
{
  "date": "20260311",
  "direction": "AI工具",
  "platform": "wechat",
  "topics": [...],
  "status": "selected",  // pending/selected/skipped
  "selected_id": 1,
  "selected_topic": {
    "id": 1,
    "title": "深度解析：AI工具的2026年最新趋势",
    "description": "...",
    "angle": "趋势分析",
    "estimated_length": "1500-2000字"
  },
  "created_at": "2026-03-11T08:30:00",
  "selected_at": "2026-03-11T09:15:00"
}
```

## 自动化脚本示例

### 完整的定时任务脚本

```bash
#!/bin/bash
# daily_cron.sh

cd /path/to/self-media-creator

# 1. 生成选题
python3 scripts/daily_scheduler.py \
  --direction "AI工具" \
  --platform wechat > /tmp/topic_notification.txt

# 2. 发送飞书通知（需要配置 webhook）
# curl -X POST -H "Content-Type: application/json" \
#   -d @/tmp/topic_notification.txt \
#   YOUR_FEISHU_WEBHOOK_URL

echo "选题已生成: $(date)"
```

### 处理用户回复的 webhook

```python
# webhook_handler.py
# 部署为飞书机器人 webhook，接收用户回复

@app.route('/webhook', methods=['POST'])
def handle_feishu_message():
    message = request.json.get('message', '')
    
    # 调用调度器处理回复
    import subprocess
    result = subprocess.run([
        'python3', 'scripts/daily_scheduler.py',
        '--response', message
    ], capture_output=True, text=True)
    
    if '已选择选题' in result.stdout:
        # 自动开始创作
        subprocess.run([
            'python3', 'scripts/create_content.py',
            '--topic-file', 'output/daily_topics/topics_20260311.json'
        ])
    
    return {'message': 'ok'}
```

## 注意事项

1. **选题方向配置**：建议创建一个 `config/daily_directions.txt` 文件，每天轮换不同的内容方向
2. **失败重试**：创作流程中如遇失败，应保存状态并通知用户，支持断点续传
3. **并发控制**：同一时间段只能有一个创作任务在运行
4. **通知时机**：
   - 选题生成 → 立即通知
   - 创作完成 → 通知并附结果
   - 遇到卡点 → 立即通知
