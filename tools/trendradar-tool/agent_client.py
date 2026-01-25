#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendRadar Tool - AI-driven public opinion & trend monitor

This tool provides access to TrendRadar's MCP server with 21 powerful tools for:
- News aggregation from multiple Chinese platforms
- RSS subscription management
- AI-powered sentiment analysis
- Trend detection and prediction
- Period comparison and data insights
"""

import sys
import os
import json
import subprocess
import argparse
import requests
from typing import Optional, Dict, Any

# Directory setup
script_dir = os.path.dirname(os.path.abspath(__file__))
SKILL_PATH = os.path.join(os.path.dirname(script_dir), ".agent", "skills", "trendradar-expert", "SKILL.md")
CONFIG_DIR = os.path.join(script_dir, "config")
TEMPLATES_PATH = os.path.join(script_dir, "templates.md")
REPORTS_DIR = os.path.join(script_dir, "reports")

# Ensure directories exist
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)


def load_skill_context() -> str:
    """Load TrendRadar skill knowledge base."""
    try:
        with open(SKILL_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️  Warning: Could not read SKILL.md: {e}")
        return ""


def load_templates() -> str:
    """Load templates for interactive menu."""
    try:
        with open(TEMPLATES_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️  Warning: Could not read templates.md: {e}")
        return "No templates available"


def run_trendradar_mcp_client(action: str, **kwargs) -> str:
    """
    Execute TrendRadar MCP tools by calling TrendRadar's server.py directly.

    This function connects to the TrendRadar MCP server and executes tools.
    """
    try:
        # Check if TrendRadar MCP server is available
        trendradar_server_path = os.path.join(script_dir, "trendradar-mcp", "server.py")

        if not os.path.exists(trendradar_server_path):
            return f"""
⚠️  TrendRadar MCP server not found at: {trendradar_server_path}

Please run the installation script first:

  Linux/Mac:
    cd {script_dir}
    bash install.sh

  Windows (PowerShell):
    cd {script_dir}
    .\\install.ps1

Or manually clone TrendRadar:
  git clone https://github.com/sansan0/TrendRadar.git ~/TrendRadar
  cd {script_dir}
  ln -s ~/TrendRadar/mcp_server trendradar-mcp  # Linux/Mac
  # Or create junction for Windows

For more information, see: https://github.com/sansan0/TrendRadar
"""

        # Map actions to MCP tool names
        tool_map = {
            # Query tools
            "latest_news": "get_latest_news",
            "news_by_date": "get_news_by_date",
            "trending_topics": "get_trending_topics",

            # RSS tools
            "latest_rss": "get_latest_rss",
            "search_rss": "search_rss",
            "rss_status": "get_rss_feeds_status",

            # Search tools
            "search_news": "search_news",
            "find_related": "find_related_news",

            # Analytics tools
            "analyze_trend": "analyze_topic_trend",
            "analyze_insights": "analyze_data_insights",
            "analyze_sentiment": "analyze_sentiment",
            "aggregate_news": "aggregate_news",
            "compare_periods": "compare_periods",
            "generate_summary": "generate_summary_report",

            # System tools
            "get_config": "get_current_config",
            "system_status": "get_system_status",
            "check_version": "check_version",
            "trigger_crawl": "trigger_crawl",

            # Storage tools
            "sync_remote": "sync_from_remote",
            "storage_status": "get_storage_status",
            "list_dates": "list_available_dates",

            # Date tools
            "resolve_date": "resolve_date_range"
        }

        tool_name = tool_map.get(action, action)

        # Use mcp client to call the tool
        try:
            from mcp import Client
            from mcp.client.stdio import stdio_client

            # Connect to TrendRadar MCP server
            async def call_tool():
                async with stdio_client(
                    [sys.executable, trendradar_server_path, "--transport", "stdio"]
                ) as (read, write):
                    async with Client(read, write) as client:
                        # Initialize connection
                        await client.initialize()

                        # List available tools to verify connection
                        tools = await client.list_tools()
                        tool_names = [t.name for t in tools]

                        if tool_name not in tool_names:
                            return f"ERROR: Tool '{tool_name}' not found. Available tools: {', '.join(tool_names[:10])}..."

                        # Call the tool
                        result = await client.call_tool(tool_name, kwargs)

                        # Extract text content from result
                        if result.content:
                            text_content = []
                            for content_item in result.content:
                                if hasattr(content_item, 'text'):
                                    text_content.append(content_item.text)
                            return "\n".join(text_content) if text_content else str(result.content)

                        return str(result)

            # Run async function
            import asyncio
            return asyncio.run(call_tool())

        except ImportError:
            # Fallback: Provide instructions if mcp library not available
            return f"""
