#!/usr/bin/env python3
"""
自媒体创作定时任务 v2.0 - 主动触发主Agent
每天8:30生成选题并飞书通知

架构变更:
- v1.0: 创建任务文件，等待主agent轮询（问题：没人轮询）
- v2.0: 直接发送飞书消息触发主agent（解决：主动触发）
"""

import json
import os
import sys
import random
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path("/home/emilyg/emilygclaws/openclaw-workspace/self-media-creator")
LOG_FILE = Path("/tmp/self-media-creator-cron.log")
CONFIG_FILE = PROJECT_DIR / "config" / ".env.feishu"
TOPICS_DIR = PROJECT_DIR / "output" / "daily_topics"
TOPICS_DIR.mkdir(parents=True, exist_ok=True)

# 内容方向库
CONTENT_DIRECTIONS = [
    "AI知识科普", "AI工具分享", "AI热点追踪",
    "ChatGPT技巧", "Midjourney绘画", "AI写作方法",
    "AI效率提升", "AI副业赚钱", "AI学习路径",
    "大模型对比", "AI行业动态", "AI产品评测",
    "Prompt工程", "AI视频制作", "AI音频处理"
]

# 选题角度库
TOPIC_ANGLES = {
    "wechat": [
        "趋势洞察", "深度评测", "入门指南", "避坑实录", "效率提升",
        "行业观察", "个人成长", "工具对比", "实战案例", "未来预测",
        "方法论总结", "踩坑复盘", "省钱攻略", "时间管理", "副业探索"
    ],
    "xiaohongshu": [
        "种草推荐", "避坑指南", "使用技巧", "对比测评", "省钱攻略",
        "效率神器", "颜值担当", "懒人必备", "小众宝藏", "真香现场",
        "后悔没早买", "亲测有效", "一周体验", "月入提升", "生活改变"
    ]
}

def log(message):
    timestamp = datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def load_config():
    """加载飞书配置"""
    webhook_url = None
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if 'FEISHU_WEBHOOK_URL' in line and '=' in line:
                    webhook_url = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break
    return webhook_url

def send_feishu_notification(webhook_url, notification_text):
    """发送飞书通知"""
    payload = {
        "msg_type": "text",
        "content": {
            "text": notification_text
        }
    }
    
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    
    try:
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json; charset=utf-8'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                log("飞书通知发送成功")
                return True
            else:
                log(f"飞书通知失败: {result}")
                return False
    except Exception as e:
        log(f"飞书通知异常: {e}")
        return False

def trigger_main_agent(direction, platform, angles):
    """
    通过飞书消息触发主Agent生成选题
    发送特殊格式的消息，主agent会识别并处理
    """
    webhook_url = load_config()
    if not webhook_url:
        log("❌ 未配置飞书webhook")
        return False
    
    platform_name = "公众号" if platform == "wechat" else "小红书"
    today = datetime.now().strftime("%Y%m%d")
    
    # 特殊格式的触发消息
    message = f"""🤖 【自媒体定时任务】请生成今日选题

📍 内容方向: {direction}
📱 平台: {platform_name}
🎯 建议角度: {', '.join(angles)}

请：
1. 基于"{direction}"生成3个{platform_name}选题
2. 每个选题包含：标题、一句话描述、角度、预计字数
3. 飞书回复通知用户选择
4. 保存结果到: {TOPICS_DIR}/topics_{today}.json

这是定时任务触发，请直接生成并回复。"""

    success = send_feishu_notification(webhook_url, message)
    if success:
        log("✅ 已发送触发消息给主agent")
    return success

