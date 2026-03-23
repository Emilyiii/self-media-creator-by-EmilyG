#!/usr/bin/env python3
"""
自媒体创作定时任务 - 每天8:30生成选题并飞书通知
替代原来的 cron_daily.sh，使用Python处理通知更可靠

修改：现在通过调用主agent来生成选题，使用大模型而不是固定模板
"""

import json
import subprocess
import os
import sys
import random
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path("/home/emilyg/emilygclaws/openclaw-workspace/self-media-creator")
LOG_FILE = Path("/tmp/self-media-creator-cron.log")
CONFIG_FILE = PROJECT_DIR / "config" / ".env.feishu"
TOPICS_DIR = PROJECT_DIR / "output" / "daily_topics"
TOPICS_DIR.mkdir(parents=True, exist_ok=True)

# 内容方向库 - 用于随机选择
CONTENT_DIRECTIONS = [
    "AI知识科普", "AI工具分享", "AI热点追踪",
    "ChatGPT技巧", "Midjourney绘画", "AI写作方法",
    "AI效率提升", "AI副业赚钱", "AI学习路径",
    "大模型对比", "AI行业动态", "AI产品评测",
    "Prompt工程", "AI视频制作", "AI音频处理"
]

# 选题角度库 - 用于增加随机性
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
    import urllib.request
    import urllib.error
    
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
            headers={
                'Content-Type': 'application/json; charset=utf-8'
            },
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

def select_random_direction():
    """随机选择内容方向"""
    direction = random.choice(CONTENT_DIRECTIONS)
    log(f"🎲 随机选择内容方向: {direction}")
    return direction

def select_random_angles(platform):
    """随机选择3个不同角度"""
    angles = TOPIC_ANGLES.get(platform, TOPIC_ANGLES["wechat"])
    return random.sample(angles, min(3, len(angles)))

def generate_topics_with_llm(direction, platform="wechat"):
    """
    使用大模型生成选题
    
    策略：创建一个任务文件，然后等待主agent处理
    主agent会读取任务文件，调用大模型生成选题，然后保存结果
    """
    today = datetime.now().strftime("%Y%m%d")
    task_file = TOPICS_DIR / f"_llm_task_{today}.json"
    result_file = TOPICS_DIR / f"topics_{today}.json"
    
    # 随机选择角度
    angles = select_random_angles(platform)
    
    # 构建prompt
    platform_name = "公众号" if platform == "wechat" else "小红书"
    
    if platform == "wechat":
        style_guide = """
选题要求：
1. 适合公众号长文，有深度、有观点
2. 标题要吸引人但不做标题党
3. 覆盖不同角度：实用教程、个人体验、趋势分析等
4. 预计字数在1200-2500字之间
"""
    else:
        style_guide = """
选题要求：
1. 适合小红书短内容，轻松、接地气
2. 标题要有网感，带emoji或符号更佳
3. 覆盖不同角度：种草、避坑、技巧、体验等
4. 预计字数在150-350字之间
"""
    
    prompt = f"""你是一个资深自媒体选题策划专家。

请为{platform_name}平台生成3个关于"{direction}"的选题建议。

可用角度参考（从以下角度中选择3个不同的）：{', '.join(angles)}

{style_guide}

请按以下JSON格式返回（不要包含任何其他文字）：
{{
  "topics": [
    {{
      "id": 1,
      "title": "选题标题",
      "description": "一句话描述这个选题的亮点",
      "angle": "角度类型",
      "estimated_length": "预计字数范围"
    }},
    ...
  ]
}}
"""
    
    # 创建任务文件
    task_data = {
        "task": "generate_topics",
        "direction": direction,
        "platform": platform,
        "prompt": prompt,
        "angles": angles,
        "output_file": str(result_file),
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    with open(task_file, 'w', encoding='utf-8') as f:
        json.dump(task_data, f, ensure_ascii=False, indent=2)
    
    log(f"📝 LLM任务文件已创建: {task_file}")
    
    # 返回任务信息，让主agent知道需要处理
    return {
        "task_file": str(task_file),
        "result_file": str(result_file),
        "prompt": prompt,
        "direction": direction,
        "platform": platform
    }

def format_notification(direction, topics, platform):
    """格式化为飞书通知文本"""
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
        "• 回复新方向可重新生成（如：换成'AI工具'）"
    ])
    
    return "\n".join(lines)

def main():
    log("=" * 50)
    log("开始执行定时任务")
    
    os.chdir(PROJECT_DIR)
    
    # 1. 随机选择内容方向
    direction = select_random_direction()
    platform = "wechat"
    
    log(f"平台: {platform}")
    
    # 2. 创建LLM任务（等待主agent处理）
    task_info = generate_topics_with_llm(direction, platform)
    
    # 输出特殊标记，让主agent知道需要调用LLM
    print("\n" + "=" * 50)
    print("_REQUIRES_LLM_GENERATION_")
    print(json.dumps(task_info, ensure_ascii=False, indent=2))
    print("=" * 50 + "\n")
    
    log("等待主agent调用LLM生成选题...")
    
    # 注意：实际的LLM调用和飞书通知由主agent完成
    # 这个脚本只负责创建任务文件和输出标记
    
    log("定时任务准备完成，等待LLM处理")

if __name__ == "__main__":
    main()
