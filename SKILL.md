---
name: self-media-creator
description: Master controller for self-media content creation. Orchestrates the complete workflow from research to publishing for 公众号 (WeChat) and 小红书 (Xiaohongshu). Integrates content-research, content-evaluator, humanize-writing, content-image-generator, and content-formatter skills. Use when creating full articles with research, writing, evaluation, image generation, and formatting. Handles the entire pipeline with checkpoint notifications.
---

# 自媒体创作 Agent (Self-Media Creator)

Master controller for complete content creation workflow.

## Overview

This skill orchestrates the entire content creation pipeline by coordinating multiple specialized skills:

```
┌─────────────────────────────────────────────────────────────┐
│                    自媒体创作 Agent                          │
├─────────────────────────────────────────────────────────────┤
│  选题 → 研究 → 写作 → 质检 → 配图 → 排版 → 发布              │
└─────────────────────────────────────────────────────────────┘
```

**Sub-skills used:**
- `content-research` - Research with freshness validation
- `content-evaluator` - Quality scoring and issue detection
- `humanize-writing` - Remove AI patterns
- `content-image-generator` - Generate illustrations
- `content-formatter` - Platform-specific formatting

## Complete Workflow

### Phase 1: Topic Selection

**Input:** Content direction or theme
**Output:** 3-5 topic options with brief descriptions

**Action:** Present options to user for selection

---

### Phase 2: Research (content-research)

**Input:** Selected topic
**Process:**
1. Generate search queries
2. Search for latest information
3. **Validate freshness** (critical!)
   - Technology: ≤3 months
   - Data: ≤5 months
   - Trends: ≤7 months
4. Score sources (credibility + freshness + relevance)

**Output:** Validated research findings with freshness scores

**Checkpoint:** If >30% sources outdated, re-search or flag to user

---

### Phase 3: Writing

**Input:** Research findings + outline
**Process:**
1. Draft article based on research
2. Integrate findings with citations
3. Check for logical flow

**Output:** First draft (AI-generated style)

---

### Phase 4: Humanize (humanize-writing)

**Input:** First draft
**Process:**
1. Detect AI patterns
2. Replace generic openings
3. Add personal voice
4. Vary sentence structure
5. Add contractions

**Output:** Humanized draft

---

### Phase 5: Quality Check (content-evaluator)

**Input:** Humanized draft + target platform
**Process:**
1. Score 4 dimensions (content/structure/expression/platform)
2. Detect issues (factual, logical, style)
3. Check against platform standards

**Output:** Score report + issue list

**Checkpoint:**
- Score ≥90: Continue to Phase 6
- Score 80-89: Apply suggestions, re-evaluate
- Score <80: Return to Phase 3 with feedback

---

### Phase 6: Image Generation (content-image-generator)

**Input:** Final article text
**Process:**
1. Analyze content for image opportunities
2. Plan image scheme (≤5 images, positions)
3. Design image specifications
4. Generate prompts
5. Generate 2 variations per image (4 total)
6. **Auto-select best** (no user confirmation needed)

**Output:** Selected images + insertion positions

---

### Phase 7: Formatting (content-formatter)

**Input:** Article + images + target platform
**Process:**
1. Design formatting scheme (style, colors, hierarchy)
2. Insert images at correct positions
3. Apply platform-specific formatting:
   - **公众号**: Markdown with headers, image placeholders
   - **小红书**: Plain text with emojis, bullet points
4. Generate multiple formats if needed

**Output:** Platform-optimized content

---

### Phase 8: Delivery

**For 公众号:**
- Markdown version (for 墨滴/Markdown Nice)
- HTML version
- Image files
- **飞书通知用户**: "排版完成，请查收文件"

**For 小红书:**
- Formatted text (ready to copy)
- Image files
- **飞书通知用户**: "内容已生成，请查收"

---

## Checkpoint Rules

### Checkpoint 1: After Research
- **Condition:** >30% sources outdated
- **Action:** Re-search with stricter date filters
- **Notify:** User if still insufficient fresh sources

### Checkpoint 2: After Quality Check
- **Condition:** Score <90
- **Action:** 
  - 80-89: Auto-fix issues, re-evaluate
  - <80: Return to writing with detailed feedback
- **Notify:** User if multiple iterations needed

### Checkpoint 3: Before Final Delivery
- **Checklist:**
  - [ ] Article content complete
  - [ ] Images generated and selected
  - [ ] Formatting applied
  - [ ] All files ready
- **Action:** Send via 飞书 with summary

---

## Usage

### Command Line

```bash
# Full workflow
python3 scripts/create_content.py \
  --topic "AI工具推荐" \
  --platform wechat \
  --output ./article/

# With custom config
python3 scripts/create_content.py \
  --topic "效率提升技巧" \
  --platform xiaohongshu \
  --style casual \
  --images 3 \
  --output ./content/
```

### As Library

```python
from self_media_creator import Creator

creator = Creator(platform="wechat")
result = creator.create(
    topic="AI写作工具对比",
    style="professional",
    notify=True
)
```

---

## Configuration

### Platform Defaults

**公众号 (WeChat):**
```json
{
  "target_length": 1500,
  "min_score": 90,
  "max_images": 5,
  "freshness_rules": {
    "technology": 3,
    "data": 5,
    "trends": 7
  }
}
```

**小红书 (Xiaohongshu):**
```json
{
  "target_length": 300,
  "min_score": 85,
  "max_images": 3,
  "freshness_rules": {
    "technology": 3,
    "data": 5,
    "trends": 7
  }
}
```

---

## Resources

### scripts/
- `create_content.py` - Main orchestration script
- `workflow_runner.py` - Step-by-step workflow execution

### references/
- `workflow-guide.md` - Detailed workflow documentation
- `skill-integration.md` - How sub-skills are integrated
- `troubleshooting.md` - Common issues and solutions
