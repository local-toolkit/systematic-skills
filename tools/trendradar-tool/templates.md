# TrendRadar Tool - 交互命令模板

## 📋 基础查询 (Basic Queries)

### 1. 查看最新新闻
```bash
# 获取今天的最新新闻（默认50条）
python agent_client.py "查看今天的新闻"

# 包含URL链接
python agent_client.py "查看今天的新闻，需要链接"

# 限制条数
python agent_client.py --action latest_news --limit 20

# 指定平台
python agent_client.py --action latest_news --platforms zhihu,weibo --limit 30
```

### 2. 查询指定日期的新闻
```bash
# 查询昨天的新闻
python agent_client.py --action news_by_date --date-range yesterday

# 查询最近7天的新闻
python agent_client.py --action news_by_date --date-range 最近7天

# 查询特定日期范围
python agent_client.py --action news_by_date --date-range 2025-01-01,2025-01-07

# 自然语言日期（需要先调用resolve_date）
python agent_client.py --action resolve_date --expression 本周
```

### 3. 获取热点话题统计
```bash
# 使用预设关键词统计
python agent_client.py --action trending_topics

# 自动提取热门话题（推荐）
python agent_client.py --action trending_topics --extract-mode auto_extract --top-n 20

# 指定模式
python agent_client.py --action trending_topics --mode daily --top-n 15
```

## 📡 RSS 订阅 (RSS Subscriptions)

### 4. 获取最新RSS内容
```bash
# 获取今天的RSS（默认1天）
python agent_client.py "获取最新的RSS订阅内容"

# 获取最近7天的Hacker News
python agent_client.py --action latest_rss --feeds hacker-news --days 7 --limit 50

# 获取多个RSS源
python agent_client.py --action latest_rss --feeds hacker-news,36kr --days 3 --include-summary

# 不限制天数（最多30天）
python agent_client.py --action latest_rss --days 30
```

### 5. 搜索RSS内容
```bash
# 搜索AI相关文章
python agent_client.py --action search_rss --keyword AI

# 搜索最近14天的Python文章
python agent_client.py --action search_rss --keyword Python --days 14

# 指定RSS源搜索
python agent_client.py --action search_rss --keyword 机器学习 --feeds hacker-news --days 7
```

### 6. 查看RSS源状态
```bash
# 查看所有RSS源状态
python agent_client.py --action rss_status
```

## 🔍 智能检索 (Smart Search)

### 7. 搜索新闻
```bash
# 基础关键词搜索
python agent_client.py --action search_news --keyword 特斯拉

# 模糊搜索
python agent_client.py --action search_news --keyword 人工智能突破 --search-mode fuzzy --threshold 0.6

# 指定日期范围搜索
python agent_client.py --action search_news --keyword iPhone --date-range 2025-01-01,2025-01-07

# 同时搜索热榜和RSS
python agent_client.py --action search_news --keyword GPT-5 --include-rss --rss-limit 20

# 包含URL链接
python agent_client.py --action search_news --keyword AI --include-url
```

### 8. 查找相关新闻
```bash
# 查找今天的相似新闻
python agent_client.py --action find_related --reference-title 特斯拉降价

# 查找上周的相关新闻
python agent_client.py --action find_related --reference-title 人工智能突破 --date-range last_week

# 调整相似度阈值（更严格）
python agent_client.py --action find_related --reference-title ChatGPT --threshold 0.7
```

## 📊 数据分析 (Data Analytics)

### 9. 话题趋势分析
```bash
# 热度趋势分析
python agent_client.py --action analyze_trend --topic AI --analysis-type trend

# 生命周期分析
python agent_client.py --action analyze_trend --topic 比特币 --analysis-type lifecycle

# 病毒式爆发检测
python agent_client.py --action analyze_trend --topic 比特币 --analysis-type viral --spike-threshold 5.0

# 话题预测
python agent_client.py --action analyze_trend --topic iPhone --analysis-type predict --lookahead-hours 12
```

### 10. 数据洞察分析
```bash
# 平台对比分析
python agent_client.py --action analyze_insights --insight-type platform_compare --topic 人工智能

# 平台活跃度统计
python agent_client.py --action analyze_insights --insight-type platform_activity --date-range 2025-01-01,2025-01-07

# 关键词共现分析
python agent_client.py --action analyze_insights --insight-type keyword_cooccur --min-frequency 5 --top-n 15
```

