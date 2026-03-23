#!/usr/bin/env python3
"""
定时任务协调器 - 每天生成选题并通知用户

修改：支持LLM生成选题，通过主agent调用大模型
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import random

PROJECT_ROOT = Path(__file__).parent.parent
TOPICS_DIR = PROJECT_ROOT / "output" / "daily_topics"
TOPICS_DIR.mkdir(parents=True, exist_ok=True)

# 内容方向库 - 用于随机选择
CONTENT_DIRECTIONS = [
    "AI知识科普", "AI工具分享", "AI热点追踪",
    "ChatGPT技巧", "Midjourney绘画", "AI写作方法",
    "AI效率提升", "AI副业赚钱", "AI学习路径",
    "大模型对比", "AI行业动态", "AI产品评测",
    "Prompt工程", "AI视频制作", "AI音频处理",
    "AI编程助手", "AI数据分析", "AI设计工具"
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


def select_random_direction():
    """随机选择内容方向"""
    return random.choice(CONTENT_DIRECTIONS)


def select_random_angles(platform):
    """随机选择3个不同角度"""
    angles = TOPIC_ANGLES.get(platform, TOPIC_ANGLES["wechat"])
    return random.sample(angles, min(3, len(angles)))


def build_topic_prompt(direction: str, platform: str, angles: list) -> str:
    """构建生成选题的prompt"""
    platform_name = "公众号" if platform == "wechat" else "小红书"
    
    if platform == "wechat":
        style_guide = """
选题要求：
1. 适合公众号长文，有深度、有观点
2. 标题要吸引人但不做标题党，避免夸张
3. 覆盖不同角度：实用教程、个人体验、趋势分析等
4. 预计字数在1200-2500字之间
5. 标题要具体，避免过于笼统
"""
    else:
        style_guide = """
选题要求：
1. 适合小红书短内容，轻松、接地气
2. 标题要有网感，可以带emoji或符号
3. 覆盖不同角度：种草、避坑、技巧、体验等
4. 预计字数在150-350字之间
5. 标题要口语化，像朋友推荐
"""
    
    prompt = f"""你是一个资深自媒体选题策划专家。

请为{platform_name}平台生成3个关于"{direction}"的选题建议。

可用角度参考（从以下角度中选择3个不同的，不要重复）：
{chr(10).join(f"- {angle}" for angle in angles)}

{style_guide}

