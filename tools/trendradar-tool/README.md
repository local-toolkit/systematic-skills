# 🎯 TrendRadar Tool

**AI-driven public opinion & trend monitor** - Comprehensive Chinese news aggregation and analysis tool.

## 📦 Features

- ✅ **Multi-platform Aggregation**: Hot topics from 10+ Chinese platforms (Baidu, Weibo, Zhihu, Douyin, etc.)
- 📡 **RSS Subscriptions**: Hacker News, 36Kr, and custom RSS feeds
- 🤖 **AI Analysis**: Sentiment analysis, trend detection, topic lifecycle, and prediction
- 🔍 **Smart Search**: Keyword search, fuzzy matching, and related news discovery
- 📊 **Period Comparison**: Week-over-week, month-over-month trend analysis
- 💾 **Flexible Storage**: Local SQLite and S3-compatible cloud storage (Cloudflare R2, AWS S3, etc.)
- 🛠️ **21 MCP Tools**: Complete toolset for comprehensive news analytics

## 📂 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning TrendRadar)
- Optional: OpenAI-compatible LLM endpoint for AI-powered queries

### Quick Install

#### Linux/Mac

```bash
cd trendradar-tool
bash install.sh
```

#### Windows (PowerShell)

```powershell
cd trendradar-tool
.\install.ps1
```

The installer will:
1. Create Python virtual environment
2. Install dependencies from `requirements.txt`
3. Clone TrendRadar repository
4. Set up MCP server symlink
5. Provide quick start commands

### Manual Install

If the automated installer fails, follow these steps:

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\Activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Clone TrendRadar
git clone https://github.com/sansan0/TrendRadar.git ~/TrendRadar

# 4. Create symlink
cd trendradar-tool
ln -s ~/TrendRadar/mcp_server trendradar-mcp
```

## 🚀 Quick Start

### 1. Basic Query (No LLM)

```bash
# View latest news (today's hotlist)
python agent_client.py "查看今天的新闻"

# Get news from specific platforms
python agent_client.py --action latest_news --platforms zhihu,weibo --limit 20

# Query yesterday's news
python agent_client.py --action news_by_date --date-range yesterday

# Get trending topics (auto-extract)
python agent_client.py --action trending_topics --extract-mode auto_extract
```

### 2. AI-Powered Queries

```bash
# Set LLM URL (or use environment variable)
export LLM_URL="http://localhost:1234/v1/chat/completions"

# Query with natural language understanding
python agent_client.py "分析AI最近一周的热度趋势"

# Search with AI interpretation
python agent_client.py "搜索特斯拉相关的新闻"

# Period comparison with AI
python agent_client.py "对比本周和上周的热点变化"

# Sentiment analysis
python agent_client.py "分析人工智能新闻的情感倾向"
```

### 3. RSS Queries

```bash
# Get latest RSS articles
python agent_client.py "获取最新的RSS订阅内容"

# Search RSS for specific topic
python agent_client.py "在RSS中搜索Python相关的文章"

# Get Hacker News last 7 days
python agent_client.py --action latest_rss --feeds hacker-news --days 7 --limit 50
```

### 4. Advanced Analytics

```bash
# Deep topic analysis
python agent_client.py --action analyze_trend --topic AI --analysis-type trend

# Viral outbreak detection
python agent_client.py --action analyze_trend --topic 比特币 --analysis-type viral --spike-threshold 5.0

# Topic prediction
python agent_client.py --action analyze_trend --topic iPhone --analysis-type predict --lookahead-hours 12

# Platform comparison
python agent_client.py --action analyze_insights --insight-type platform_compare --topic 人工智能

# Keyword co-occurrence
python agent_client.py --action analyze_insights --insight-type keyword_cooccur --min-frequency 5 --top-n 15
```

### 5. Cross-Platform Analysis

```bash
# Aggregate and deduplicate news
python agent_client.py --action aggregate_news --similarity-threshold 0.8

# Week-over-week comparison
python agent_client.py --action compare_periods --period1 last_week --period2 this_week

