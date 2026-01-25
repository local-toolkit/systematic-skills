import requests
import json
import subprocess
import sys
import os
from typing import Optional, Dict, Any

script_dir = os.path.dirname(os.path.abspath(__file__))
SKILL_PATH = os.path.join(script_dir, "../../.agent/skills/news-aggregator-expert/SKILL.md")
TOOL_SCRIPT = os.path.join(script_dir, "main.py")
TEMPLATES_PATH = os.path.join(script_dir, "templates.md")
REPORTS_DIR = os.path.join(script_dir, "reports")

def load_skill_context() -> str:
    try:
        with open(SKILL_PATH, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read SKILL.md: {e}")
        return ""

def load_templates() -> str:
    try:
        with open(TEMPLATES_PATH, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read templates.md: {e}")
        return ""

def run_news_aggregator(**kwargs) -> str:
    """Executes the news aggregator tool with the given arguments."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(script_dir, "venv", "bin", "python")
    
    if os.path.exists(venv_python):
        python_exe = venv_python
    else:
        python_exe = sys.executable

    cmd = [python_exe, TOOL_SCRIPT]
    
    if kwargs.get('source'):
        cmd.extend(['--source', kwargs['source']])
    else:
        cmd.extend(['--source', 'all'])
    
    if kwargs.get('limit'):
        cmd.extend(['--limit', str(kwargs['limit'])])
    else:
        cmd.extend(['--limit', '10'])
        
    if kwargs.get('keyword'):
        cmd.extend(['--keyword', kwargs['keyword']])
        
    if kwargs.get('deep'):
        cmd.append('--deep')

    print(f"\n🚀 Executing: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"SUCCESS:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"ERROR (Exit Code {e.returncode}):\n{e.stderr}\n{e.stdout}"
    except Exception as e:
        return f"EXECUTION FAILED: {str(e)}"

def chat_with_local_llm(user_query: str, llm_url: Optional[str] = None):
    skill_content = load_skill_context()
    
    system_prompt = f"""You are an advanced AI assistant capable of controlling a terminal tool called 'news-aggregator-tool'.
You have access to a specific 'Skill' knowledge base which describes how to use the news aggregator effectively.

--- SKILL KNOWLEDGE BASE ---
{skill_content}
----------------------------

Your job is to interpret the user's natural language request and call the `run_news_aggregator` tool with the appropriate arguments.
Always use the tools provided to fulfill the user's request.

When the user asks for a menu or help with commands (e.g., "menu", "help", "news-aggregator-skill 如意如意"):
1. Read the templates.md file content which is provided below
2. Display the menu options to the user
3. Guide them to select a number or copy a command

--- TEMPLATES.md CONTENT ---
{load_templates()}
---------------------------
"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "run_news_aggregator",
                "description": "Fetch news from multiple sources including Hacker News, GitHub Trending, Product Hunt, 36Kr, Tencent News, WallStreetCN, V2EX, and Weibo. Use this for ALL news aggregation requests.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Source(s) to fetch from. Options: hackernews, weibo, github, 36kr, producthunt, v2ex, tencent, wallstreetcn, all (comma-separated for multiple). Default: all",
                            "default": "all"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum items per source. Default: 10",
                            "default": 10
                        },
                        "keyword": {
                            "type": "string",
                            "description": "Comma-separated keyword filters (e.g., 'AI,GPT,LLM'). You should expand simple keywords to cover the entire domain (e.g., 'AI' -> 'AI,LLM,GPT,Claude,Generative,Machine Learning,RAG,Agent')."
                        },
                        "deep": {
                            "type": "boolean",
                            "description": "Enable deep fetching to download and extract article content for detailed analysis.",
                            "default": False
                        }
                    },
                    "required": []
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    print(f"🤖 User: {user_query}")
    
    if not llm_url:
        print("⚠️  No LLM URL provided. Running in CLI mode.")
        print("💡 Set LLM_URL environment variable or pass as argument to enable AI-powered responses.")
        print("📋 Available commands:")
        print(load_templates())
        return

    print("⏳ Sending to LLM...")

    payload = {
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.0
    }

    try:
        response = requests.post(llm_url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Error connecting to LLM: {e}")
        print(f"📋 Available commands:\n{load_templates()}")
        return

    message = data['choices'][0]['message']

    if message.get('tool_calls'):
        tool_call = message['tool_calls'][0]
        function_name = tool_call['function']['name']
        arguments_str = tool_call['function']['arguments']
        
        print(f"🛠️  LLM wants to call: {function_name}({arguments_str})")

        if function_name == "run_news_aggregator":
            args = json.loads(arguments_str)
            tool_output = run_news_aggregator(**args)
            
            print(f"✅ Tool Output: {tool_output[:500]}...")

            messages.append(message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call['id'],
                "content": tool_output
            })
            
            payload["messages"] = messages
            try:
                res2 = requests.post(llm_url, json=payload, headers={"Content-Type": "application/json"})
                final_content = res2.json()['choices'][0]['message']['content']
                print(f"\n🤖 Assistant: {final_content}")
            except Exception as e:
                 print(f"❌ Error getting final response: {e}")

    else:
        print(f"🤖 Assistant: {message['content']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_client.py \"<your query>\"")
        print("       python agent_client.py \"<your query>\" --llm-url <llm_url>")
        print("")
        print("Environment variables:")
        print("  LLM_URL: URL for LLM endpoint (e.g., http://localhost:1234/v1/chat/completions)")
        print("")
        print("Examples:")
        print("  python agent_client.py \"帮我看看 Hacker News 有什么 AI 新闻\"")
        print("  python agent_client.py \"menu\"")
        print("  LLM_URL=http://localhost:1234/v1/chat/completions python agent_client.py \"全网扫描 AI 新闻\"")
        sys.exit(1)
    
    query = sys.argv[1]
    
    llm_url = None
    if '--llm-url' in sys.argv:
        idx = sys.argv.index('--llm-url')
        if idx + 1 < len(sys.argv):
            llm_url = sys.argv[idx + 1]
    else:
        llm_url = os.environ.get('LLM_URL')
    
    chat_with_local_llm(query, llm_url)
