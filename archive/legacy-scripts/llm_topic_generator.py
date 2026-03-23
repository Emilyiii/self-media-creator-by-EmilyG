#!/usr/bin/env python3
"""
LLM选题生成器 - 由主agent调用

这个脚本接收一个prompt，调用大模型生成选题，然后保存结果。
它通过 openclaw 的 sessions_spawn 机制被主agent调用。

使用方式:
    python3 scripts/llm_topic_generator.py --task-file output/daily_topics/_llm_task_20260315.json
"""

import json
import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent.parent
TOPICS_DIR = PROJECT_DIR / "output" / "daily_topics"


def parse_llm_response(response_text: str) -> list:
    """解析大模型返回的JSON"""
    try:
        # 尝试直接解析
        data = json.loads(response_text)
        if "topics" in data:
            return data["topics"]
    except json.JSONDecodeError:
        pass
    
    # 尝试从markdown代码块中提取
    import re
    json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    for match in matches:
        try:
            data = json.loads(match.strip())
            if "topics" in data:
                return data["topics"]
        except json.JSONDecodeError:
            continue
    
    # 尝试找到JSON对象
    try:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start >= 0 and end > start:
            data = json.loads(response_text[start:end])
            if "topics" in data:
                return data["topics"]
    except (json.JSONDecodeError, ValueError):
        pass
    
    raise ValueError(f"无法解析LLM响应: {response_text[:200]}...")


def generate_topics(task_file: str, llm_response: str = None):
    """
    生成选题
    
    Args:
        task_file: 任务文件路径
        llm_response: 大模型的响应内容（如果为None，则读取stdin）
    """
    task_path = Path(task_file)
    
    if not task_path.exists():
        print(f"❌ 任务文件不存在: {task_file}")
        sys.exit(1)
    
    # 读取任务
    with open(task_path, 'r', encoding='utf-8') as f:
        task = json.load(f)
    
    direction = task["direction"]
    platform = task["platform"]
    output_file = task.get("output_file")
    
    if not output_file:
        today = datetime.now().strftime("%Y%m%d")
        output_file = str(TOPICS_DIR / f"topics_{today}.json")
    
    # 如果提供了LLM响应，解析它
    if llm_response:
        try:
            topics = parse_llm_response(llm_response)
            print(f"✅ 成功解析 {len(topics)} 个选题")
        except ValueError as e:
            print(f"❌ 解析失败: {e}")
            sys.exit(1)
    else:
        # 从stdin读取
        print("等待从stdin读取LLM响应...")
        response_text = sys.stdin.read()
        try:
            topics = parse_llm_response(response_text)
            print(f"✅ 成功解析 {len(topics)} 个选题")
        except ValueError as e:
            print(f"❌ 解析失败: {e}")
            sys.exit(1)
    
    # 保存结果
    result = {
        "date": datetime.now().strftime("%Y%m%d"),
        "direction": direction,
        "platform": platform,
        "topics": topics,
        "status": "pending",
        "selected_id": None,
        "created_at": datetime.now().isoformat(),
        "llm_generated": True
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 选题已保存到: {output_file}")
    
    # 更新任务状态
    task["status"] = "completed"
    task["completed_at"] = datetime.now().isoformat()
    task["result_file"] = output_file
    
    with open(task_path, 'w', encoding='utf-8') as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    
    # 输出飞书通知格式
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
    
    notification = "\n".join(lines)
    
    # 输出通知内容（供主agent使用）
    print("\n" + "=" * 50)
    print("NOTIFICATION_START")
    print(notification)
    print("NOTIFICATION_END")
    print("=" * 50)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="LLM选题生成器")
    parser.add_argument("--task-file", "-t", required=True, help="任务文件路径")
    parser.add_argument("--llm-response", "-r", help="LLM响应内容（JSON字符串）")
    parser.add_argument("--from-stdin", action="store_true", help="从stdin读取LLM响应")
    
    args = parser.parse_args()
    
    if args.llm_response:
        generate_topics(args.task_file, args.llm_response)
    elif args.from_stdin:
        generate_topics(args.task_file, None)
    else:
        # 直接生成示例（用于测试）
        print("⚠️ 未提供LLM响应，请使用 --llm-response 或 --from-stdin")
        print(f"任务文件: {args.task_file}")
        
        # 读取并显示任务
        with open(args.task_file, 'r', encoding='utf-8') as f:
            task = json.load(f)
        print(f"\n任务内容:")
        print(f"  方向: {task['direction']}")
        print(f"  平台: {task['platform']}")
        print(f"  Prompt:\n{task['prompt'][:500]}...")


if __name__ == "__main__":
    main()
