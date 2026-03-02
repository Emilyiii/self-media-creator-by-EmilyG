# Workflow Guide

## Complete Workflow Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    自媒体创作 Agent                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐      │
│  │ 1.选题  │ → │ 2.研究  │ → │ 3.写作  │ → │ 4.润色  │      │
│  └─────────┘   └────┬────┘   └─────────┘   └─────────┘      │
│                     │                                        │
│                     ↓ Checkpoint 1                           │
│              ┌─────────────┐                                 │
│              │ 资料时效检查  │                                │
│              └──────┬──────┘                                 │
│                     │                                        │
│              ┌──────┴──────┐                                 │
│              │ >30%过期?   │                                 │
│              └──────┬──────┘                                 │
│              是 ↓    ↓ 否                                    │
│         ┌────────┐  └────────┐                               │
│         │重新搜索│           ↓                               │
│         └────────┘    ┌─────────┐   ┌─────────┐             │
│                       │ 5.质检  │ → │ 6.配图  │             │
│                       └────┬────┘   └─────────┘             │
│                            │                                 │
│                            ↓ Checkpoint 2                    │
│                     ┌─────────────┐                          │
│                     │ 分数 ≥ 90?  │                          │
│                     └──────┬──────┘                          │
│              <80 ↓  80-89 ↓    ↓ ≥90                        │
│         ┌────────┐ ┌────────┐ └────────┐                     │
│         │重写+反馈│ │自动修复│          ↓                     │
│         └────────┘ └────────┘   ┌─────────┐   ┌─────────┐   │
│                                 │ 7.排版  │ → │ 8.交付  │   │
│                                 └─────────┘   └────┬────┘   │
│                                                    │         │
│                                                    ↓         │
│                                              ┌─────────┐    │
│                                              │飞书通知 │    │
│                                              └─────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Phase Details

### Phase 1: Topic Selection
**Duration:** 2-5 minutes
**Input:** Theme or direction
**Output:** 3-5 topic options
**Action:** User selects one

### Phase 2: Research (content-research)
**Duration:** 3-8 minutes
**Key Steps:**
1. Generate search queries
2. Search web sources
3. Extract publication dates
4. Calculate freshness scores
5. Filter outdated sources

**Checkpoint 1 Rules:**
- Outdated ratio ≤30%: Continue
- Outdated ratio >30%: Re-search with date filters
- After 3 attempts: Flag to user

### Phase 3: Writing
**Duration:** 5-10 minutes
**Input:** Research findings
**Output:** First draft
**Style:** AI-generated, structured

### Phase 4: Humanize (humanize-writing)
**Duration:** 2-3 minutes
**Transformations:**
- Remove AI patterns
- Add personal voice
- Vary sentence structure
- Add contractions

### Phase 5: Quality Check (content-evaluator)
**Duration:** 1-2 minutes
**Dimensions:**
- Content quality (30%)
- Structure quality (25%)
- Expression quality (25%)
- Platform fit (20%)

**Checkpoint 2 Rules:**
| Score | Action |
|-------|--------|
| ≥90 | Continue to Phase 6 |
| 80-89 | Auto-fix, re-evaluate (max 2 times) |
| <80 | Return to Phase 3 with feedback |

### Phase 6: Image Generation (content-image-generator)
**Duration:** 2-5 minutes (depends on API)
**Steps:**
1. Analyze content for image opportunities
2. Plan image scheme (≤5 images)
3. Generate prompts
4. Generate 2 variations per image
5. Auto-select best

**Cost:** ~0.8元 for 4 images (Seedream)

### Phase 7: Formatting (content-formatter)
**Duration:** 1-2 minutes
**Platform-specific:**
- **公众号**: Markdown with headers, image placeholders
- **小红书**: Plain text with emojis, bullet points

### Phase 8: Delivery
**Duration:** 1 minute
**Actions:**
1. Save all files
2. Generate summary
3. Send 飞书 notification
4. Attach files

## Timing Estimates

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Topic | 2-5 min | 2-5 min |
| Research | 3-8 min | 5-13 min |
| Writing | 5-10 min | 10-23 min |
| Humanize | 2-3 min | 12-26 min |
| Evaluation | 1-2 min | 13-28 min |
| Images | 2-5 min | 15-33 min |
| Formatting | 1-2 min | 16-35 min |
| Delivery | 1 min | 17-36 min |

**Total:** ~20-40 minutes for complete article

## Error Handling

### Research Phase
- **No sources found:** Expand search terms, try alternative keywords
- **All sources outdated:** Use general knowledge, flag to user
- **API error:** Retry 2 times, then use cached/default data

### Writing Phase
- **Writer's block:** Use outline expansion technique
- **Content too short:** Add examples, expand key points
- **Content too long:** Summarize, move details to appendix

### Quality Phase
- **Score stuck at 80-89:** Try different humanize tone
- **Repeated failures:** Simplify topic, reduce scope
- **Platform mismatch:** Re-format specifically for target

### Image Phase
- **Generation failed:** Use placeholder, continue workflow
- **All images rejected:** Reduce count, simplify prompts
- **API quota exceeded:** Queue for later, notify user

## Best Practices

### For 公众号
- Target 1500-2500 characters
- Use 3-5 images
- Include code blocks if technical
- End with question for engagement

### For 小红书
- Target 200-400 characters
- Use 3 images max
- Front-load value in first 2 lines
- Include 3-5 relevant hashtags

### General
- Always check freshness for tech content
- Score <90 requires attention
- Keep backup of each phase output
- Notify user at key checkpoints