# Month-over-month comparison
python agent_client.py --action compare_periods --period1 last_month --period2 this_month --compare-type topic_shift
```

### 6. System Management

```bash
# Check system status
python agent_client.py --action system_status

# Get configuration
python agent_client.py --action get_config

# Trigger crawl (temporary)
python agent_client.py --action trigger_crawl --platforms zhihu,weibo

# Trigger crawl (persistent)
python agent_client.py --action trigger_crawl --save-to-local

# Check version updates
python agent_client.py --action check_version

# Sync from remote storage
python agent_client.py --action sync_remote --days 7
```

### 7. Interactive Menu

```bash
# Display available commands
python agent_client.py "menu"
```

Or trigger help:
```bash
python agent_client.py "help"
python agent_client.py "?"
```

## 📋 Command Reference

### Direct Tool Actions

| Action | Description | Example |
|---------|-------------|----------|
| `latest_news` | Get latest hotlist news | `--action latest_news --platforms zhihu --limit 50` |
| `news_by_date` | Query historical news | `--action news_by_date --date-range 2025-01-01,2025-01-07` |
| `trending_topics` | Get trending topics | `--action trending_topics --extract-mode auto_extract` |
| `latest_rss` | Get latest RSS content | `--action latest_rss --days 7` |
| `search_rss` | Search RSS data | `--action search_rss --keyword AI` |
| `rss_status` | Get RSS feed status | `--action rss_status` |
| `search_news` | Search news (hotlist + optional RSS) | `--action search_news --keyword 特斯拉` |
| `find_related` | Find related news | `--action find_related --reference-title iPhone发布` |
| `analyze_trend` | Analyze topic trends | `--action analyze_trend --topic AI --analysis-type lifecycle` |
| `analyze_insights` | Data insights analysis | `--action analyze_insights --insight-type platform_compare` |
| `analyze_sentiment` | Sentiment analysis | `--action analyze_sentiment --topic AI` |
| `aggregate_news` | Cross-platform aggregation | `--action aggregate_news` |
| `compare_periods` | Period comparison | `--action compare_periods --period1 last_week --period2 this_week` |
| `generate_summary` | Generate summary report | `--action generate_summary --report-type weekly` |
| `get_config` | Get configuration | `--action get_config --section crawler` |
| `system_status` | System status check | `--action system_status` |
| `check_version` | Check version updates | `--action check_version` |
| `trigger_crawl` | Trigger crawl task | `--action trigger_crawl --save-to-local` |
| `sync_remote` | Sync from remote | `--action sync_remote --days 30` |
| `storage_status` | Storage status | `--action storage_status` |
| `list_dates` | List available dates | `--action list_dates --source both` |
| `resolve_date` | Resolve natural language dates | `--action resolve_date --expression 本周` |

### Common Parameters

| Parameter | Type | Description | Example |
|-----------|--------|-------------|----------|
| `--platforms` | string | Comma-separated platform IDs | `zhihu,weibo,baidu` |
| `--limit` | int | Max items to return (default 50) | `100` |
| `--days` | int | Number of days for queries | `7` |
| `--date-range` | string | Date range (YYYY-MM-DD,YYYY-MM-DD or natural language) | `2025-01-01,2025-01-07` or `本周` |
| `--topic` | string | Topic keyword for analysis/search | `AI` or `特斯拉` |
| `--include-url` | flag | Include URL links (default false) | `--include-url` |
| `--save-to-local` | flag | Save crawl results locally | `--save-to-local` |
| `--analysis-type` | string | Analysis type for trends | `trend`, `lifecycle`, `viral`, `predict` |
| `--insight-type` | string | Insight type for data insights | `platform_compare`, `platform_activity`, `keyword_cooccur` |

## 🎯 Use Cases

### Use Case 1: Daily News Scan

**Goal**: Get comprehensive overview of today's hot topics

```bash
# Step 1: Get latest news
python agent_client.py "查看今天的新闻，包含链接"

# Step 2: Get trending topics (auto-extract)
python agent_client.py "自动分析今天的热门话题"

