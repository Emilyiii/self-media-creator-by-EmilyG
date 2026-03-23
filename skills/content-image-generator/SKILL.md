---
name: content-image-generator
description: Generate AI images for content creation. Use when creating illustrations, diagrams, or visual assets for articles, blog posts, social media content, or any text-based content that needs配图. Supports automatic image planning, prompt generation, and batch image generation with selection logic. Works with Seedream, DALL-E, Midjourney, or other image generation APIs.
---

# Content Image Generator

Generate contextual images for articles and content.

## Overview

This skill helps generate配图 (illustrations/images) for content like公众号 articles, blog posts, and social media. It handles the full workflow from analyzing content to generating and selecting images.

## Workflow

### Step 1: Analyze Content & Plan Images

Read the article/content and determine:
- How many images are needed (recommend ≤5 for公众号, ≤3 for short posts)
- Where each image should be inserted (after which paragraph/section)
- What each image should depict (concept, scene, diagram type)

### Step 2: Design Image Specifications

For each planned image, design:
- **Content**: What visual elements to include
- **Layout**: Composition (centered, split-screen, full-width, etc.)
- **Style**: Art direction (flat illustration, 3D render, photography, etc.)

### Step 3: Generate Prompts (双语版本)

Create detailed prompts for image generation. **必须同时生成英文和中文两个版本**。

Prompt结构：
```
[Subject] + [Scene/Environment] + [Style] + [Composition] + [Lighting/Mood] + [Technical specs]
```

**双语Prompt要求：**
- **英文版 (prompt_en)**: 用于Seedream、DALL-E、Midjourney等AI绘图工具
- **中文版 (prompt_zh)**: 用于即梦、文心一格等中文AI绘图工具，或作为用户参考

**示例：**
```json
{
  "prompt_en": "modern flat illustration, AI technology concept, neural networks, clean design, bright gradient colors, professional, 16:9 aspect ratio, high quality",
  "prompt_zh": "现代扁平插画风格，AI科技概念，神经网络，简洁设计，明亮渐变色，专业感，16:9比例，高质量"
}
```

### Step 4: Generate Images

Use the generation script:
```bash
python3 scripts/generate_images.py --prompts prompts.json --output ./images --model seedream
```

Or generate via API directly if preferred.

### Step 5: Select Best Images

Review generated images and select the best ones based on:
- Relevance to content
- Visual quality
- Style consistency
- Readability (text elements if any)

No user confirmation needed - make the selection autonomously.

### Step 6: Deliver Results

Return to caller with:
- Selected image file paths
- Insertion positions in the content
- Brief description of each image

## Configuration

### Supported Models

| Model | Best For | Cost Estimate |
|-------|----------|---------------|
| Seedream (豆包) | Chinese content, illustration | ~0.2元/image |
| DALL-E 3 | General purpose, text rendering | ~$0.04/image |
| Midjourney | Artistic, high quality | ~$0.10/image |

### Image Types

- **封面图 (Cover)**: Eye-catching, represents article theme
- **概念图 (Concept)**: Explains abstract ideas
- **对比图 (Comparison)**: Side-by-side comparisons
- **流程图 (Process)**: Step-by-step visualizations
- **数据图 (Data)**: Charts, infographics (prefer code-generated)

## Resources

### scripts/
- `generate_images.py` - Batch image generation with multiple providers
- `select_best.py` - Automatic image selection based on criteria

### references/
- `prompt-guide.md` - Prompt engineering for image generation
- `style-reference.md` - Visual style catalog and examples

## Integration with Content Pipeline

This skill is designed to be called by a parent agent (e.g.,公众号创作 Agent). Expected input/output:

**Input:**
```json
{
  "content": "文章正文...",
  "max_images": 5,
  "style_preference": "flat_illustration",
  "output_dir": "./article_images"
}
```

**Output:**
```json
{
  "images": [
    {
      "file_path": "./article_images/cover.png",
      "position": "after_title",
      "description": "封面图：AI工具概念插画",
      "prompt": "modern flat illustration, AI technology concept...",
      "prompt_en": "modern flat illustration, AI technology concept, neural networks, clean design, bright gradient colors, professional, 16:9 aspect ratio",
      "prompt_zh": "现代扁平插画风格，AI科技概念，神经网络，简洁设计，明亮渐变色，专业感，16:9比例"
    }
  ],
  "total_cost": "0.8元"
}
```
