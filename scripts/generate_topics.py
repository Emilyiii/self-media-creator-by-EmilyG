#!/usr/bin/env python3
"""
选题模块 - 独立运行，生成备选选题
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List

# 项目路径配置
PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
CONTENT_RESEARCH_SKILL = SKILLS_DIR / "content-research" / "SKILL.md"


class TopicGenerator:
    """选题生成器"""
    
    def __init__(self, platform: str = "wechat"):
        self.platform = platform
    
    def generate_topics(self, direction: str) -> List[Dict]:
        """
        根据方向生成3个选题建议
        
        Args:
            direction: 内容方向/主题方向
            
        Returns:
            选题列表，每个包含title、description、angle
        """
        topics = []
        
        if self.platform == "wechat":
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
        
        return topics
    
    def format_for_notification(self, direction: str, topics: List[Dict]) -> str:
        """格式化为飞书通知文本"""
        platform_name = "公众号" if self.platform == "wechat" else "小红书"
        
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
    parser = argparse.ArgumentParser(description="选题生成模块")
    parser.add_argument("--direction", "-d", required=True, help="内容方向")
    parser.add_argument("--platform", "-p", default="wechat", 
                       choices=["wechat", "xiaohongshu"], help="平台")
    parser.add_argument("--output", "-o", help="输出JSON文件路径")
    parser.add_argument("--format", "-f", choices=["json", "text"], 
                       default="text", help="输出格式")
    
    args = parser.parse_args()
    
    generator = TopicGenerator(platform=args.platform)
    topics = generator.generate_topics(args.direction)
    
    if args.format == "json":
        result = {
            "direction": args.direction,
            "platform": args.platform,
            "topics": topics,
            "timestamp": datetime.now().isoformat()
        }
        output = json.dumps(result, ensure_ascii=False, indent=2)
        
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f"✅ 选题已保存到: {args.output}")
        else:
            print(output)
    else:
        # 文本格式（用于飞书通知）
        output = generator.format_for_notification(args.direction, topics)
        
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f"✅ 选题已保存到: {args.output}")
        else:
            print(output)


if __name__ == "__main__":
    from datetime import datetime
    main()
