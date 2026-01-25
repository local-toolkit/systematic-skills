---
name: trendradar
description: Comprehensive Chinese news aggregation and trend analysis tool with AI-powered sentiment analysis, topic trend detection, period comparison, and RSS subscription management.
status: active
type: execution
---

# TrendRadar Expert Skill

AI-driven public opinion & trend monitor for comprehensive Chinese news aggregation and analysis.

## Overview

TrendRadar provides **21 powerful MCP tools** for:

- 📰 **News Aggregation**: Hot topics from Chinese platforms (Baidu, Weibo, Zhihu, Douyin, etc.)
- 📡 **RSS Subscriptions**: Hacker News, 36Kr, and custom RSS feeds
- 📊 **AI Analysis**: Sentiment analysis, trend detection, topic lifecycle
- 🔍 **Smart Search**: Keyword search, fuzzy matching, related news discovery
- 📈 **Period Comparison**: Week-over-week, month-over-month analysis
- 💾 **Data Sync**: Local/remote storage management

---

# Tool Categories

## 📅 Date Resolution (Priority Tool)

### `resolve_date_range`
**Purpose**: Parse natural language date expressions to standard format

**Why Important**: Ensures consistent date parsing across all AI models. Use this before any date-based queries.

**Examples**:
- "本周" → `{"start": "2025-01-20", "end": "2025-01-26"}`
- "最近7天" → `{"start": "2025-01-19", "end": "2025-01-26"}`
- "上周" → `{"start": "2025-01-13", "end": "2025-01-19"}`

---

## 📰 Query Tools

### `get_latest_news`
**Purpose**: Get latest crawled hot news from all platforms

**Parameters**:
- `platforms` (array, optional): Platform IDs like `['zhihu', 'weibo', 'baidu']`
- `limit` (int, default 50): Max items (max 1000)
- `include_url` (bool, default false): Include URL links (costs more tokens)

**Usage Examples**:
```bash
# Get latest news (default 50 items)
get_latest_news()

# Get specific platforms with more items
get_latest_news(platforms=['zhihu', 'weibo'], limit=100)

# Get news with URLs
get_latest_news(include_url=true)
```

---

### `get_news_by_date`
**Purpose**: Query historical news by date range

**Parameters**:
- `date_range` (object): Format `{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}` OR natural language string
- `platforms` (array, optional): Platform filter
- `limit` (int, default 50): Max items
- `include_url` (bool, default false): Include URLs

**Usage Examples**:
```bash
# Query today's news
get_news_by_date(date_range="today")

# Query specific date range
get_news_by_date(date_range={"start": "2025-01-01", "end": "2025-01-07"})

# Use natural language (RECOMMENDED: resolve_date_range first)
get_news_by_date(date_range="本周")
```

---

### `get_trending_topics`
**Purpose**: Get trending topics statistics

**Parameters**:
- `top_n` (int, default 10): Return TOP N topics
- `mode` (string, default "current"): Time mode - "daily" or "current"
- `extract_mode` (string, default "keywords"): Extraction mode
  - `"keywords"`: Use preset keywords from config/frequency_words.txt
  - `"auto_extract"`: Auto-extract from news titles (no preset needed)

**Usage Examples**:
```bash
# Get trending topics with preset keywords
get_trending_topics(top_n=20, mode="current")

# Auto-extract trending topics (discover what's hot)
get_trending_topics(extract_mode="auto_extract", top_n=20)
```

---

## 📡 RSS Tools

### `get_latest_rss`
**Purpose**: Get latest RSS subscription content (multi-day support)

**Parameters**:
- `feeds` (array, optional): RSS feed IDs like `['hacker-news', '36kr']`
- `days` (int, default 1): Get recent N days (max 30 days)
- `limit` (int, default 50): Max items per source
- `include_summary` (bool, default false): Include article summaries

**Usage Examples**:
```bash
# Get latest RSS (today only)
get_latest_rss()

# Get last 7 days of Hacker News
get_latest_rss(feeds=['hacker-news'], days=7, limit=50)

# Get multiple feeds with summaries
get_latest_rss(feeds=['hacker-news', '36kr'], include_summary=true)
```

---

### `search_rss`
**Purpose**: Search RSS data for keywords