### 11. 情感倾向分析
```bash
# 整体情感分析（今天）
python agent_client.py --action analyze_sentiment --limit 50

# 特定话题情感分析
python agent_client.py --action analyze_sentiment --topic AI

# 指定时间范围
python agent_client.py --action analyze_sentiment --topic 特斯拉 --date-range 2025-01-01,2025-01-07

# 不按权重排序
python agent_client.py --action analyze_sentiment --sort-by-weight false
```

### 12. 跨平台新闻聚合
```bash
# 聚合今天的新闻
python agent_client.py --action aggregate_news

# 更严格的相似度阈值
python agent_client.py --action aggregate_news --similarity-threshold 0.8

# 聚合特定时间范围
python agent_client.py --action aggregate_news --date-range 2025-01-01,2025-01-07

# 包含URL链接
python agent_client.py --action aggregate_news --include-url
```

### 13. 时期对比分析
```bash
# 周环比（本周vs上周）
python agent_client.py --action compare_periods --period1 last_week --period2 this_week

# 月环比（本月vs上月）
python agent_client.py --action compare_periods --period1 last_month --period2 this_month

# 话题变化分析
python agent_client.py --action compare_periods --period1 last_week --period2 this_week --compare-type topic_shift

# 自定义日期范围对比
python agent_client.py --action compare_periods \
    --period1 2025-01-01,2025-01-07 \
    --period2 2025-01-08,2025-01-14
```

### 14. 生成摘要报告
```bash
# 生成每日摘要
python agent_client.py --action generate_summary --report-type daily

# 生成每周摘要
python agent_client.py --action generate_summary --report-type weekly

# 自定义时间范围摘要
python agent_client.py --action generate_summary \
    --report-type weekly \
    --date-range 2025-01-01,2025-01-07
```

## ⚙️ 系统管理 (System Management)

### 15. 系统状态检查
```bash
# 查看系统运行状态
python agent_client.py --action system_status
```

### 16. 获取系统配置
```bash
# 获取所有配置
python agent_client.py --action get_config

# 获取爬虫配置
python agent_client.py --action get_config --section crawler

# 获取权重配置
python agent_client.py --action get_config --section weights
```

### 17. 检查版本更新
```bash
# 检查TrendRadar和MCP Server版本
python agent_client.py --action check_version

# 使用代理检查
python agent_client.py --action check_version --proxy-url http://127.0.0.1:7890
```

### 18. 触发爬取任务
```bash
# 临时爬取（不保存）
python agent_client.py --action trigger_crawl --platforms zhihu,weibo

# 持久化爬取（保存数据）
python agent_client.py --action trigger_crawl --save-to-local

# 包含URL链接
python agent_client.py --action trigger_crawl --include-url
```

## 💾 存储同步 (Storage Sync)

### 19. 从远程同步数据
```bash
# 同步最近7天的数据
python agent_client.py --action sync_remote --days 7

# 同步最近30天的数据
python agent_client.py --action sync_remote --days 30

# 不拉取数据（仅检查）
python agent_client.py --action sync_remote --days 0
```

### 20. 查看存储状态
```bash
# 查看存储配置和状态
python agent_client.py --action storage_status
```

### 21. 列出可用日期
```bash
# 对比本地和远程日期
python agent_client.py --action list_dates

# 仅查看本地日期
python agent_client.py --action list_dates --source local

# 仅查看远程日期
python agent_client.py --action list_dates --source remote
```

## 📅 日期解析 (Date Resolution)

### 22. 解析自然语言日期
```bash
# 解析"本周"
python agent_client.py --action resolve_date --expression 本周

# 解析"最近7天"
python agent_client.py --action resolve_date --expression 最近7天

# 解析"本月"
python agent_client.py --action resolve_date --expression 本月

# 解析"上月"
python agent_client.py --action resolve_date --expression 上月
```

## 🤖 AI 智能查询 (AI-Powered Queries)

以下命令需要设置 LLM_URL 环境变量：

```bash
# 设置LLM端点
export LLM_URL="http://localhost:1234/v1/chat/completions"

# 或在命令中指定
python agent_client.py "查询" --llm-url http://localhost:1234/v1/chat/completions
```