⚠️  MCP library not installed. Please install:

  pip install mcp

Then run this command again.

For manual usage, you can start TrendRadar MCP server:
  cd trendradar-mcp
  python server.py --transport stdio

For more information, see: https://github.com/sansan0/TrendRadar/blob/master/README-MCP-FAQ.md
"""
        except Exception as e:
            return f"ERROR: {str(e)}\n{type(e).__name__}"

    except Exception as e:
        return f"ERROR: {str(e)}\n{type(e).__name__}"


def chat_with_local_llm(user_query: str, llm_url: Optional[str] = None):
    """
    Chat with local LLM using TrendRadar skill knowledge base.

    Uses OpenAI-compatible API endpoint for natural language processing.
    """
    skill_content = load_skill_context()

    system_prompt = f"""You are an advanced AI assistant specialized in news aggregation and trend analysis using TrendRadar tools.

You have access to a comprehensive knowledge base about TrendRadar's MCP server, which provides 21 powerful tools for:
- News aggregation from multiple Chinese platforms (Baidu, Weibo, Zhihu, Douyin, etc.)
- RSS subscription management (Hacker News, 36Kr, etc.)
- AI-powered sentiment analysis and trend detection
- Period comparison and data insights
- Cross-platform news aggregation and deduplication

--- TRENDRADAR SKILL KNOWLEDGE BASE ---
{skill_content}
---

Your tasks:
1. Interpret user's natural language requests about news, trends, or sentiment analysis
2. Select the most appropriate TrendRadar MCP tool based on the request
3. Format tool calls with proper parameters
4. Present results in a clear, organized manner
5. Always use Chinese for explanations unless user specifically asks for English

Important Notes:
- TrendRadar MCP tools return up to 50 items by default to save tokens
- Use resolve_date_range tool for parsing "本周", "最近7天" etc.
- Most tools support date_range parameter: {{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}}
- URL links are excluded by default; ask user if they need them
- Data needs to be crawled first via trigger_crawl before analysis

Available Tool Categories:
📅 Date Resolution: resolve_date_range
📰 Query: get_latest_news, get_news_by_date, get_trending_topics
📡 RSS: get_latest_rss, search_rss, get_rss_feeds_status
🔍 Search: search_news, find_related_news
📊 Analytics: analyze_topic_trend, analyze_data_insights, analyze_sentiment, aggregate_news, compare_periods, generate_summary_report
⚙️ System: get_current_config, get_system_status, check_version, trigger_crawl
💾 Storage: sync_from_remote, get_storage_status, list_available_dates

When user asks for menu or help:
1. Read templates.md content provided below
2. Display available commands and examples
3. Guide user to select an option

