---
name: content-evaluator
description: Evaluate and score content quality across multiple dimensions. Use when assessing articles, blog posts, or social media content for quality, structure, expression, and platform fit. Detects issues like factual errors, logical inconsistencies, repetitive content, and platform violations. Outputs detailed scores, issue reports, and improvement suggestions. Supports configurable scoring criteria and pass/fail thresholds.
---

# Content Evaluator

Evaluate content quality with multi-dimensional scoring.

## Overview

This skill assesses content across four key dimensions: content quality, structure, expression, and platform fit. Identifies issues and provides actionable improvement suggestions.

## Scoring Dimensions

### 1. Content Quality (30 points)

| Sub-dimension | Points | Criteria |
|--------------|--------|----------|
| Accuracy | 10 | Facts are verifiable, no suspicious claims |
| Depth | 10 | Analysis goes beyond surface level |
| Originality | 10 | Unique insights, not generic advice |

**Detection:**
- Claims without sources
- Generic statements
- Surface-level analysis
- Clichés and platitudes

### 2. Structure Quality (25 points)

| Sub-dimension | Points | Criteria |
|--------------|--------|----------|
| Logic | 10 | Arguments are sound and well-supported |
| Coherence | 8 | Smooth transitions between sections |
| Completeness | 7 | Clear intro and conclusion |

**Detection:**
- Logical fallacies
- Missing transitions
- Abrupt topic changes
- Weak opening/closing

### 3. Expression Quality (25 points)

| Sub-dimension | Points | Criteria |
|--------------|--------|----------|
| Readability | 10 | Appropriate sentence complexity |
| Fluency | 8 | Natural flow, no awkward phrasing |
| Engagement | 7 | Hook, storytelling, holds attention |

**Detection:**
- Overly long sentences
- Awward phrasing
- Weak hook
- Boring passages

### 4. Platform Fit (20 points)

| Sub-dimension | Points | Criteria |
|--------------|--------|----------|
| Format | 10 | Follows platform conventions |
| Length | 5 | Appropriate word count |
| Engagement | 5 | Encourages interaction |

**Platform-specific criteria:**
- **公众号**: Proper headers, image placement, length 800-3000字
- **小红书**: Mobile-friendly, emoji usage, 200-500字

## Evaluation Workflow

### Step 1: Basic Analysis

Gather baseline metrics:
- Word count
- Paragraph count
- Sentence count
- Average sentence length
- Structure breakdown

### Step 2: Issue Detection

Scan for:
- **Factual claims** (flag for verification)
- **Sensitive content** (check against word lists)
- **Repetition** (similar sentences/paragraphs)
- **Logical gaps** (missing connections)

### Step 3: Dimension Scoring

Score each dimension based on detected patterns:
```
Score = Base - Deductions + Bonuses
```

### Step 4: Generate Report

Output includes:
- Total score (0-100)
- Dimension breakdown
- Issue list (prioritized)
- Improvement suggestions
- Pass/fail verdict

## Input/Output

**Input:**
```json
{
  "content": "文章正文...",
  "platform": "wechat" | "xiaohongshu",
  "config": {
    "pass_threshold": 90,
    "weights": {
      "content": 30,
      "structure": 25,
      "expression": 25,
      "platform": 20
    }
  }
}
```

**Output:**
```json
{
  "total_score": 85,
  "passed": false,
  "dimensions": {
    "content": {
      "score": 28,
      "max": 30,
      "breakdown": {
        "accuracy": 9,
        "depth": 10,
        "originality": 9
      }
    },
    "structure": { "score": 22, "max": 25, ... },
    "expression": { "score": 20, "max": 25, ... },
    "platform": { "score": 15, "max": 20, ... }
  },
  "issues": [
    {
      "severity": "warning" | "error",
      "type": "fact_check" | "logic" | "style" | "platform",
      "location": "第3段第2句",
      "description": "数据引用缺少来源",
      "suggestion": "添加数据来源或改为定性描述"
    }
  ],
  "suggestions": [
    "开头可以更吸引人，建议用具体案例引入",
    "第2节逻辑跳跃，建议添加过渡句"
  ],
  "summary": "内容整体质量良好，但存在数据来源和逻辑衔接问题..."
}
```

## Integration with Content Pipeline

```
写作模块
    ↓
质检/打分模块
    ↓
分数 ≥ 阈值? 
    ├── 是 → 继续配图模块
    └── 否 → 返回写作模块
              ↓
        附带质检报告
        (具体问题+改进建议)
```

## Configuration

### Default Thresholds

| Platform | Pass Threshold | Ideal Score |
|----------|---------------|-------------|
| 公众号 | 90 | 95+ |
| 小红书 | 85 | 90+ |

### Issue Severity Levels

- **Error**: Must fix (factual errors, platform violations)
- **Warning**: Should fix (logical gaps, weak expression)
- **Suggestion**: Could improve (minor style issues)

## Resources

### scripts/
- `evaluate.py` - Main evaluation script
- `detect_issues.py` - Issue detection utilities

### references/
- `scoring-rubric.md` - Detailed scoring criteria
- `platform-standards.md` - Platform-specific requirements
- `sensitive-words.md` - Content moderation word lists