### AI 常用查询示例

```bash
# 完整工作流：分析AI本周趋势
python agent_client.py "帮我分析AI本周的热度趋势"

# 深度分析：情感+趋势
python agent_client.py "分析特斯拉新闻的情感倾向和热度趋势"

# 事件追踪：跨平台分析
python agent_client.py "追踪iPhone发布事件在各平台的表现"

# 对比分析：周环比
python agent_client.py "对比本周和上周的热点变化，找出上升和下降的话题"

# 智能搜索：模糊匹配
python agent_client.py "模糊搜索人工智能突破相关的新闻"

# RSS监控：最新+搜索
python agent_client.py "获取Hacker News最新内容，然后搜索Python相关文章"

# 生成报告：每日汇总
python agent_client.py "生成今天的新闻摘要报告"

# 预测分析：下周热点预测
python agent_client.py "预测下周可能出现的热点话题"
```

## 📊 完整工作流示例 (Complete Workflow Examples)

### 工作流1：每日热点扫描
```bash
# 步骤1：获取最新新闻
python agent_client.py --action latest_news --include-url

# 步骤2：获取自动提取的热门话题
python agent_client.py --action trending_topics --extract-mode auto_extract --top-n 20

# 步骤3：生成每日摘要
python agent_client.py --action generate_summary --report-type daily
```

### 工作流2：话题深度分析
```bash
# 步骤1：解析日期
python agent_client.py --action resolve_date --expression 本周

# 步骤2：分析话题趋势
python agent_client.py --action analyze_trend --topic AI --analysis-type lifecycle

# 步骤3：情感分析
python agent_client.py --action analyze_sentiment --topic AI

# 步骤4：查找相关新闻
python agent_client.py --action find_related --reference-title 人工智能突破
```

### 工作流3：跨平台事件追踪
```bash
# 步骤1：搜索事件
python agent_client.py --action search_news --keyword iPhone发布

# 步骤2：聚合去重
python agent_client.py --action aggregate_news --similarity-threshold 0.8

# 步骤3：平台对比
python agent_client.py --action analyze_insights --insight-type platform_compare --topic iPhone
```

### 工作流4：周期性趋势监控
```bash
# 步骤1：对比两个时期
python agent_client.py --action compare_periods --period1 last_week --period2 this_week

# 步骤2：分析话题变化
python agent_client.py --action compare_periods --period1 last_week --period2 this_week --compare-type topic_shift

# 步骤3：生成每周摘要
python agent_client.py --action generate_summary --report-type weekly
```

## 💡 快捷提示

### 常用参数组合

```bash
# 热门平台
--platforms zhihu,weibo,baidu

# 限制条数
--limit 20
--limit 100

# 时间范围
--date-range 2025-01-01,2025-01-07
--date-range 本周
--date-range 最近7天

# 包含链接
--include-url

# 保存数据
--save-to-local
```

## 🎯 推荐查询模式

### 初级用户 (Beginner)
```bash
# 查看最新新闻
python agent_client.py "最新新闻"

# 获取热门话题
python agent_client.py --action trending_topics

# 查看系统状态
python agent_client.py --action system_status
```

### 中级用户 (Intermediate)
```bash
# 搜索特定话题
python agent_client.py --action search_news --keyword 特斯拉

# 分析话题趋势
python agent_client.py --action analyze_trend --topic AI

# 对比两个时期
python agent_client.py --action compare_periods --period1 last_week --period2 this_week
```

### 高级用户 (Advanced)
```bash
# 完整工作流（AI驱动）
export LLM_URL="http://localhost:1234/v1/chat/completions"
python agent_client.py "帮我完成AI话题的完整分析：趋势、情感、相关新闻和预测"

# RSS监控
python agent_client.py --action latest_rss --days 7 --include-summary
python agent_client.py --action search_rss --keyword AI --days 14

# 数据同步
python agent_client.py --action sync_remote --days 30
python agent_client.py --action storage_status
```

---

**提示**：
1. 使用自然语言查询时，建议先调用 `resolve_date` 解析日期
2. 默认设置是为了节省token，可以指定 `--include-url` 获取链接
3. 数据需要先爬取，如果没有数据请先运行 `trigger_crawl`
4. 更多信息请查看 `.agent/skills/trendradar-expert/SKILL.md`
