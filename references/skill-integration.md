# Skill Integration Reference

## Sub-Skills Integration

### 1. content-research

**Purpose:** Search and validate information freshness

**Integration Point:** Phase 2 (Research)

**Input:**
```python
{
    "query": "AI工具 2026",
    "content_type": "technology",  # technology/data/trends/general
    "min_sources": 5
}
```

**Output:**
```python
{
    "findings": [
        {
            "content": "...",
            "source": "techcrunch.com",
            "date": "2026-02-15",
            "freshness_score": 9,
            "credibility_score": 9,
            "overall_score": 8.8,
            "status": "fresh"
        }
    ],
    "outdated_count": 0,
    "gaps": []
}
```

**Call Pattern:**
```bash
python3 content-research/scripts/research.py \
    --query "{topic}" \
    --type technology \
    --output {output_dir}/research.json
```

---

### 2. content-evaluator

**Purpose:** Quality scoring and issue detection

**Integration Point:** Phase 5 (Quality Check)

**Input:**
```python
{
    "content": "文章正文...",
    "platform": "wechat"  # wechat/xiaohongshu
}
```

**Output:**
```python
{
    "total_score": 88,
    "passed": False,
    "dimensions": {
        "content": {"score": 28, "max": 30},
        "structure": {"score": 22, "max": 25},
        "expression": {"score": 20, "max": 25},
        "platform": {"score": 18, "max": 20}
    },
    "issues": [...],
    "suggestions": [...]
}
```

**Call Pattern:**
```bash
python3 content-evaluator/scripts/evaluate.py \
    --input {content_file} \
    --platform {platform} \
    --output {output_dir}/evaluation.json
```

---

### 3. humanize-writing

**Purpose:** Remove AI patterns, add human voice

**Integration Point:** Phase 4 (Humanize)

**Input:**
```python
{
    "text": "AI-generated draft...",
    "tone": "casual"  # casual/professional/playful
}
```

**Output:**
```python
{
    "original_length": 1500,
    "transformed_length": 1480,
    "transformations_applied": [
        "Replaced generic opening",
        "Added contractions",
        "Varied sentence structure"
    ]
}
```

**Call Pattern:**
```bash
python3 humanize-writing/scripts/transform_text.py \
    --input {draft_file} \
    --output {output_file} \
    --tone {tone} \
    --vary-structure \
    --add-personal
```

---

### 4. content-image-generator

**Purpose:** Generate contextual images

**Integration Point:** Phase 6 (Image Generation)

**Input:**
```python
{
    "content": "文章正文...",
    "max_images": 5,
    "style_preference": "flat_illustration"
}
```

**Output:**
```python
{
    "images": [
        {
            "file_path": "./images/cover.png",
            "position": "after_title",
            "description": "封面图"
        }
    ],
    "total_cost": "0.8元"
}
```

**Call Pattern:**
```bash
# Step 1: Generate
python3 content-image-generator/scripts/generate_images.py \
    --prompts {prompts_file} \
    --output {image_dir} \
    --model seedream

# Step 2: Select
python3 content-image-generator/scripts/select_best.py \
    --results {generation_results} \
    --output {selected_file}
```

---

### 5. content-formatter

**Purpose:** Platform-specific formatting

**Integration Point:** Phase 7 (Formatting)

**Input:**
```python
{
    "content": "文章正文...",
    "images": [...],
    "platform": "wechat"  # wechat/xiaohongshu
}
```

**Output:**
```python
{
    "platform": "wechat",
    "formatted_content": "# 标题\n\n...",
    "images_inserted": ["cover.png", "diagram.png"]
}
```

**Call Pattern:**
```bash
# For 公众号
python3 content-formatter/scripts/format_wechat.py \
    --input {content_file} \
    --images {images_json} \
    --output {output_file}

# For 小红书
python3 content-formatter/scripts/format_xiaohongshu.py \
    --input {content_file} \
    --output {output_file} \
    --tone casual
```

---

## Data Flow

```
Input Topic
    ↓
[content-research] → research.json
    ↓
Writing (internal)
    ↓
[humanize-writing] → humanized.txt
    ↓
[content-evaluator] → evaluation.json
    ↓ (if score < 90, loop back)
[content-image-generator] → images/
    ↓
[content-formatter] → final.txt
    ↓
Output + Notification
```

## Error Handling by Skill

| Skill | Common Errors | Handling Strategy |
|-------|--------------|-------------------|
| content-research | No results | Expand query, reduce specificity |
| content-research | All outdated | Use general knowledge, flag user |
| content-evaluator | Low score | Auto-fix or return to writing |
| humanize-writing | Over-transformation | Reduce intensity, preserve meaning |
| content-image-generator | Generation fail | Use placeholders, continue |
| content-formatter | Format error | Fallback to plain text |

## Configuration Passing

### Global Config
```python
config = {
    "platform": "wechat",
    "style": "professional",
    "min_score": 90,
    "max_images": 5,
    "freshness_rules": {...}
}
```

### Skill-Specific Overrides
```python
# content-research
research_config = {
    **global_config,
    "min_sources": 5,
    "content_type": "technology"
}

# content-evaluator
eval_config = {
    **global_config,
    "weights": {...}  # Custom scoring weights
}
```

## File Naming Convention

```
{output_dir}/
├── research.json          # content-research output
├── draft.txt              # Initial draft
├── humanized.txt          # humanize-writing output
├── evaluation.json        # content-evaluator output
├── images/
│   ├── cover_v1.png
│   ├── cover_v2.png
│   └── selected.json
├── final_wechat.txt       # content-formatter output
└── summary.json           # Workflow summary
```