**Parameters**:
- `keyword` (string, required): Search keyword
- `feeds` (array, optional): Feed filter
- `days` (int, default 7): Search recent N days (max 30)
- `limit` (int, default 50): Max items
- `include_summary` (bool, default false): Include summaries

**Usage Examples**:
```bash
# Search for AI articles
search_rss(keyword="AI", days=7)

# Search Hacker News for Python
search_rss(keyword="Python", feeds=['hacker-news'], days=14)
```

---

### `get_rss_feeds_status`
**Purpose**: Get RSS source status and statistics

**Returns**: Available dates, total dates, today's feed statistics

**Usage**:
```bash
# View all RSS feeds status
get_rss_feeds_status()
```

---

## 🔍 Search Tools

### `search_news`
**Purpose**: Unified search across hotlist and optionally RSS

**Parameters**:
- `query` (string, required): Search keyword or content fragment
- `search_mode` (string, default "keyword"): Search mode
  - `"keyword"`: Exact keyword matching
  - `"fuzzy"`: Fuzzy content matching
  - `"entity"`: Entity name search
- `date_range` (object): Date range (use resolve_date_range for natural language)
- `platforms` (array, optional): Platform filter
- `limit` (int, default 50): Hotlist max items
- `sort_by` (string, default "relevance"): Sort by "relevance", "weight", or "date"
- `threshold` (float, default 0.6): Similarity threshold (fuzzy mode only)
- `include_url` (bool, default false): Include URLs
- `include_rss` (bool, default false): Also search RSS data
- `rss_limit` (int, default 20): RSS max items

**Usage Examples**:
```bash
# Search news about AI
search_news(query="AI", limit=50)

# Search with fuzzy matching
search_news(query="人工智能突破", search_mode="fuzzy", threshold=0.6)

# Search specific date range
search_news(query="特斯拉", date_range={"start": "2025-01-01", "end": "2025-01-07"})

# Search both hotlist and RSS
search_news(query="GPT-5", include_rss=true, rss_limit=20)
```

---

### `find_related_news`
**Purpose**: Find news similar to a given title (today and historical)

**Parameters**:
- `reference_title` (string, required): Full or partial news title
- `date_range` (object/string, optional): Date range
  - Not specified: Only today's data
  - Presets: "today", "yesterday", "last_week", "last_month"
  - Custom: `{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}`
- `threshold` (float, default 0.5): Similarity threshold (0-1, higher = stricter)
- `limit` (int, default 50): Max items
- `include_url` (bool, default false): Include URLs

**Usage Examples**:
```bash
# Find similar news today
find_related_news(reference_title="特斯拉降价")

# Find related news from last week
find_related_news(reference_title="人工智能突破", date_range="last_week")

# Find from specific date range
find_related_news(reference_title="ChatGPT", date_range={"start": "2025-01-01", "end": "2025-01-07"})
```

---

## 📊 Analytics Tools

### `analyze_topic_trend`
**Purpose**: Unified topic trend analysis (hotness/lifecycle/viral/prediction)

**Parameters**:
- `topic` (string, required): Topic keyword
- `analysis_type` (string, default "trend"):
  - `"trend"`: Hotness trend analysis
  - `"lifecycle"`: Lifecycle analysis
  - `"viral"`: Viral outbreak detection
  - `"predict"`: Topic prediction
- `date_range` (object, optional): Date range (use resolve_date_range first)
- `granularity` (string, default "day"): Time granularity
- `spike_threshold` (float, default 3.0): Hotness spike threshold (viral mode)
- `time_window` (int, default 24): Detection window hours (viral mode)
- `lookahead_hours` (int, default 6): Prediction future hours (predict mode)
- `confidence_threshold` (float, default 0.7): Confidence threshold (predict mode)

**Usage Examples**:
```bash
# Analyze AI hotness trend
analyze_topic_trend(topic="AI", analysis_type="trend")

# Check if topic is viral
analyze_topic_trend(topic="比特币", analysis_type="viral", spike_threshold=5.0)

# Predict future trends
analyze_topic_trend(topic="iPhone", analysis_type="predict", lookahead_hours=12)
```

---

