# Content Freshness Guidelines

## Freshness Rules by Domain

### Technology (3 months)

**Applies to:**
- AI/ML models and tools
- Software releases and updates
- Programming languages and frameworks
- Hardware products
- API documentation

**Why 3 months:**
Technology changes rapidly. 3-month-old information about AI tools may already be outdated.

**Examples:**
- ✅ "ChatGPT-4 released in January 2026" - Fresh
- ⚠️ "GPT-4 capabilities from October 2025" - Check for updates
- ❌ "Best AI tools of 2025" - Outdated, needs 2026 update

**Red flags:**
- Version numbers without dates
- "Latest" without timestamp
- Feature lists without version context

---

### Data & Statistics (5 months)

**Applies to:**
- Market size and growth
- User statistics
- Survey results
- Financial figures
- Performance metrics

**Why 5 months:**
Data has longer validity but still needs regular updates for accuracy.

**Examples:**
- ✅ "Q4 2025 market report" - Acceptable in March 2026
- ⚠️ "Mid-2025 user statistics" - Aging, verify still relevant
- ❌ "2024 annual report" - Outdated for current analysis

**Red flags:**
- Round numbers without sources
- "Studies show" without citation
- Percentages without base numbers

---

### Industry Trends (7 months)

**Applies to:**
- Market analysis
- Strategy recommendations
- Best practices
- Case studies
- Industry predictions

**Why 7 months:**
Trends evolve more slowly but can shift significantly in half a year.

**Examples:**
- ✅ "2025 year-end trend analysis" - Still relevant
- ⚠️ "Summer 2025 industry outlook" - Check for major shifts
- ❌ "2024 trend predictions" - Likely outdated

**Red flags:**
- Predictions without timelines
- Trends without supporting data
- "Everyone is doing X" without evidence

---

### General Knowledge (12+ months)

**Applies to:**
- Historical facts
- Fundamental concepts
- Established theories
- Classic examples
- Core principles

**Why 12+ months:**
Foundational knowledge doesn't expire.

**Examples:**
- ✅ "First iPhone released in 2007" - Timeless
- ✅ "Pythagorean theorem" - Permanent
- ✅ "Moore's Law" - Established concept

**Exception:** Even general knowledge should be verified if:
- New research contradicts it
- Context has changed significantly
- Used to support current claims

---

## Date Parsing Guide

### Common Date Formats

| Format | Example | Parsed |
|--------|---------|--------|
| ISO 8601 | 2026-03-01 | ✅ 2026-03-01 |
| Chinese | 2026年3月1日 | ✅ 2026-03-01 |
| Month-Year | 2026-03 | ✅ 2026-03-01 |
| Relative | "last month" | ⚠️ Needs context |
| Vague | "recently" | ❌ Flag for verification |

### Date Extraction Tips

**From URLs:**
- `/2026/03/01/article-name` → 2026-03-01
- `/article-20260301` → 2026-03-01

**From Content:**
- "Published on March 1, 2026" → 2026-03-01
- "Updated: 2026-03-01" → 2026-03-01 (use update date)
- "© 2026 Company" → 2026 (year only, less precise)

**Priority:**
1. Article publication date
2. Last updated date
3. Copyright year (least preferred)

---

## Handling Outdated Information

### Decision Tree

```
Is information outdated?
    ↓
Is it critical to the content?
    ├── No → Keep with date annotation
    └── Yes → Can it be updated?
              ├── Yes → Search for newer version
              └── No → Flag for user review
```

### Strategies

**1. Replace with newer source**
- Search for same topic with date filter
- Prefer same publisher if available

**2. Annotate with date**
- "As of October 2025..."
- "According to 2025 data..."

**3. Remove if not essential**
- Omit outdated examples
- Replace with timeless alternatives

**4. Flag for manual review**
- When no replacement found
- When outdated but historically relevant

---

## Freshness Score Interpretation

| Score | Status | Action |
|-------|--------|--------|
| 10 | Excellent | Use confidently |
| 8-9 | Good | Use, minor preference for newer |
| 6-7 | Acceptable | Use with date annotation |
| 4-5 | Aging | Verify relevance, prefer update |
| 0-3 | Outdated | Replace or flag |

---

## Special Cases

### Breaking News
- Validity: Days to weeks
- Check for follow-up coverage
- Verify initial reports with confirmation

### Academic Papers
- Preprints: Treat as technology (3 months)
- Published: Treat as trends (7 months)
- Reviews: Treat as general (12 months)

### Official Documentation
- API docs: Technology (3 months)
- Policy docs: Trends (7 months)
- Legal docs: General (12 months)

### User-Generated Content
- Reddit/Forum: Technology (3 months)
- Tutorials: Trends (7 months)
- Reviews: Context-dependent
