#!/usr/bin/env python3
"""
Content Formatter - Format articles for 公众号 (WeChat)
Outputs Markdown with formatting markers and image placeholders
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional


def detect_structure(content: str) -> List[Dict]:
    """
    Analyze content structure and identify sections
    
    Returns list of sections with type and content
    """
    sections = []
    
    # Split by common section markers
    # Look for patterns like "## 标题", "一、", "1. ", etc.
    lines = content.split('\n')
    current_section = {"type": "intro", "content": []}
    
    for line in lines:
        # Detect headers
        if re.match(r'^#{1,3}\s+', line):
            if current_section["content"]:
                sections.append(current_section)
            level = len(re.match(r'^#+', line).group())
            current_section = {
                "type": f"h{level}",
                "title": re.sub(r'^#+\s*', '', line),
                "content": []
            }
        # Detect numbered sections (一、二、三)
        elif re.match(r'^[一二三四五六七八九十]+[、.．]\s*', line):
            if current_section["content"]:
                sections.append(current_section)
            current_section = {
                "type": "section",
                "title": line.strip(),
                "content": []
            }
        else:
            current_section["content"].append(line)
    
    if current_section["content"] or current_section.get("title"):
        sections.append(current_section)
    
    return sections


def format_markdown(content: str, images: List[Dict], style: str = "professional") -> str:
    """
    Format content as Markdown for 公众号
    
    Args:
        content: Raw article content
        images: List of image dicts with path and position
        style: Formatting style (professional/casual/minimal)
    
    Returns:
        Formatted Markdown string
    """
    lines = []
    
    # Add title if not present
    if not content.strip().startswith('#'):
        # Try to extract first line as title
        first_line = content.strip().split('\n')[0]
        lines.append(f"# {first_line}")
        lines.append("")
        content = '\n'.join(content.strip().split('\n')[1:])
    
    # Insert cover image after title
    cover_images = [img for img in images if img.get("position") == "after_title"]
    if cover_images:
        lines.append(f"![封面图]({cover_images[0]['path']})")
        lines.append("")
    
    # Process content sections
    sections = detect_structure(content)
    image_idx = 0
    other_images = [img for img in images if img.get("position") != "after_title"]
    
    for i, section in enumerate(sections):
        # Add section title
        if section.get("title"):
            if section["type"] == "h1":
                lines.append(f"# {section['title']}")
            elif section["type"] == "h2":
                lines.append(f"## {section['title']}")
            elif section["type"] == "h3":
                lines.append(f"### {section['title']}")
            else:
                lines.append(f"## {section['title']}")
            lines.append("")
        
        # Add section content
        section_text = '\n'.join(section["content"]).strip()
        
        # Apply style-specific formatting
        if style == "professional":
            section_text = format_professional(section_text)
        elif style == "casual":
            section_text = format_casual(section_text)
        else:  # minimal
            section_text = format_minimal(section_text)
        
        lines.append(section_text)
        lines.append("")
        
        # Insert image after section (every 2-3 sections)
        if i > 0 and i % 2 == 0 and image_idx < len(other_images):
            lines.append(f"![配图]({other_images[image_idx]['path']})")
            lines.append("")
            image_idx += 1
    
    # Add remaining images at the end
    while image_idx < len(other_images):
        lines.append(f"![配图]({other_images[image_idx]['path']})")
        lines.append("")
        image_idx += 1
    
    return '\n'.join(lines)


def format_professional(text: str) -> str:
    """Apply professional formatting"""
    # Bold key terms (simplified - in practice would use NLP)
    # Add blockquotes for important statements
    lines = text.split('\n')
    formatted = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Convert "注意：" or "提示：" to blockquote
        if re.match(r'^(注意|提示|重要|关键)[：:]', line):
            formatted.append(f"> {line}")
        # Convert list items
        elif re.match(r'^[\-\*•]\s', line):
            formatted.append(line)
        else:
            formatted.append(line)
    
    return '\n\n'.join(formatted)


def format_casual(text: str) -> str:
    """Apply casual formatting"""
    # More conversational, use italics for emphasis
    text = re.sub(r'"([^"]+)"', r'*\1*', text)  # Quotes to italic
    return text


def format_minimal(text: str) -> str:
    """Apply minimal formatting"""
    # Clean, simple formatting
    return text.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Format content for 公众号 (WeChat)"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input file containing article content"
    )
    parser.add_argument(
        "--images",
        help="JSON file with image metadata"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file for formatted content"
    )
    parser.add_argument(
        "--style",
        choices=["professional", "casual", "minimal"],
        default="professional",
        help="Formatting style"
    )
    
    args = parser.parse_args()
    
    # Load content
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error loading content: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Load images
    images = []
    if args.images:
        try:
            with open(args.images, 'r', encoding='utf-8') as f:
                images = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load images: {e}", file=sys.stderr)
    
    # Format content
    formatted = format_markdown(content, images, args.style)
    
    # Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(formatted)
    
    # Output result info
    result = {
        "platform": "wechat",
        "output_file": str(output_path),
        "style": args.style,
        "images_inserted": len(images),
        "content_length": len(formatted)
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nFormatted content saved to: {output_path}")


if __name__ == "__main__":
    main()
