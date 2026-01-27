---
name: news-aggregator
description: Comprehensive news aggregator that fetches, filters, and deeply analyzes real-time content from 8 major sources.
status: active
type: execution
---

# News Aggregator Skill

Fetch real-time hot news from multiple sources.

## Agent Instructions

### Command Construction

- **Keyword Expansion**: Automatically expand user topics.
  - User: "AI" -> `--keyword "AI,LLM,GPT,Claude,Generative,Machine Learning,RAG"`
  - User: "Finance" -> `--keyword "Finance,Stock,Market,Economy,Crypto"`
- **Sources**: `hackernews`, `weibo`, `github`, `36kr`, `producthunt`, `v2ex`, `tencent`, `wallstreetcn`, `all`.
- **Deep Mode**: Use `--deep` when the user wants content analysis, not just headlines.

### Smart Fill Logic (CRITICAL)

- **Time Window**: If user asks for "past X hours" and results are sparse (< 5), **YOU MUST** include older high-value items to fill the report. Mark them as "⚠️ Older" or "🔥 Hot".
- **GitHub Trending**: Do NOT apply smart fill. Return exact list.

## Response Guidelines

**Format**: Magazine/Newsletter style (Simplified Chinese).
**Structure**:

- **Global Headlines**: Top 3-5 stories.
- **Tech/Domain**: Specific domain news.
- **Item**:
  - `### [Title](Link)`
  - `Metadata`: Source | Time | Heat
  - `Summary`: 1-line punchy summary.
  - `Deep Analysis` (if --deep): 2-3 bullet points on _why_ it matters.
