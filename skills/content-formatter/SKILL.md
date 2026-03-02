---
name: content-formatter
description: Format content for different publishing platforms. Use when preparing articles for WeChat Official Accounts or Xiaohongshu. Supports platform-specific formatting, image insertion, and style optimization.
---

# Content Formatter

Format articles for different publishing platforms.

## Overview

This skill adapts content to platform-specific formats and styles. Supports 公众号 (WeChat Official Accounts) and 小红书 (Xiaohongshu) with extensible architecture for more platforms.

## Supported Platforms

| Platform | Output Format | Special Handling |
|----------|---------------|------------------|
| 公众号 | Markdown with formatting markers | HTML conversion ready, image placeholders |
| 小红书 | Plain text with emojis | Optimized for mobile reading, hashtag suggestions |

## Workflow

### Step 1: Analyze Platform Requirements

Determine formatting rules based on target platform:
- **公众号**: Structured, visual hierarchy, image integration
- **小红书**: Concise, mobile-friendly, emoji-rich, hashtag-optimized

### Step 2: Design Formatting Scheme

For each platform, design:
- **Visual hierarchy**: Headers, emphasis, spacing
- **Image placement**: Where images fit in the flow
- **Styling**: Colors, fonts (for preview), special markers

### Step 3: Apply Platform-Specific Transformations

**公众号 transformations:**
- Add Markdown formatting (headers, bold, lists)
- Insert image markers at appropriate positions
- Add horizontal rules for section breaks
- Preserve code blocks and quotes

**小红书 transformations:**
- Extract key points for brevity
- Add relevant emojis (✨💡📌)
- Suggest hashtags at the end
- Optimize line breaks for mobile
- Convert long paragraphs to bullet points

### Step 4: Generate Output

**公众号 output:**
```markdown
# 文章标题

![封面图](image_1.png)

## 第一节标题

正文内容...**重点强调**...

![配图](image_2.png)

## 第二节标题

- 要点1
- 要点2
```

**小红书 output:**
```
✨ 文章标题

💡 核心观点一句话总结

📌 重点内容：
• 要点1
• 要点2
• 要点3

💬 我的看法：
（简短个人感悟）

#标签1 #标签2 #标签3
```

## Platform-Specific Guidelines

### 公众号 Formatting Rules

**Structure:**
- H1 for title (only one)
- H2 for main sections
- H3 for subsections if needed
- Images after every 2-3 paragraphs or at section breaks

**Formatting:**
- Use `**bold**` for emphasis
- Use `*italic*` for quotes or secondary emphasis
- Use `> ` for important quotes or callouts
- Use `---` for section dividers
- Code blocks with triple backticks

**Image Integration:**
- Place cover image after title
- Place content images at logical breaks
- Use `![description](path)` format

### 小红书 Formatting Rules

**Structure:**
- Hook line with emoji (first 2 lines visible in feed)
- Core insight (1-2 sentences)
- Key points as bullet list
- Personal take (authentic voice)
- Hashtags (3-5 relevant tags)

**Formatting:**
- Start with attention-grabbing emoji (✨🔥💡)
- Use • or - for bullet points
- Add emojis inline for visual breaks
- Keep paragraphs under 2 lines
- Add line breaks every 2-3 sentences

**Tone:**
- Conversational and personal
- "我" perspective
- Authentic, not overly polished
- Engaging questions to encourage comments

## Input/Output Specification

**Input:**
```json
{
  "content": "文章正文...",
  "images": [
    {"path": "./cover.png", "position": "after_title"},
    {"path": "./diagram.png", "position": "after_section_1"}
  ],
  "platform": "wechat" | "xiaohongshu",
  "options": {
    "style": "professional" | "casual" | "minimal",
    "include_hashtags": true
  }
}
```

**Output:**
```json
{
  "platform": "wechat",
  "formatted_content": "# 标题\n\n![封面](cover.png)...",
  "images_inserted": ["cover.png", "diagram.png"],
  "suggestions": ["建议添加引导关注", "结尾可优化"]
}
```

## Resources

### scripts/
- `format_wechat.py` - Format for 公众号
- `format_xiaohongshu.py` - Format for 小红书

### references/
- `platform-guide.md` - Detailed platform-specific guidelines
- `emoji-library.md` - Curated emoji suggestions by topic
