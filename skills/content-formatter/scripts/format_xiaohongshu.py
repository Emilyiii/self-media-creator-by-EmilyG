#!/usr/bin/env python3
"""
Content Formatter - Format articles for 小红书 (Xiaohongshu)
Outputs plain text optimized for mobile reading
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional


def extract_key_points(content: str, num_points: int = 3) -> List[str]:
    """
    Extract key points from content for bullet list
    
    Args:
        content: Article content
        num_points: Number of key points to extract
    
    Returns:
        List of key point strings
    """
    # Simple extraction based on sentence structure
    # In production, this could use NLP for better extraction
    
    sentences = re.split(r'[。！？\n]', content)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    # Look for sentences with key indicators
    key_indicators = ['关键', '核心', '重点', '首先', '其次', '最后', '第一', '第二', '第三']
    key_points = []
    
    for sent in sentences:
        if any(indicator in sent for indicator in key_indicators):
            key_points.append(sent)
        if len(key_points) >= num_points:
            break
    
    # If not enough key points found, take first few substantial sentences
    if len(key_points) < num_points:
        for sent in sentences:
            if sent not in key_points and len(sent) > 15:
                key_points.append(sent)
            if len(key_points) >= num_points:
                break
    
    return key_points[:num_points]


def suggest_hashtags(content: str) -> List[str]:
    """
    Suggest relevant hashtags based on content
    
    Args:
        content: Article content
    
    Returns:
        List of hashtag suggestions
    """
    # Topic detection based on keywords
    topic_keywords = {
        'AI': ['AI', '人工智能', 'ChatGPT', '大模型', '机器学习'],
        'tech': ['技术', '编程', '代码', '开发', '程序员'],
        'productivity': ['效率', '工具', '自动化', '工作流', '时间管理'],
        'learning': ['学习', '成长', '知识', '读书', '教程'],
        'career': ['职场', '工作', '面试', '简历', '跳槽'],
        'life': ['生活', '日常', '分享', '记录', '感悟']
    }
    
    content_lower = content.lower()
    detected_topics = []
    
    for topic, keywords in topic_keywords.items():
        if any(kw in content for kw in keywords):
            detected_topics.append(topic)
    
    # Map to actual hashtags
    hashtag_map = {
        'AI': ['#AI工具', '#人工智能', '#效率神器', '#科技改变生活'],
        'tech': ['#程序员', '#编程学习', '#技术分享', '#代码'],
        'productivity': ['#效率工具', '#生产力', '#时间管理', '#工作提效'],
        'learning': ['#学习笔记', '#知识分享', '#自我提升', '#学习方法'],
        'career': ['#职场干货', '#求职经验', '#工作经验', '#打工人'],
        'life': ['#生活记录', '#日常分享', '#生活方式', '#治愈系']
    }
    
    hashtags = []
    for topic in detected_topics[:2]:  # Top 2 topics
        hashtags.extend(hashtag_map.get(topic, []))
    
    # Add general hashtags
    hashtags.extend(['#干货分享', '#经验分享'])
    
    return list(dict.fromkeys(hashtags))[:5]  # Remove duplicates, limit to 5


def format_xiaohongshu(content: str, style: str = "casual") -> str:
    """
    Format content for 小红书
    
    Args:
        content: Raw article content
        style: Tone style (casual/professional/friendly)
    
    Returns:
        Formatted plain text for 小红书
    """
    lines = []
    
    # Extract title (first line or first sentence)
    first_line = content.strip().split('\n')[0]
    if len(first_line) > 30:
        # If first line is too long, extract a shorter hook
        title = first_line[:25] + "..."
    else:
        title = first_line
    
    # Hook line with emoji
    hook_emojis = {
        "casual": "✨",
        "professional": "💡",
        "friendly": "🌟"
    }
    hook_emoji = hook_emojis.get(style, "✨")
    lines.append(f"{hook_emoji} {title}")
    lines.append("")
    
    # Core insight (1-2 sentences summary)
    sentences = re.split(r'[。！？]', content)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    if sentences:
        core = sentences[0]
        if len(core) > 50:
            core = core[:50] + "..."
        lines.append(f"💡 {core}")
        lines.append("")
    
    # Key points section
    lines.append("📌 重点内容：")
    key_points = extract_key_points(content, 3)
    
    for point in key_points:
        # Truncate long points
        if len(point) > 40:
            point = point[:38] + "..."
        lines.append(f"• {point}")
    
    lines.append("")
    
    # Personal take section
    take_emojis = {
        "casual": "💬",
        "professional": "📝",
        "friendly": "💭"
    }
    take_emoji = take_emojis.get(style, "💬")
    lines.append(f"{take_emoji} 我的看法：")
    
    # Generate a brief personal take
    if style == "casual":
        lines.append("这个真的挺有用的，建议收藏！👇")
    elif style == "professional":
        lines.append("实践下来效果不错，推荐尝试。")
    else:
        lines.append("希望对大家有帮助呀～有问题可以问我")
    
    lines.append("")
    
    # Hashtags
    hashtags = suggest_hashtags(content)
    lines.append(" ".join(hashtags))
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Format content for 小红书 (Xiaohongshu)"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input file containing article content"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file for formatted content"
    )
    parser.add_argument(
        "--style",
        choices=["casual", "professional", "friendly"],
        default="casual",
        help="Tone style"
    )
    
    args = parser.parse_args()
    
    # Load content
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error loading content: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Format content
    formatted = format_xiaohongshu(content, args.style)
    
    # Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(formatted)
    
    # Output result info
    result = {
        "platform": "xiaohongshu",
        "output_file": str(output_path),
        "style": args.style,
        "character_count": len(formatted),
        "estimated_read_time": f"{len(formatted) // 200}分钟"
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nFormatted content saved to: {output_path}")


if __name__ == "__main__":
    main()