def generate_topics_locally(direction, platform):
    """本地生成选题（备用方案）"""
    angles = random.sample(TOPIC_ANGLES.get(platform, TOPIC_ANGLES["wechat"]), 3)
    platform_name = "公众号" if platform == "wechat" else "小红书"
    
    # 选题模板库
    templates = {
        "趋势洞察": [
            (f"2024年{direction}最新趋势：这3个变化你必须知道", "深度分析行业最新动态，帮你把握先机"),
            (f"从{direction}看未来：我们正处在什么阶段？", "结合最新发展，预测未来走向"),
        ],
        "入门指南": [
            (f"{direction}零基础入门：我花3天整理的完整路径", "新手友好，从零开始的系统指南"),
            (f"写给小白的{direction}入门手册", "用最通俗的语言讲清楚核心概念"),
        ],
        "个人成长": [
            (f"学习{direction}30天，我的生活发生了什么变化", "真实记录，从怀疑到真香的转变"),
            (f"{direction}如何帮我提升了3倍工作效率", "具体案例+方法分享，可复制"),
        ],
        "深度评测": [
            (f"我测试了5款{direction}工具，最惊艳的是这个", "横向对比，帮你选择最适合的"),
        ],
        "效率提升": [
            (f"用{direction}优化工作流程后，我每天节省2小时", "具体方法+工具推荐"),
        ],
        "实战案例": [
            (f"我是如何用{direction}完成这个项目的", "完整复盘，从规划到执行"),
        ]
    }
    
    topics = []
    used_titles = set()
    
    for i, angle in enumerate(angles, 1):
        angle_templates = templates.get(angle, templates["趋势洞察"])
        available = [t for t in angle_templates if t[0] not in used_titles]
        if not available:
            available = angle_templates
        
        template = random.choice(available)
        title, description = template
        used_titles.add(title)
        
        length = random.choice(["1200-1500字", "1500-2000字"]) if platform == "wechat" else random.choice(["150-250字", "200-300字"])
        
        topics.append({
            "id": i,
            "title": title,
            "description": description,
            "angle": angle,
            "estimated_length": length
        })
    
    return topics

def save_and_notify(topics, direction, platform):
    """保存选题并发送飞书通知"""
    today = datetime.now().strftime("%Y%m%d")
    result_file = TOPICS_DIR / f"topics_{today}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            "date": today,
            "direction": direction,
            "platform": platform,
            "topics": topics,
            "generated_at": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    log(f"✅ 选题已保存: {result_file}")
    
    webhook_url = load_config()
    if webhook_url:
        platform_name = "公众号" if platform == "wechat" else "小红书"
        
        lines = [
            f"🎯 【今日选题推荐 | {platform_name}】",
            f"📍 内容方向：{direction}",
            "",
            "请回复数字 (1/2/3) 选择您想要的选题：",
            ""
        ]
        
        for topic in topics:
            lines.extend([
                f"【{topic['id']}】{topic['title']}",
                f"   💡 {topic['description']}",
                f"   📝 预计字数：{topic['estimated_length']} | 角度：{topic['angle']}",
                ""
            ])
        
        lines.extend([
            "───────────────",
            "💬 回复格式：",
            "• 回复数字 1/2/3 选择对应选题",
            "• 回复 'skip' 跳过今日",
            "• 回复新方向可重新生成"
        ])
        
        send_feishu_notification(webhook_url, "\n".join(lines))

def main():
    log("=" * 50)
    log("开始执行定时任务 v2.1 (Heartbeat监听模式)")
    
    # 1. 随机选择内容方向
    direction = random.choice(CONTENT_DIRECTIONS)
    platform = "wechat"
    angles = random.sample(TOPIC_ANGLES[platform], 3)
    
    log(f"🎲 内容方向: {direction}")
    log(f"📱 平台: {platform}")
    log(f"🎯 角度: {', '.join(angles)}")
    
    # 2. 创建任务文件（Heartbeat监听模式核心）
    # 主agent会在Heartbeat时检查这个文件并处理
    today = datetime.now().strftime("%Y%m%d")
    task_file = TOPICS_DIR / f"_llm_task_{today}.json"
    
    task_data = {
        "task": "generate_topics",
        "direction": direction,
        "platform": platform,
        "angles": angles,
        "output_file": str(TOPICS_DIR / f"topics_{today}.json"),
        "created_at": datetime.now().isoformat(),
        "status": "pending",
        "version": "2.1"
    }
    
    with open(task_file, 'w', encoding='utf-8') as f:
        json.dump(task_data, f, ensure_ascii=False, indent=2)
    
    log(f"✅ 任务文件已创建: {task_file}")
    log(f"⏳ 等待主agent在Heartbeat时处理...")
    
    # 3. 可选：同时发送飞书通知（让用户知道任务已创建）
    webhook_url = load_config()
    if webhook_url:
        message = f"""🤖 【自媒体定时任务】选题任务已创建

📍 内容方向: {direction}
📱 平台: 公众号
🎯 角度: {', '.join(angles)}
⏰ 将在下次Heartbeat时自动生成选题

（无需回复，稍后会收到选题通知）"""
        send_feishu_notification(webhook_url, message)
    
    log("=" * 50)

if __name__ == "__main__":
    main()