### `analyze_data_insights`
**Purpose**: Unified data insights (platform comparison/activity/keyword co-occurrence)

**Parameters**:
- `insight_type` (string, default "platform_compare"):
  - `"platform_compare"`: Compare platform attention to topic
  - `"platform_activity"`: Platform activity statistics
  - `"keyword_cooccur"`: Keyword co-occurrence analysis
- `topic` (string, optional): Topic keyword (platform_compare mode)
- `date_range` (object, optional): Date range object `{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}`
- `min_frequency` (int, default 3): Min co-occurrence frequency (keyword_cooccur mode)
- `top_n` (int, default 20): Return TOP N results

**Usage Examples**:
```bash
# Compare platform attention to AI
analyze_data_insights(insight_type="platform_compare", topic="人工智能")

# Check platform activity
analyze_data_insights(insight_type="platform_activity", date_range={"start": "2025-01-01", "end": "2025-01-07"})

# Keyword co-occurrence analysis
analyze_data_insights(insight_type="keyword_cooccur", min_frequency=5, top_n=15)
```

---

### `analyze_sentiment`
**Purpose**: Analyze news sentiment and hotness trends

**Parameters**:
- `topic` (string, optional): Topic keyword
- `platforms` (array, optional): Platform filter
- `date_range` (object, optional): Date range (use resolve_date_range first)
- `limit` (int, default 50): Max items (deduped by title, max 100)
- `sort_by_weight` (bool, default true): Sort by hotness weight
- `include_url` (bool, default false): Include URLs

**Usage Examples**:
```bash
# Analyze sentiment for AI news
analyze_sentiment(topic="AI", date_range={"start": "2025-01-01", "end": "2025-01-07"})

# Analyze overall sentiment today
analyze_sentiment(limit=50, sort_by_weight=true)

# Analyze specific platform
analyze_sentiment(platforms=['zhihu'], topic="特斯拉")
```

---

### `aggregate_news`
**Purpose**: Cross-platform news deduplication and aggregation

**Parameters**:
- `date_range` (object, optional): Date range (not specified = today)
- `platforms` (array, optional): Platform filter
- `similarity_threshold` (float, default 0.7): Similarity threshold (0.3-1.0, higher = stricter)
- `limit` (int, default 50): Max aggregated items
- `include_url` (bool, default false): Include URLs

**Usage Examples**:
```bash
# Aggregate today's news
aggregate_news()

# Aggregate with stricter matching
aggregate_news(similarity_threshold=0.8)

# Aggregate specific date range
aggregate_news(date_range={"start": "2025-01-01", "end": "2025-01-07"})
```

---

### `compare_periods`
**Purpose**: Period comparison analysis (week-over-week, month-over-month)

**Parameters**:
- `period1` (object/string, required): First period (baseline)
  - Presets: "today", "yesterday", "this_week", "last_week", "this_month", "last_month"
  - Custom: `{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}`
- `period2` (object/string, required): Second period (comparison)
- `topic` (string, optional): Topic keyword (focus on specific topic comparison)
- `compare_type` (string, default "overview"):
  - `"overview"`: Overall overview (news count, keywords, TOP news)
  - `"topic_shift"`: Topic change analysis (rising/falling/new topics)
  - `"platform_activity"`: Platform activity comparison
- `platforms` (array, optional): Platform filter
- `top_n` (int, default 10): Return TOP N results

**Usage Examples**:
```bash
# Week-over-week comparison
compare_periods(period1="last_week", period2="this_week")

# Month-over-month comparison with topic focus
compare_periods(period1="last_month", period2="this_month", topic="人工智能")

# Custom date range comparison
compare_periods(
    period1={"start": "2025-01-01", "end": "2025-01-07"},
    period2={"start": "2025-01-08", "end": "2025-01-14"}
)
```

---

### `generate_summary_report`
**Purpose**: Generate daily/weekly summary reports

**Parameters**:
- `report_type` (string, default "daily"): "daily" or "weekly"
- `date_range` (object, optional): Custom date range object `{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}`

**Usage Examples**:
```bash
# Generate daily summary
generate_summary_report(report_type="daily")

# Generate weekly summary
generate_summary_report(report_type="weekly")

# Custom date range summary
generate_summary_report(report_type="weekly", date_range={"start": "2025-01-01", "end": "2025-01-07"})
```