# Step 3: Generate daily summary
python agent_client.py --action generate_summary --report-type daily
```

### Use Case 2: Topic Tracking

**Goal**: Track a specific topic over time

```bash
# Step 1: Resolve date range
python agent_client.py --action resolve_date --expression 本周

# Step 2: Analyze topic trend
python agent_client.py --action analyze_trend --topic AI --analysis-type trend

# Step 3: Sentiment analysis
python agent_client.py --action analyze_sentiment --topic AI

# Step 4: Find related news
python agent_client.py --action find_related --reference-title 人工智能突破
```

### Use Case 3: Cross-Platform Event Analysis

**Goal**: Analyze how an event spread across platforms

```bash
# Step 1: Search for the event
python agent_client.py --action search_news --keyword iPhone发布

# Step 2: Aggregate and deduplicate
python agent_client.py --action aggregate_news --similarity-threshold 0.8

# Step 3: Compare platform attention
python agent_client.py --action analyze_insights --insight-type platform_compare --topic iPhone
```

### Use Case 4: Periodic Trend Monitoring

**Goal**: Monitor hot topic changes between periods

```bash
# Step 1: Week-over-week comparison
python agent_client.py --action compare_periods --period1 last_week --period2 this_week

# Step 2: Analyze topic shifts
python agent_client.py --action compare_periods --period1 last_week --period2 this_week --compare-type topic_shift

# Step 3: Generate weekly summary
python agent_client.py --action generate_summary --report-type weekly
```

### Use Case 5: RSS Subscription Management

**Goal**: Keep up with RSS subscriptions

```bash
# Step 1: Get latest RSS ( Hacker News)
python agent_client.py --action latest_rss --feeds hacker-news --days 1

# Step 2: Search RSS for specific topics
python agent_client.py --action search_rss --keyword Python --feeds hacker-news --days 7

# Step 3: Check RSS feed status
python agent_client.py --action rss_status
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|----------|
| `LLM_URL` | OpenAI-compatible LLM endpoint for AI-powered queries | `http://localhost:1234/v1/chat/completions` |

### TrendRadar Configuration

TrendRadar's main configuration is in `trendradar-mcp/config/config.yaml`:

**Important Settings**:
- `platforms.sources`: Available news platforms
- `rss.feeds`: RSS subscription sources
- `ai.model`: AI model for analysis (e.g., `deepseek/deepseek-chat`)
- `ai.api_key`: API key for AI analysis
- `storage.backend`: Local or remote storage

For detailed configuration, see: https://github.com/sansan0/TrendRadar

## 💡 Best Practices

### 1. Token Optimization

- Default: 50 items, no URLs (saves ~160 tokens/item)
- Adjust only when user requests: "返回前 10 条", "需要链接", etc.

### 2. Date Handling

**RECOMMENDED**: Always use `resolve_date_range` tool first for natural language dates

```bash
# Bad: AI calculates "本周" differently
# Good: Server-side ensures consistency
python agent_client.py --action resolve_date --expression 本周
```

### 3. Data Freshness

Analysis requires fresh data. If no results:

```bash
# Check when data was last crawled
python agent_client.py --action system_status

# Crawl fresh data
python agent_client.py --action trigger_crawl --save-to-local

# Or sync from remote
python agent_client.py --action sync_remote --days 7
```

### 4. AI Display Behavior

AI models often auto-summarize. To get full data:

```bash
# Explicit request
python agent_client.py "展示所有新闻，不要总结"

# Or specify quantity
python agent_client.py "返回前 100 条新闻"
```

## 🌐 Supported Platforms

### News Platforms (Hotlist)

| Platform ID | Name |
|-------------|-------|
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

### RSS Feeds

| Feed ID | Name | Default URL |
|----------|-------|-------------|
| `hacker-news` | Hacker News | https://hnrss.org/frontpage |
| `ruanyifeng` | 阮一峰的网络日志 | http://www.ruanyifeng.com/blog/atom.xml |
| `yahoo-finance` | 雅虎财经 | https://finance.yahoo.com/news/rssindex |

## 🚦 Directory Structure