--- TEMPLATES.md CONTENT ---
{load_templates()}
---
"""

    # Define tools for the LLM
    tools = [
        {
            "type": "function",
            "function": {
                "name": "run_trendradar_tool",
                "description": "Execute TrendRadar MCP tools for news aggregation, RSS queries, sentiment analysis, and trend detection. Available tools: get_latest_news, get_news_by_date, get_trending_topics, get_latest_rss, search_rss, get_rss_feeds_status, search_news, find_related_news, analyze_topic_trend, analyze_data_insights, analyze_sentiment, aggregate_news, compare_periods, generate_summary_report, get_current_config, get_system_status, check_version, trigger_crawl, sync_from_remote, get_storage_status, list_available_dates, resolve_date_range",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Tool action name. Choose from: latest_news, news_by_date, trending_topics, latest_rss, search_rss, rss_status, search_news, find_related, analyze_trend, analyze_insights, analyze_sentiment, aggregate_news, compare_periods, generate_summary, get_config, system_status, check_version, trigger_crawl, sync_remote, storage_status, list_dates, resolve_date"
                        },
                        "platforms": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Platform IDs (e.g., ['zhihu', 'weibo', 'baidu']). Only for query tools."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of items to return (default 50, max 1000)."
                        },
                        "date_range": {
                            "type": "object",
                            "description": "Date range for filtering. Format: {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}. Use resolve_date_range tool first for natural language dates.",
                            "properties": {
                                "start": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                                "end": {"type": "string", "description": "End date in YYYY-MM-DD format"}
                            }
                        },
                        "topic": {
                            "type": "string",
                            "description": "Topic keyword for analysis or search (e.g., 'AI', '特斯拉', '人工智能')."
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "Analysis type for analyze_trend: 'trend', 'lifecycle', 'viral', 'predict'. Default: 'trend'"
                        },
                        "insight_type": {
                            "type": "string",
                            "description": "Insight type for analyze_insights: 'platform_compare', 'platform_activity', 'keyword_cooccur'. Default: 'platform_compare'"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days for queries (e.g., 7 for last 7 days)."
                        },
                        "include_url": {
                            "type": "boolean",
                            "description": "Include URL links in results (default false to save tokens)."
                        },
                        "save_to_local": {
                            "type": "boolean",
                            "description": "Save crawl results to local (for trigger_crawl). Default false."
                        }
                    },
                    "required": ["action"]
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    print(f"🤖 User: {user_query}")
    print()

    # Check if LLM URL is available
    if not llm_url:
        print("⚠️  No LLM URL provided. Running in CLI mode.")
        print("💡 Set LLM_URL environment variable or pass --llm-url argument to enable AI-powered responses.")
        print()
        print("📋 Available commands:")
        print(load_templates())
        return

    print("⏳ Sending to LLM...")
    print()

    payload = {
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.0
    }

    try:
        response = requests.post(llm_url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to LLM: {e}")
        print()
        print("📋 Available commands:")
        print(load_templates())
        return

    message = data['choices'][0]['message']

    # Handle tool calls
    if message.get('tool_calls'):
        tool_call = message['tool_calls'][0]
        function_name = tool_call['function']['name']
        arguments_str = tool_call['function']['arguments']

        print(f"🛠️  LLM calling: {function_name}")
        print(f"📝 Arguments: {arguments_str}")
        print()

        if function_name == "run_trendradar_tool":
            args = json.loads(arguments_str)
            action = args.pop('action', None)

            if not action:
                print("❌ Error: No action specified")
                return

            # Execute the tool
            tool_output = run_trendradar_mcp_client(action=action, **args)

            print(f"✅ Tool Output (first 500 chars):")
            print(tool_output[:500] + "..." if len(tool_output) > 500 else tool_output)
            print()

            # Add tool result to conversation
            messages.append(message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call['id'],
                "content": tool_output[:5000]  # Limit to avoid token overflow
            })

            # Get final response
            try:
                payload["messages"] = messages
                res2 = requests.post(llm_url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
                res2.raise_for_status()
                final_content = res2.json()['choices'][0]['message']['content']
                print(f"\n🤖 Assistant:\n{final_content}")
                print()
            except Exception as e:
                print(f"❌ Error getting final response: {e}")

    elif message.get('content'):
        # Direct response without tool calls (e.g., menu display)
        print(f"🤖 Assistant:\n{message['content']}")
        print()


def save_report(content: str, filename_prefix: str = "trendradar_report"):
    """Save report to reports directory with timestamp."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.md"
    filepath = os.path.join(REPORTS_DIR, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 Report saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Failed to save report: {e}")
        return None


def main():
    """Main entry point for TrendRadar tool."""
    parser = argparse.ArgumentParser(
        description="TrendRadar Tool - AI-driven public opinion & trend monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query latest news
  python agent_client.py "查看今天的新闻"

  # Analyze trends
  python agent_client.py "分析AI最近一周的热度趋势"

  # Search with specific topic
  python agent_client.py "搜索特斯拉相关的新闻"

  # Get RSS feeds
  python agent_client.py "获取最新的RSS订阅内容"

  # Use LLM integration
  python agent_client.py "对比本周和上周的热点变化" --llm-url http://localhost:1234/v1/chat/completions

  # Show menu
  python agent_client.py "menu"

For more information, see:
  https://github.com/sansan0/TrendRadar
        """
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Query or command to execute"
    )

    parser.add_argument(
        "--llm-url",
        help="LLM endpoint URL (e.g., http://localhost:1234/v1/chat/completions). "
             "Also supports LLM_URL environment variable."
    )

    parser.add_argument(
        "--mcp-server",
        action="store_true",
        help="Start TrendRadar MCP server directly (requires TrendRadar installed)"
    )

    parser.add_argument(
        "--action",
        help="Direct tool action (bypasses LLM interpretation). "
             "See templates.md for available actions."
    )

    parser.add_argument(
        "--platforms",
        help="Comma-separated platform list (e.g., zhihu,weibo,baidu)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum items to return (default: 50)"
    )

    parser.add_argument(
        "--days",
        type=int,
        help="Number of days for queries"
    )

    parser.add_argument(
        "--date-range",
        help="Date range in format YYYY-MM-DD,YYYY-MM-DD"
    )

    parser.add_argument(
        "--topic",
        help="Topic keyword for analysis or search"
    )

    parser.add_argument(
        "--include-url",
        action="store_true",
        help="Include URL links in results"
    )

    args = parser.parse_args()

    # Get LLM URL from argument or environment
    llm_url = args.llm_url or os.environ.get('LLM_URL')

    # Handle MCP server mode
    if args.mcp_server:
        print("🚀 Starting TrendRadar MCP Server...")
        print("⚠️  This requires TrendRadar to be installed separately.")
        print("See: https://github.com/sansan0/TrendRadar")
        print()
        print("Installation:")
        print("  git clone https://github.com/sansan0/TrendRadar.git")
        print("  cd TrendRadar/mcp_server")
        print("  python server.py --transport stdio")
        return

    # Handle direct action mode
    if args.action:
        kwargs = {}

        if args.platforms:
            kwargs['platforms'] = [p.strip() for p in args.platforms.split(',')]

        if args.limit != 50:
            kwargs['limit'] = args.limit

        if args.days:
            kwargs['days'] = args.days

        if args.date_range:
            try:
                start, end = args.date_range.split(',')
                kwargs['date_range'] = {'start': start.strip(), 'end': end.strip()}
            except Exception as e:
                print(f"❌ Invalid date range format: {e}")
                print("Expected: YYYY-MM-DD,YYYY-MM-DD")
                sys.exit(1)

        if args.topic:
            kwargs['topic'] = args.topic

        if args.include_url:
            kwargs['include_url'] = True

        result = run_trendradar_mcp_client(action=args.action, **kwargs)
        print(result)
        return

    # Handle interactive/chat mode
    if not args.query:
        print("💡 TrendRadar Tool - News Aggregation & Trend Analysis")
        print()
        print("Usage:")
        print("  python agent_client.py \"<query>\"              # Query with LLM")
        print("  python agent_client.py \"menu\"                 # Show available commands")
        print("  python agent_client.py --action <action>        # Direct tool execution")
        print()
        print("Examples:")
        print('  python agent_client.py "查看今天的新闻"')
        print('  python agent_client.py "分析AI的热度趋势"')
        print('  LLM_URL=http://localhost:1234/v1/chat/completions python agent_client.py "搜索特斯拉新闻"')
        sys.exit(1)

    # Check for menu request
    if args.query.lower() in ['menu', 'help', '菜单', '?']:
        print("📋 TrendRadar Tool - Available Commands")
        print()
        print(load_templates())
        return

    # Interactive chat mode
    chat_with_local_llm(args.query, llm_url=llm_url)


if __name__ == "__main__":
    main()