---

## ⚙️ System Tools

### `get_current_config`
**Purpose**: Get current system configuration

**Parameters**:
- `section` (string, default "all"): Config section
  - `"all"`: All configurations
  - `"crawler"`: Crawler configuration
  - `"push"`: Notification configuration
  - `"keywords"`: Keywords configuration
  - `"weights"`: Weight configuration

**Usage**:
```bash
# Get all configuration
get_current_config(section="all")

# Get crawler config only
get_current_config(section="crawler")
```

---

### `get_system_status`
**Purpose**: Get system running status and health check

**Returns**: System version, data statistics, cache status, last crawl time, available dates

**Usage**:
```bash
# Check system status
get_system_status()
```

---

### `check_version`
**Purpose**: Check version updates (TrendRadar + MCP Server)

**Parameters**:
- `proxy_url` (string, optional): Proxy URL for GitHub access

**Usage**:
```bash
# Check version
check_version()

# Check with proxy
check_version(proxy_url="http://127.0.0.1:7890")
```

---

### `trigger_crawl`
**Purpose**: Manually trigger crawl task (optional persistence)

**Parameters**:
- `platforms` (array, optional): Platform IDs like `['zhihu', 'weibo']`
- `save_to_local` (bool, default false): Save to local output directory
- `include_url` (bool, default false): Include URLs

**Usage Examples**:
```bash
# Temporary crawl (no save)
trigger_crawl(platforms=['zhihu'])

# Persistent crawl (save data)
trigger_crawl(platforms=['zhihu', 'weibo'], save_to_local=true)
```

---

## 💾 Storage Tools

### `sync_from_remote`
**Purpose**: Pull data from remote storage to local

**Parameters**:
- `days` (int, default 7): Pull recent N days data
  - `0`: No pull
  - `7`: Last week
  - `30`: Last month

**Usage Examples**:
```bash
# Sync last 7 days
sync_from_remote(days=7)

# Sync last 30 days
sync_from_remote(days=30)
```

---

### `get_storage_status`
**Purpose**: Get storage configuration and status

**Returns**: Local/remote storage status, pull configuration

**Usage**:
```bash
# Check storage status
get_storage_status()
```

---

### `list_available_dates`
**Purpose**: List available dates in local/remote storage

**Parameters**:
- `source` (string, default "both"):
  - `"local"`: Local only
  - `"remote"`: Remote only
  - `"both"`: Both with comparison (default)

**Usage Examples**:
```bash
# List both local and remote
list_available_dates()

# List local only
list_available_dates(source="local")
```

---

# Best Practices

## 1. Token Optimization

**Default Settings** (to save tokens):
- Limit: 50 items max
- Date: Today only
- URLs: Excluded by default

**When to Adjust**:
- User asks: "返回前 10 条" or "给我 100 条" → Adjust `limit`
- User asks: "查询昨天" or "最近一周" → Set `date_range`
- User asks: "需要链接" or "包含 URL" → Set `include_url=true`

---

## 2. Date Handling

**RECOMMENDED**: Always use `resolve_date_range` first for natural language expressions

**Example Workflow**:
```
User: "分析AI本周的热度趋势"

Step 1: resolve_date_range("本周")
        → {"date_range": {"start": "2025-01-20", "end": "2025-01-26"}}

Step 2: analyze_topic_trend(topic="AI", date_range={"start": "2025-01-20", "end": "2025-01-26"})
```

**Why**: Ensures all AI models get consistent date ranges from server-side calculation.

---

## 3. AI Display Behavior

**Important**: AI models often automatically summarize and only display partial results.

**If you want full data**:
- Method 1: "请展示全部新闻，不要总结"
- Method 2: "展示所有 50 条新闻"
- Method 3: "为什么只展示了 15 条？我要看全部"
- Method 4: "查询今天的新闻，完整展示所有结果"

---

## 4. Data Freshness

**Critical**: News data needs to be crawled first via `trigger_crawl` before analysis.

**If analysis shows no data**:
1. Check: `get_system_status()` → See last crawl time
2. Trigger: `trigger_crawl()` → Crawl fresh data
3. Sync (if using remote): `sync_from_remote()` → Pull to local
4. Retry analysis

