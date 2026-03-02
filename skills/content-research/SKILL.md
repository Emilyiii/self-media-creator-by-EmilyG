---
name: content-research
description: Research and gather information for content creation with freshness validation. Use when searching for latest information, verifying source credibility, and checking data freshness for articles, reports, or any content requiring up-to-date information. Supports web search, source evaluation, and freshness scoring. Ensures content relies on current, credible sources.
---

# Content Research

Research and validate information for content creation.

## Overview

This skill handles information gathering with a focus on **freshness** and **credibility**. It searches for latest information, evaluates sources, and flags outdated content.

## Why Freshness Matters

**Problem:** AI models and search results often return outdated information (e.g., "2025年2月" data when it's 2026年3月)

**Impact:**
- Incorrect statistics
- Outdated tool recommendations
- Misleading trends
- Loss of credibility

**Solution:** Systematic freshness checking with clear cutoff dates.

## Freshness Rules

### By Content Type

| Type | Freshness Requirement | Cutoff Date |
|------|----------------------|-------------|
| **Technology** | Very High | 3 months (2025-12) |
| **Data/Statistics** | High | 5 months (2025-10) |
| **Industry Trends** | Medium | 7 months (2025-08) |
| **General Knowledge** | Low | 12+ months acceptable |

### By Topic Category

**Technology (3 months):**
- AI tools and models
- Software updates
- Hardware releases
- API changes

**Data/Statistics (5 months):**
- Market data
- User statistics
- Survey results
- Financial figures

**Industry Trends (7 months):**
- Market analysis
- Strategy recommendations
- Best practices
- Case studies

**General Knowledge (12+ months):**
- Historical facts
- Fundamental concepts
- Established theories
- Classic examples

## Research Workflow

### Step 1: Query Generation

Transform content outline into search queries:
- Extract key topics
- Generate 3-5 search queries per topic
- Prioritize recency keywords ("2026", "latest", "new")

### Step 2: Information Gathering

Search multiple sources:
- Web search (Brave, Google)
- News sources
- Official documentation
- Academic papers

### Step 3: Source Evaluation

Score each source on:
- **Credibility** (0-10): Authority of publisher
- **Freshness** (0-10): How recent is the information
- **Relevance** (0-10): Match to content needs

**Overall Score = (Credibility × 0.4) + (Freshness × 0.4) + (Relevance × 0.2)**

### Step 4: Freshness Validation

For each piece of information:
1. Extract publication date
2. Compare to cutoff date for content type
3. Flag if outdated
4. Suggest re-search if needed

**Freshness Score:**
- 10: Within 1 month
- 8-9: Within 3 months
- 6-7: Within 6 months
- 4-5: Within 12 months
- 0-3: Over 12 months (flag for update)

### Step 5: Output Generation

Return validated information with metadata:
```json
{
  "topic": "AI工具趋势",
  "findings": [
    {
      "content": "...",
      "source": "...",
      "date": "2026-02-15",
      "freshness_score": 9,
      "credibility_score": 8,
      "status": "fresh"
    }
  ],
  "outdated_items": [],
  "gaps": ["需要更多2026年Q1数据"]
}
```

## Input/Output

**Input:**
```json
{
  "outline": "文章大纲...",
  "topics": ["AI工具", "效率提升"],
  "content_type": "technology",
  "min_sources": 5,
  "max_age_months": 3
}
```

**Output:**
```json
{
  "research_id": "uuid",
  "query_time": "2026-03-01T10:00:00Z",
  "findings": [
    {
      "topic": "AI工具",
      "content": "...",
      "source": "...",
      "source_url": "...",
      "date": "2026-02-20",
      "freshness_score": 9,
      "credibility_score": 8,
      "overall_score": 8.6,
      "status": "fresh"
    }
  ],
  "outdated_count": 0,
  "gaps": [],
  "summary": "找到8个有效来源，全部符合时效性要求"
}
```

## Integration with Writing Pipeline

```
写作模块
    ↓
生成搜索查询
    ↓
调用 content-research Skill
    ↓
获取带时效评级的资料
    ↓
检查：有超期资料？
    ├── 是 → 重新搜索/标记待核实
    └── 否 → 继续写作
    ↓
拟写文章（引用带日期标记）
```

## Usage

```bash
# Research with freshness check
python3 scripts/research.py \
  --query "AI工具 2026" \
  --type technology \
  --output results.json

# Validate existing sources
python3 scripts/validate_freshness.py \
  --sources sources.json \
  --type data \
  --output validation.json
```

## Resources

### scripts/
- `research.py` - Main research with freshness validation
- `validate_freshness.py` - Check existing sources
- `source_evaluator.py` - Score source credibility

### references/
- `freshness-guidelines.md` - Detailed freshness rules by domain
- `source-ratings.md` - Trusted source database
- `search-tips.md` - Advanced search strategies
