#!/usr/bin/env python3
"""
定时任务协调器 - 每天8:30生成选题并通知用户
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
TOPICS_DIR = PROJECT_ROOT / "output" / "daily_topics"
TOPICS_DIR.mkdir(parents=True, exist_ok=True)


def generate_and_notify(direction: str, platform: str = "wechat"):
    """
    生成选题并输出飞书通知格式
    
    使用方式:
    python3 scripts/daily_scheduler.py --direction "AI工具" --platform wechat
    """
    # 导入选题生成器
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from generate_topics import TopicGenerator
    
    generator = TopicGenerator(platform=platform)
    topics = generator.generate_topics(direction)
    
    # 保存选题到文件（供后续用户回复时使用）
    today = datetime.now().strftime("%Y%m%d")
    topics_file = TOPICS_DIR / f"topics_{today}.json"
    
    topics_data = {
        "date": today,
        "direction": direction,
        "platform": platform,
        "topics": topics,
        "status": "pending",  # pending/selected/skipped
        "selected_id": None,
        "created_at": datetime.now().isoformat()
    }
    
    with open(topics_file, 'w', encoding='utf-8') as f:
        json.dump(topics_data, f, ensure_ascii=False, indent=2)
    
    # 输出飞书通知格式
    notification = generator.format_for_notification(direction, topics)
    
    # 添加文件路径信息（供主系统使用）
    full_notification = f"""{notification}

📁 选题已保存: {topics_file}
🤖 回复后我将自动继续创作流程
"""
    
    print(full_notification)
    return topics_file


def handle_user_response(response: str, date: str = None):
    """
    处理用户回复
    
    回复格式:
    - "1", "2", "3": 选择对应选题
    - "skip": 跳过今日
    - 其他: 视为新方向，重新生成选题
    
    使用方式:
    python3 scripts/daily_scheduler.py --response "1" --date 20260311
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
    parser.add_argument("--direction", "-d", help="内容方向（定时任务模式）")
    parser.add_argument("--platform", "-p", default="wechat",
                       choices=["wechat", "xiaohongshu"], help="平台")
    parser.add_argument("--response", "-r", help="用户回复（处理模式）")
    parser.add_argument("--date", help="指定日期 (YYYYMMDD)")
    
    args = parser.parse_args()
    
    if args.response:
        # 处理用户回复模式
        result = handle_user_response(args.response, args.date)
        if result:
            # 可以在这里自动触发创作流程
            pass
    elif args.direction:
        # 定时任务模式 - 生成选题
        generate_and_notify(args.direction, args.platform)
    else:
        parser.error("请提供 --direction 或 --response 参数")


if __name__ == "__main__":
    main()