请按以下JSON格式返回（不要包含任何其他文字，只返回JSON）：
{{
  "topics": [
    {{
      "id": 1,
      "title": "选题标题",
      "description": "一句话描述这个选题的亮点和看点",
      "angle": "角度类型（从上面提供的角度中选择）",
      "estimated_length": "预计字数范围"
    }},
    {{
      "id": 2,
      "title": "选题标题",
      "description": "一句话描述这个选题的亮点和看点",
      "angle": "角度类型",
      "estimated_length": "预计字数范围"
    }},
    {{
      "id": 3,
      "title": "选题标题",
      "description": "一句话描述这个选题的亮点和看点",
      "angle": "角度类型",
      "estimated_length": "预计字数范围"
    }}
  ]
}}
"""
    return prompt


def create_llm_task(direction: str, platform: str = "wechat") -> dict:
    """
    创建LLM生成选题的任务
    
    返回任务信息，供主agent调用LLM
    """
    today = datetime.now().strftime("%Y%m%d")
    task_file = TOPICS_DIR / f"_llm_task_{today}.json"
    result_file = TOPICS_DIR / f"topics_{today}.json"
    
    # 随机选择角度
    angles = select_random_angles(platform)
    
    # 构建prompt
    prompt = build_topic_prompt(direction, platform, angles)
    
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
    
    return {
        "task_file": str(task_file),
        "result_file": str(result_file),
        "prompt": prompt,
        "direction": direction,
        "platform": platform
    }


def generate_and_notify(direction: str = None, platform: str = "wechat", use_llm: bool = True):
    """
    生成选题并输出飞书通知格式
    
    Args:
        direction: 内容方向（None则随机选择）
        platform: 平台
        use_llm: 是否使用大模型生成
    """
    # 确定内容方向
    if direction is None:
        direction = select_random_direction()
        print(f"🎲 随机选择内容方向: {direction}")
    
    if use_llm:
        # LLM模式：创建任务文件，等待主agent处理
        task_info = create_llm_task(direction, platform)
        
        # 输出特殊标记，让调用者知道需要调用LLM
        print("\n" + "=" * 60)
        print("🤖 LLM选题生成任务已创建")
        print("=" * 60)
        print(f"\n📍 内容方向: {direction}")
        print(f"📝 任务文件: {task_info['task_file']}")
        print(f"💾 结果文件: {task_info['result_file']}")
        print("\n⚠️  需要主agent调用大模型生成选题")
        print("=" * 60)
        
        # 输出JSON格式的任务信息（供脚本解析）
        print("\n_TASK_INFO_")
        print(json.dumps(task_info, ensure_ascii=False, indent=2))
        
        return task_info
    else:
        # 模板模式（fallback）
        return generate_template_topics(direction, platform)


def generate_template_topics(direction: str, platform: str):
    """使用模板生成选题（作为fallback）"""
    today = datetime.now().strftime("%Y%m%d")
    result_file = TOPICS_DIR / f"topics_{today}.json"
    
    if platform == "wechat":
        topics = [
            {
                "id": 1,
                "title": f"深度解析：{direction}的2026年最新趋势",
                "description": "从技术、市场、用户三个维度全面分析，适合深度长文",
                "angle": "趋势分析",
                "estimated_length": "1500-2000字"
            },
            {
                "id": 2,
                "title": f"我用了一个月{direction}，这是我的真实体验",
                "description": "第一手体验报告，真实使用感受，更有亲和力",
                "angle": "体验分享",
                "estimated_length": "1200-1500字"
            },
            {
                "id": 3,
                "title": f"{direction}入门指南：从零到精通的完整路径",
                "description": "适合新手的系统性教程，覆盖面广",
                "angle": "教程指南",
                "estimated_length": "1800-2500字"
            }
        ]
    else:  # xiaohongshu
        topics = [
            {
                "id": 1,
                "title": f"被{direction}惊艳到了！",
                "description": "短平快的种草内容，突出亮点，适合快速传播",
                "angle": "种草推荐",
                "estimated_length": "200-300字"
            },
            {
                "id": 2,
                "title": f"{direction}避坑指南｜血泪教训",
                "description": "分享经验和避坑技巧，实用性强",
                "angle": "经验分享",
                "estimated_length": "250-350字"
            },
            {
                "id": 3,
                "title": f"{direction}真的太香了",
                "description": "轻松愉快的推荐内容，易产生共鸣",
                "angle": "轻松推荐",
                "estimated_length": "150-250字"
            }
        ]
    
    # 保存结果
    result = {
        "date": today,
        "direction": direction,
        "platform": platform,
        "topics": topics,
        "status": "pending",
        "selected_id": None,
        "created_at": datetime.now().isoformat(),
        "llm_generated": False
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 输出通知
    notification = format_notification(direction, topics, platform)
    print(notification)
    print(f"\n📁 选题已保存: {result_file}")
    
    return result


def format_notification(direction: str, topics: list, platform: str) -> str:
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


def handle_user_response(response: str, date: str = None):
    """
    处理用户回复
    
    回复格式:
    - "1", "2", "3": 选择对应选题
    - "skip": 跳过今日
    - 其他: 视为新方向，重新生成选题
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    topics_file = TOPICS_DIR / f"topics_{date}.json"
    
    if not topics_file.exists():
        print(f"❌ 未找到 {date} 的选题文件")
        return None
    
    with open(topics_file, 'r', encoding='utf-8') as f:
        topics_data = json.load(f)
    
    response = response.strip().lower()
    
    if response == "skip":
        topics_data["status"] = "skipped"
        with open(topics_file, 'w', encoding='utf-8') as f:
            json.dump(topics_data, f, ensure_ascii=False, indent=2)
        print("⏭️ 已跳过今日创作")
        return None
    
    if response in ["1", "2", "3"]:
        selected_id = int(response)
        selected_topic = next(
            (t for t in topics_data["topics"] if t["id"] == selected_id), 
            None
        )
        
        if selected_topic:
            topics_data["status"] = "selected"
            topics_data["selected_id"] = selected_id
            topics_data["selected_topic"] = selected_topic
            topics_data["selected_at"] = datetime.now().isoformat()
            
            with open(topics_file, 'w', encoding='utf-8') as f:
                json.dump(topics_data, f, ensure_ascii=False, indent=2)
            
            # 输出创作启动信息
            print(f"✅ 已选择选题 {selected_id}: {selected_topic['title']}")
            print(f"📁 选题文件: {topics_file}")
            print(f"🚀 可以继续执行创作流程:")
            print(f"   python3 scripts/create_content.py --topic-file {topics_file}")
            
            return topics_file
        else:
            print(f"❌ 无效的选题ID: {selected_id}")
            return None
    else:
        # 视为新方向，重新生成选题
        print(f"🔄 重新生成选题，方向: {response}")
        return generate_and_notify(response, topics_data.get("platform", "wechat"))


def main():
    parser = argparse.ArgumentParser(description="定时任务协调器")
    parser.add_argument("--direction", "-d", help="内容方向（不指定则随机选择）")
    parser.add_argument("--platform", "-p", default="wechat",
                       choices=["wechat", "xiaohongshu"], help="平台")
    parser.add_argument("--response", "-r", help="用户回复（处理模式）")
    parser.add_argument("--date", help="指定日期 (YYYYMMDD)")
    parser.add_argument("--template", action="store_true",
                       help="使用模板模式（不调用LLM）")
    parser.add_argument("--random", action="store_true",
                       help="随机选择内容方向（默认行为）")
    
    args = parser.parse_args()
    
    if args.response:
        # 处理用户回复模式
        result = handle_user_response(args.response, args.date)
        if result:
            # 可以在这里自动触发创作流程
            pass
    else:
        # 定时任务模式 - 生成选题
        use_llm = not args.template
        generate_and_notify(args.direction, args.platform, use_llm)


if __name__ == "__main__":
    main()