```
trendradar-tool/
├── agent_client.py          # Main entry point (CLI, MCP, LLM integration)
├── install.sh              # Installation script (Linux/Mac)
├── install.ps1            # Installation script (Windows)
├── requirements.txt         # Python dependencies
├── README.md              # This file
├── config/                # TrendRadar config (empty initially)
│   └── config.yaml
├── reports/               # Analysis reports output
└── trendradar-mcp/      # Symlink to TrendRadar MCP server
    └── server.py          # TrendRadar MCP server
```

## 📚 Resources

### Official Documentation

- **TrendRadar GitHub**: https://github.com/sansan0/TrendRadar
- **MCP FAQ (中文)**: https://github.com/sansan0/TrendRadar/blob/master/README-MCP-FAQ.md
- **MCP FAQ (English)**: https://github.com/sansan0/TrendRadar/blob/master/README-MCP-FAQ-EN.md
- **TrendRadar Config**: https://github.com/sansan0/TrendRadar/blob/master/config/config.yaml

### Tool Documentation

- **SKILL.md**: `.agent/skills/trendradar-expert/SKILL.md`
- **Templates**: `templates.md` (for interactive menu)

## 🐛 Troubleshooting

### Common Issues

**1. "No data available"**
```
Cause: No crawled data exists
Solution:
  python agent_client.py --action trigger_crawl --save-to-local
  # Or: python agent_client.py --action sync_remote --days 7
```

**2. "Python not found"**
```
Cause: Python 3.8+ not installed
Solution: Install Python 3.8+ from https://www.python.org/downloads/
```

**3. "LLM connection failed"**
```
Cause: LLM_URL not set or incorrect
Solution:
  export LLM_URL="http://your-llm-endpoint/v1/chat/completions"
  # Or pass: --llm-url http://...
```

**4. "Module import error"**
```
Cause: Dependencies not installed
Solution:
  source venv/bin/activate
  pip install -r requirements.txt
```

**5. "TrendRadar MCP server not found"**
```
Cause: TrendRadar not installed or symlink broken
Solution:
  # Re-run install script
  bash install.sh  # Linux/Mac
  .\install.ps1  # Windows
```

## 📝 Examples

### Example 1: Complete Daily Workflow

```bash
# 1. Check system status
python agent_client.py --action system_status

# 2. Crawl latest data
python agent_client.py --action trigger_crawl --save-to-local

# 3. Get latest news
python agent_client.py "查看今天的新闻，需要包含链接"

# 4. Analyze trending topics (auto-extract)
python agent_client.py --action trending_topics --extract-mode auto_extract

# 5. Generate daily summary
python agent_client.py --action generate_summary --report-type daily
```

### Example 2: AI-Powered Topic Analysis

```bash
# Set LLM endpoint
export LLM_URL="http://localhost:1234/v1/chat/completions"

# Let AI handle the entire workflow
python agent_client.py "帮我分析AI本周的热度趋势，包括情感分析"
```

### Example 3: RSS Monitoring

```bash
# 1. Get Hacker News latest
python agent_client.py --action latest_rss --feeds hacker-news --days 1 --limit 50

# 2. Search RSS for AI articles
python agent_client.py --action search_rss --keyword AI --feeds hacker-news --days 7

# 3. Check RSS feed status
python agent_client.py --action rss_status
```

### Example 4: Period Comparison

```bash
# 1. Compare this week vs last week
python agent_client.py --action compare_periods --period1 last_week --period2 this_week

# 2. Focus on AI topic
python agent_client.py --action compare_periods --period1 last_week --period2 this_week --topic AI

# 3. Analyze topic shifts
python agent_client.py --action compare_periods --period1 last_week --period2 this_week --compare-type topic_shift
```

## 🤝 Contributing

To contribute improvements or report issues:

1. Check TrendRadar's issue tracker: https://github.com/sansan0/TrendRadar/issues
2. Follow contribution guidelines in the repository

## 📄 License

This tool is a wrapper around TrendRadar, which is licensed under GPL-3.0.
See: https://github.com/sansan0/TrendRadar/blob/master/LICENSE

---

**Last Updated**: 2025-01-24
