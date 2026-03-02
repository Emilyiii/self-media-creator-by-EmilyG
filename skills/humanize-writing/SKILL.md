---
name: humanize-writing
description: Remove AI-like characteristics from text and rewrite in a more natural, human voice. Use when content sounds robotic, overly structured, or lacks personality. Detects common AI writing patterns (generic openings, excessive signposting, formal stiffness) and transforms them into authentic, engaging prose. Works for articles, essays, social media posts, and any text that needs a more personal touch.
---

# Humanize Writing

Transform AI-generated text into natural, human-sounding prose.

## Overview

This skill identifies and removes common AI writing patterns, replacing them with authentic human expression. It preserves the original meaning while adding personality, variability, and natural flow.

## Common AI Patterns to Remove

### 1. Generic Openings
**AI patterns:**
- "In today's world..."
- "In the rapidly evolving landscape of..."
- "As we all know..."
- "It's important to note that..."

**Human alternatives:**
- Start with a specific observation or question
- Jump directly into the topic
- Use a personal anecdote

### 2. Excessive Signposting
**AI patterns:**
- "First... Second... Third... Finally..."
- "In conclusion..."
- "Let's dive in..."
- "Without further ado..."

**Human alternatives:**
- Use natural transitions
- Let structure emerge organically
- Vary transition phrases

### 3. Overly Formal Language
**AI patterns:**
- "It is worth noting that..."
- "One could argue that..."
- "It should be mentioned..."
- "Furthermore... Moreover..."

**Human alternatives:**
- Contractions (don't, can't, it's)
- Direct statements
- Conversational tone

### 4. Lack of Specificity
**AI patterns:**
- Generic examples
- Vague statements
- "Many people..." "Some experts..."
- "Various studies show..."

**Human alternatives:**
- Concrete details
- Specific references
- Personal experiences

### 5. Perfect Structure
**AI patterns:**
- Uniform paragraph lengths
- Predictable patterns
- Overly balanced arguments
- Missing imperfections

**Human alternatives:**
- Varied sentence lengths
- Occasional fragments
- Natural digressions
- Imperfect but authentic flow

## Transformation Process

### Step 1: Detect AI Patterns

Scan text for:
- [ ] Generic opening phrases
- [ ] Excessive signposting
- [ ] Overly formal constructions
- [ ] Vague or generic statements
- [ ] Perfectly parallel structure

### Step 2: Analyze Context

Determine:
- Target audience
- Intended tone (casual/professional/playful)
- Content type (blog/essay/social media)
- Author persona

### Step 3: Apply Transformations

**Structural changes:**
- Break up overly regular patterns
- Vary paragraph lengths
- Add natural digressions
- Remove unnecessary transitions

**Language changes:**
- Replace formal phrases with casual alternatives
- Add contractions
- Use active voice
- Include personal pronouns (I, we, you)

**Content changes:**
- Add specific examples
- Include minor imperfections
- Add parenthetical asides
- Use rhetorical questions

### Step 4: Preserve Meaning

Ensure:
- Core message intact
- Key facts preserved
- Logical flow maintained
- Only style changes, not substance

## Transformation Examples

### Example 1: Opening

**Before (AI):**
> In today's rapidly evolving digital landscape, it is crucial for professionals to stay updated with the latest tools and technologies. This article will explore five essential productivity tools that can help streamline your workflow.

**After (Humanized):**
> I spent last year drowning in browser tabs and half-finished to-do lists. Then I discovered these five tools. They're not magic, but they saved my sanity—and about 10 hours a week.

### Example 2: Body Paragraph

**Before (AI):**
> First, it is worth noting that effective time management requires careful planning. Second, one must prioritize tasks based on importance and urgency. Third, regular breaks are essential for maintaining productivity.

**After (Humanized):**
> Here's what actually works: plan your day the night before (yes, even if you're tired), tackle the scary stuff first while your coffee's still hot, and for god's sake take breaks—your brain isn't a machine.

### Example 3: Conclusion

**Before (AI):**
> In conclusion, the strategies discussed above provide a comprehensive framework for improving productivity. By implementing these techniques, readers can expect to see significant improvements in their workflow efficiency.

**After (Humanized):**
> Look, productivity advice is everywhere and most of it is garbage. But these actually helped me, so maybe they'll help you too. Start with one. See how it goes.

## Tone Options

### Casual
- Contractions everywhere
- Slang and colloquialisms
- Personal stories
- Imperfect grammar (occasionally)

### Professional but Human
- Clear but not stiff
- Some contractions
- Direct statements
- Occasional personality

### Playful
- Humor and wit
- Creative metaphors
- Exclamation points (sparingly)
- Engaging rhetorical questions

## Input/Output

**Input:**
```json
{
  "text": "AI-generated content...",
  "tone": "casual" | "professional" | "playful",
  "preserve_structure": false,
  "add_personal_touch": true
}
```

**Output:**
```json
{
  "original_text": "...",
  "humanized_text": "...",
  "changes_made": [
    "Removed generic opening",
    "Added personal anecdote",
    "Replaced formal phrases"
  ],
  "confidence_score": 0.92
}
```

## Resources

### references/
- `ai-patterns.md` - Comprehensive catalog of AI writing patterns
- `transformation-guide.md` - Detailed transformation strategies

### scripts/
- `analyze_text.py` - Detect AI patterns in text
- `transform_text.py` - Apply humanizing transformations