---

## 5. Combination Workflows

### Example 1: Deep Topic Analysis
```bash
1. Search: search_news(query="人工智能")
2. Analyze trend: analyze_topic_trend(topic="人工智能", analysis_type="trend")
3. Sentiment analysis: analyze_sentiment(topic="人工智能")
```

### Example 2: Event Tracking
```bash
1. Latest: get_latest_news() with topic filter
2. Historical: get_news_by_date(date_range="上周")
3. Find related: find_related_news(reference_title="iPhone 发布")
```

### Example 3: Period Comparison
```bash
1. Resolve dates: resolve_date_range("本周")
2. Resolve dates: resolve_date_range("上周")
3. Compare: compare_periods(period1="last_week", period2="this_week")
```

---

# Platform IDs Reference

| ID | Name |
|-----|-------|
| `toutiao` | 今日头条 |
| `baidu` | 百度热搜 |
| `wallstreetcn-hot` | 华尔街见闻 |
| `thepaper` | 澎湃新闻 |
| `bilibili-hot-search` | bilibili 热搜 |
| `cls-hot` | 财联社热门 |
| `ifeng` | 凤凰网 |
| `tieba` | 贴吧 |
| `weibo` | 微博 |
| `douyin` | 抖音 |
| `zhihu` | 知乎 |

---

# RSS Feed IDs Reference

| ID | Name | URL (default) |
|-----|-------|---------------|
| `hacker-news` | Hacker News | https://hnrss.org/frontpage |
| `ruanyifeng` | 阮一峰的网络日志 | http://www.ruanyifeng.com/blog/atom.xml |
| `yahoo-finance` | 雅虎财经 | https://finance.yahoo.com/news/rssindex |

---

# Error Handling

**Common Errors**:

1. **"No data available"**
   - Cause: No crawl data exists for requested date
   - Solution: Run `trigger_crawl()` or `sync_from_remote()`

2. **"Invalid date range"**
   - Cause: Date format incorrect
   - Solution: Use `resolve_date_range()` first

3. **"Keyword not found"**
   - Cause: No matches for search keyword
   - Solution: Try fuzzy mode or broader keywords

---

# Quick Reference

## Most Common Queries

```bash
# Latest news
get_latest_news()

# Today's news
get_news_by_date(date_range="today")

# Yesterday's news
get_news_by_date(date_range="yesterday")

# Hot topics (preset keywords)
get_trending_topics()

# Hot topics (auto-extract)
get_trending_topics(extract_mode="auto_extract")

# Search news
search_news(query="关键词")

# Trend analysis
analyze_topic_trend(topic="关键词")

# Sentiment analysis
analyze_sentiment(topic="关键词")

# Platform comparison
analyze_data_insights(insight_type="platform_compare", topic="关键词")

# Week-over-week comparison
compare_periods(period1="last_week", period2="this_week")

# Daily summary
generate_summary_report(report_type="daily")

# RSS latest
get_latest_rss()

# RSS search
search_rss(keyword="关键词")

# Check system status
get_system_status()

# Check version
check_version()

# Crawl data
trigger_crawl()

# Sync from remote
sync_from_remote(days=7)
```

---

# Interactive Menu

When user asks for **"menu"** or **"trendradar-tool 菜单"**:

1. Read `templates.md` in skill directory
2. Display list of available commands
3. Guide user to select an option or copy command

---

# Installation

See tool installation scripts:
- **Linux/Mac**: `install.sh`
- **Windows**: `install.ps1`

These scripts will:
1. Install Python dependencies
2. Clone TrendRadar repository
3. Set up MCP server link
4. Provide quick start commands

---

# Resources

- **TrendRadar GitHub**: https://github.com/sansan0/TrendRadar
- **MCP FAQ (中文)**: https://github.com/sansan0/TrendRadar/blob/master/README-MCP-FAQ.md
- **MCP FAQ (English)**: https://github.com/sansan0/TrendRadar/blob/master/README-MCP-FAQ-EN.md
- **Configuration**: TrendRadar `config/config.yaml`

---

**Last Updated**: 2025-01-24
