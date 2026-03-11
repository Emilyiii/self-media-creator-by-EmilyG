# 飞书机器人配置指南

## 快速配置步骤

### 1. 创建飞书机器人

1. 打开**飞书** → 进入您想接收消息的群聊
2. 点击右上角 **"..."** → **群设置** → **群机器人**
3. 点击 **添加机器人**
4. 选择 **"自定义机器人"**
5. 设置机器人名称（如"自媒体助手"）→ 点击 **添加**
6. 复制 **Webhook 地址**（格式：`https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx`）

### 2. 配置 Webhook

**方式一：直接修改配置文件（推荐）**

编辑 `config/.env.feishu`：

```bash
# 用您的webhook地址替换下方内容
FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxx"
```

**方式二：设置环境变量**

```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxx"

# 添加到 ~/.bashrc 使其永久生效
echo 'export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxx"' >> ~/.bashrc
```

### 3. 测试飞书通知

```bash
cd /home/emilyg/emilygclaws/openclaw-workspace/self-media-creator
bash scripts/test_feishu.sh
```

看到飞书群里收到测试消息即为成功！✅

---

## 配置详情

### 配置文件位置

```
config/
├── .env.feishu          # 飞书配置
└── .env.example         # 配置示例
```

### 安全提示

⚠️ **Webhook 地址是敏感信息**，请勿：
- 提交到公开代码仓库
- 分享给他人
- 暴露在日志中

`.env.feishu` 已添加到 `.gitignore`，不会被提交。

---

## 消息格式

飞书通知支持多种格式：

### 文本消息（当前使用）
```
🎯 【今日选题推荐 | 公众号】
📍 内容方向：AI工具

请回复数字 (1/2/3) 选择您想要的选题：

【1】深度解析：AI工具的2026年最新趋势
   💡 从技术、市场、用户三个维度全面分析
   📝 预计字数：1500-2000字 | 角度：趋势分析
...
```

### 交互卡片（未来扩展）
可以升级为带按钮的交互卡片，直接在飞书里点击选择。

---

## 故障排查

### 检查配置是否正确

```bash
# 查看当前配置
cat config/.env.feishu

# 测试发送消息
bash scripts/test_feishu.sh
```

### 检查日志

```bash
# 查看定时任务日志
tail -f /tmp/self-media-creator-cron.log

# 查看最近执行结果
cat /tmp/self-media-creator-cron.log | tail -20
```

### 常见问题

**Q: 飞书收不到消息？**
- 检查 webhook URL 是否正确复制
- 检查机器人是否还在群里（可能被移除）
- 检查 webhook 地址是否过期（自定义机器人webhook长期有效）

**Q: 消息格式错乱？**
- 飞书文本消息不支持所有Markdown语法
- 特殊字符需要转义

**Q: 可以发到私聊吗？**
- 飞书自定义机器人只能发送到群聊
- 如需私聊通知，需使用飞书应用或自建机器人

---

## 高级配置

### 多群通知

如果需要通知多个群，修改 `cron_daily.sh`：

```bash
FEISHU_WEBHOOKS=(
    "https://open.feishu.cn/open-apis/bot/v2/hook/xxxx1"
    "https://open.feishu.cn/open-apis/bot/v2/hook/xxxx2"
)

for webhook in "${FEISHU_WEBHOOKS[@]}"; do
    curl -s -X POST -H "Content-Type: application/json" \
        -d "$JSON_PAYLOAD" "$webhook"
done
```

### 安全加固

将 webhook 地址存储在系统密钥管理中：

```bash
# 使用 pass 或类似的密码管理器
FEISHU_WEBHOOK_URL=$(pass show feishu/webhook)
```
