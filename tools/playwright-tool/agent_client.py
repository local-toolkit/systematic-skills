#!/usr/bin/env python3
"""
Playwright Tool Agent Client
Entry point for Playwright MCP server with LLM integration support.
"""

import requests
import json
import subprocess
import sys
import os

SKILL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.agent/skills/playwright-expert/SKILL.md")
MCP_SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")
TEMPLATES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates.md")

def load_skill_context() -> str:
    """Load skill knowledge base."""
    try:
        with open(SKILL_PATH, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read SKILL.md: {e}")
        return ""

def load_templates() -> str:
    """Load command templates."""
    try:
        with open(TEMPLATES_PATH, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read templates.md: {e}")
        return ""

def run_mcp_server(**kwargs) -> str:
    """Run MCP server with given arguments."""
    script_dir = os.path.dirname(os.path.abspath(MCP_SERVER_SCRIPT))
    
    # Attempt to find venv python first
    venv_python = os.path.join(script_dir, "venv", "bin", "python")
    
    if os.path.exists(venv_python):
        python_exe = venv_python
    else:
        python_exe = sys.executable
    
    cmd = [python_exe, MCP_SERVER_SCRIPT]
    
    print(f"\n🚀 Executing: {' '.join(cmd)}")
    try:
        # Run the MCP server
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"SUCCESS:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"ERROR (Exit Code {e.returncode}):\n{e.stderr}\n{e.stdout}"
    except Exception as e:
        return f"EXECUTION FAILED: {str(e)}"

def chat_with_local_llm(user_query: str, llm_url: str = None):
    """Chat with local LLM using tool calling."""
    skill_content = load_skill_context()
    
    system_prompt = f"""You are an advanced AI assistant capable of controlling a Playwright browser automation tool through MCP (Model Context Protocol).
You have access to a specific 'Skill' knowledge base which describes how to use Playwright effectively.

--- SKILL KNOWLEDGE BASE ---
{skill_content}
----------------------------

Your job is to interpret the user's natural language request and call the appropriate MCP tools.
Always use the tools provided to fulfill the user's request.

When the user asks for "menu", "help", "templates", or "examples":
1. Load the templates from templates.md and display available commands
2. Guide them to select a number or copy the command template

Common tasks you should handle:
- Web page navigation and information extraction
- Taking screenshots
- Form filling and submission
- Clicking on elements
- Text extraction
- Running JavaScript code
- Web scraping and data extraction
- Waiting for elements
"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "run_mcp_server",
                "description": "Run the Playwright MCP server. Use this for ALL browser automation requests.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "browser_type": {
                            "type": "string",
                            "description": "Browser type to launch (chromium, firefox, webkit). Default: chromium",
                            "enum": ["chromium", "firefox", "webkit"],
                            "default": "chromium"
                        },
                        "headless": {
                            "type": "boolean",
                            "description": "Run in headless mode. Default: true",
                            "default": True
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds. Default: 30000",
                            "default": 30000
                        },
                        "url": {
                            "type": "string",
                            "description": "Initial URL to navigate to"
                        },
                        "wait_until": {
                            "type": "string",
                            "description": "Wait condition (load, networkidle, domcontentloaded, commit). Default: load",
                            "enum": ["load", "networkidle", "domcontentloaded", "commit"],
                            "default": "load"
                        },
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for page operations"
                        },
                        "value": {
                            "type": "string",
                            "description": "Value to fill or text to type"
                        },
                        "text": {
                            "type": "string",
                            "description": "Text to type into an element"
                        },
                        "delay": {
                            "type": "integer",
                            "description": "Delay between keystrokes in ms. Default: 50"
                        },
                        "script": {
                            "type": "string",
                            "description": "JavaScript code to execute"
                        },
                        "schema": {
                            "type": "string",
                            "description": "JSON schema for structured data extraction"
                        },
                        "full_page": {
                            "type": "boolean",
                            "description": "Capture full page screenshot. Default: false"
                        },
                        "path": {
                            "type": "string",
                            "description": "Path to save screenshot"
                        },
                        "state": {
                            "type": "string",
                            "description": "Element state (attached, visible, hidden). Default: visible"
                        },
                        "code": {
                            "type": "string",
                            "description": "JavaScript code to execute"
                        },
                        "width": {
                            "type": "integer",
                            "description": "Viewport width in pixels. Default: 1280"
                        },
                        "height": {
                            "type": "integer",
                            "description": "Viewport height in pixels. Default: 720"
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
        print("💡 Set LLM_URL environment variable or pass --llm-url to enable AI-powered responses.")
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
        response = requests.post(llm_url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        message = data['choices'][0]['message']
        
        print(f"🛠️  LLM wants to call: {message.get('content', 'No tool call')}")
        
        # Handle tool calls
        if message.get('tool_calls'):
            for tool_call in message['tool_calls']:
                tool_name = tool_call['function']['name']
                arguments_str = json.dumps(tool_call['function']['arguments'], indent=2)
                print(f"🔧 Executing: {tool_name}({arguments_str})")
                
                # Execute the corresponding function
                if tool_name == "run_mcp_server":
                    args = tool_call['function']['arguments']
                    result = run_mcp_server(**args)
                else:
                    result = f"ERROR: Unknown tool {tool_name}"
                
                # Send result back to LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call['id'],
                    "content": result
                })
            
            # Final response
            messages.append({
                "role": "assistant",
                "content": message.get('content', 'No additional response')
            })
            
            # Get final response
            final_payload = {"messages": messages}
            final_response = requests.post(llm_url, json=final_payload, headers={"Content-Type": "application/json"}, timeout=60)
            final_data = final_response.json()
            final_message = final_data['choices'][0]['message']['content']
            
            print(f"\n🤖 Assistant: {final_message}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to LLM: {e}")
        print(f"📋 Available commands:\n{load_templates()}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_client.py \"<query>\"")
        print("       python agent_client.py \"<query>\" --llm-url <url>")
        print("")
        print("Environment variables:")
        print("  LLM_URL: URL for LLM endpoint (e.g., http://localhost:1234/v1/chat/completions)")
        print("")
        print("Examples:")
        print("  python agent_client.py \"打开 github.com 并截图\"")
        print("  python agent_client.py \"帮我填写这个表单\"")
        print("  python agent_client.py \"获取页面所有链接\"")
        print("")
        print("Available templates (run with 'menu' or 'help'):")
        print(load_templates())
        sys.exit(1)
    
    query = sys.argv[1]
    llm_url = None
    
    # Parse command line arguments
    for i in range(2, len(sys.argv)):
        arg = sys.argv[i]
        if arg == '--llm-url' and i + 1 < len(sys.argv):
            llm_url = sys.argv[i + 1]
    
    chat_with_local_llm(query, llm_url)
