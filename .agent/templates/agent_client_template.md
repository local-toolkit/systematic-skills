# Agent Client Template

This is a standardized template for creating `agent_client.py` files.
It automatically adapts to different tool types: subprocess, MCP server, or meta.

## How to Use

1. Copy this file to `{your-tool}/agent_client.py`
2. Replace `{{TOOL_NAME}}`, `{{SKILL_NAME}}`, `{{INTEGRATION_TYPE}}`
3. Adjust tool definitions based on your tool's capabilities
4. Test with `python agent_client.py "test query"`

## Supported Integration Types

### Type 1: Subprocess (Simple Tools)

**Best for:** Simple CLI tools with `main.py` that don't need MCP

**Examples:** yt-dlp-tool, news-aggregator-tool, imgconv-tool

**Configuration:**

```python
INTEGRATION_TYPE = "subprocess"
TOOL_SCRIPT = "main.py"
```

**Pattern:**

```python
def run_tool(**kwargs):
    cmd = [python_exe, TOOL_SCRIPT]
    # Convert kwargs to CLI arguments
    result = subprocess.run(cmd, ...)
    return result
```

---

### Type 2: MCP Server (Advanced Integration)

**Best for:** Tools that need deep AI integration via MCP protocol

**Examples:** playwright-tool

**Configuration:**

```python
INTEGRATION_TYPE = "mcp"
MCP_SERVER_SCRIPT = "mcp_server.py"
IS_EXTERNAL_MCP = True/False  # True for external servers like TrendRadar
```

**Pattern:**

```python
from mcp_client import create_mcp_client

client = create_mcp_client(
    server_path=MCP_SERVER_SCRIPT,
    server_name="{{TOOL_NAME}}-mcp",
    is_external=IS_EXTERNAL_MCP
)

async def run_tool(action: str, **kwargs):
    result = await client.call_tool(action, **kwargs)
    return result
```

---

### Type 3: Meta Skills (No Execution)

**Best for:** Skills that provide guidance only

**Examples:** literature-search-expert, mcp-builder-expert, tool-development-expert

**Configuration:**

```python
INTEGRATION_TYPE = "meta"
HAS_MAIN = False
```

**Pattern:**

```python
def main():
    # Display SKILL.md content
    print(load_skill_context())
```

---

## Template Code

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{{TOOL_NAME}} Tool Agent Client
{{TOOL_DESCRIPTION}}
"""

import sys
import os
import json
import subprocess
from typing import Optional, Dict, Any

# ====== CONFIGURATION ======

script_dir = os.path.dirname(os.path.abspath(__file__))
SKILL_PATH = os.path.join(
    os.path.dirname(script_dir),
    ".agent",
    "skills",
    "{{SKILL_NAME}}",
    "SKILL.md"
)

# Integration type: subprocess | mcp | meta
INTEGRATION_TYPE = "{{INTEGRATION_TYPE}}"

# Subprocess configuration
TOOL_SCRIPT = os.path.join(script_dir, "main.py")

# MCP configuration
MCP_SERVER_SCRIPT = os.path.join(script_dir, "{{MCP_SERVER_PATH}}")
IS_EXTERNAL_MCP = {{IS_EXTERNAL_MCP}}

# Templates configuration
TEMPLATES_PATH = os.path.join(script_dir, "templates.md")
REPORTS_DIR = os.path.join(script_dir, "reports")

# Ensure directories exist
if os.path.basename(script_dir) in ["{{TOOL_NAME}}-tool"]:
    os.makedirs(REPORTS_DIR, exist_ok=True)

# ====== UTILITY FUNCTIONS ======

def load_skill_context() -> str:
    """Load skill knowledge base."""
    try:
        with open(SKILL_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read SKILL.md: {e}")
        return ""

def load_templates() -> str:
    """Load command templates if available."""
    try:
        with open(TEMPLATES_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return ""  # Templates are optional

# ====== TOOL EXECUTION (SUBPROCESS MODE) ======

{{SUBPROCESS_IMPLEMENTATION}}

# ====== TOOL EXECUTION (MCP MODE) ======

{{MCP_IMPLEMENTATION}}

# ====== LLM INTEGRATION ======

def chat_with_local_llm(user_query: str, llm_url: Optional[str] = None):
    """
    Chat with local LLM using tool capabilities.
    """
    skill_content = load_skill_context()

    system_prompt = f"""You are an advanced AI assistant specialized in {{TOOL_NAME}}.
You have access to a comprehensive knowledge base about this tool.

--- {TOOL_NAME} SKILL KNOWLEDGE BASE ---
{skill_content}
---

Your job:
1. Interpret user's natural language requests about {{TOOL_NAME}}
2. Select the appropriate tool/action based on the request
3. Format tool calls with proper parameters
4. Present results in a clear, organized manner
5. Always use Chinese for explanations unless user asks for English

Available Tools:
{{TOOL_DEFINITIONS}}

When user asks for "menu", "help", "templates" or "菜单":
1. Load templates.md content provided below
2. Display available commands and examples
3. Guide user to select an option or copy a command

--- TEMPLATES.md CONTENT ---
{load_templates()}
---
"""

{{LLM_TOOLS}}

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    print(f"🤖 User: {user_query}")
    print()

    # Check if LLM URL is available
    if not llm_url:
        print("⚠️  No LLM URL provided. Running in CLI mode.")
        print("💡 Set LLM_URL environment variable or pass --llm-url argument.")
        print()
        print("📋 Available commands:")
        print(load_templates())
        return

    print("⏳ Sending to LLM...")
    print()

    try:
        import requests
        payload = {
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": 0.0
        }

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

        # Execute tool
        try:
            args = json.loads(arguments_str)

            if function_name in ["{{TOOL_FUNCTION_NAMES}}"]:
                tool_output = {{TOOL_EXECUTION_CALL}}(args)

                print(f"✅ Tool Output (first 500 chars):")
                output_preview = tool_output[:500] + "..." if len(tool_output) > 500 else tool_output
                print(output_preview)
                print()

                # Add tool result to conversation
                messages.append(message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call['id'],
                    "content": tool_output[:5000]  # Limit to avoid token overflow
                })

                # Get final response
                payload["messages"] = messages
                res2 = requests.post(llm_url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
                final_content = res2.json()['choices'][0]['message']['content']
                print(f"\n🤖 Assistant:\n{final_content}")
                print()

        except Exception as e:
            print(f"❌ Error executing tool: {e}")

    elif message.get('content'):
        # Direct response without tool calls (e.g., menu display)
        print(f"🤖 Assistant:\n{message['content']}")
        print()

# ====== MAIN ENTRY POINT ======

def main():
    """Main entry point for {{TOOL_NAME}} tool."""
    import argparse

    parser = argparse.ArgumentParser(
        description="{{TOOL_NAME}} Tool - {{TOOL_DESCRIPTION}}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent_client.py "查询示例"
  python agent_client.py "menu"
  python agent_client.py --action {{DEFAULT_ACTION}} --param1 value1

For more information, see:
  SKILL.md: {SKILL_PATH}
  Templates: {TEMPLATES_PATH}
        """
    )

    parser.add_argument("query", nargs="?", help="Query or command to execute")
    parser.add_argument("--llm-url", help="LLM endpoint URL")
    parser.add_argument("--action", help="Direct tool action (bypasses LLM)")
    {{ARGUMENT_DEFINITIONS}}

    args = parser.parse_args()

    # Get LLM URL from argument or environment
    llm_url = args.llm_url or os.environ.get('LLM_URL')

    # Handle direct action mode
    if args.action:
        {{DIRECT_ACTION_HANDLER}}
        return

    # Handle interactive/chat mode
    if not args.query:
        print("💡 {{TOOL_NAME}} Tool")
        print()
        print("Usage:")
        print(f"  python agent_client.py \"<query>\"")
        print(f"  python agent_client.py \"menu\"")
        print(f"  python agent_client.py --action <action>")
        print()
        print("Environment variable:")
        print("  LLM_URL: URL for LLM endpoint")
        print()
        sys.exit(1)

    # Check for menu request
    if args.query.lower() in ['menu', 'help', '菜单', '?']:
        print("📋 {{TOOL_NAME}} Tool - Available Commands")
        print()
        print(load_templates())
        return

    # Interactive chat mode
    chat_with_local_llm(args.query, llm_url=llm_url)


if __name__ == "__main__":
    main()
```

---

## Fill-in Guide

### For Subprocess Tools

Replace these placeholders:

1. `{{TOOL_NAME}}` - Tool name (e.g., "yt-dlp", "imgconv")
2. `{{SKILL_NAME}}` - Skill name (e.g., "yt-dlp-expert")
3. `{{TOOL_DESCRIPTION}}` - One-line description
4. `{{INTEGRATION_TYPE}}` - Set to "subprocess"
5. `{{MCP_SERVER_PATH}}` - Not needed for subprocess tools
6. `{{IS_EXTERNAL_MCP}}` - Set to False

Implement:

- `{{SUBPROCESS_IMPLEMENTATION}}` - Add your run_tool function
- `{{LLM_TOOLS}}` - Define LLM tool schemas
- `{{TOOL_FUNCTION_NAMES}}` - List tool function names
- `{{TOOL_EXECUTION_CALL}}` - Tool execution call
- `{{ARGUMENT_DEFINITIONS}}` - Add argparse arguments
- `{{DIRECT_ACTION_HANDLER}}` - Add direct action handler

### For MCP Tools

Replace these placeholders:

1. `{{TOOL_NAME}}` - Tool name (e.g., "playwright")
2. `{{SKILL_NAME}}` - Skill name (e.g., "playwright-expert")
3. `{{TOOL_DESCRIPTION}}` - One-line description
4. `{{INTEGRATION_TYPE}}` - Set to "mcp"
5. `{{MCP_SERVER_PATH}}` - Set to "mcp_server.py"
6. `{{IS_EXTERNAL_MCP}}` - True for external MCP (like TrendRadar), False for local

Implement:

- `{{MCP_IMPLEMENTATION}}` - Add MCP client integration
- `{{LLM_TOOLS}}` - Define LLM tool schemas
- `{{TOOL_FUNCTION_NAMES}}` - List tool names from MCP server
- `{{TOOL_EXECUTION_CALL}}` - Tool execution via MCP client
- `{{ARGUMENT_DEFINITIONS}}` - Add argparse arguments
- `{{DIRECT_ACTION_HANDLER}}` - Add direct action handler

### For Meta Skills

Replace these placeholders:

1. `{{TOOL_NAME}}` - Skill name (e.g., "literature-search")
2. `{{SKILL_NAME}}` - Skill name (e.g., "literature-search-expert")
3. `{{TOOL_DESCRIPTION}}` - One-line description
4. `{{INTEGRATION_TYPE}}` - Set to "meta"

Simplify:

- Remove tool execution code
- Remove LLM tools definitions
- Only implement SKILL.md display logic

---

## Best Practices

### 1. Error Handling

Always include try-except blocks for all external operations:

```python
try:
    result = subprocess.run(cmd, ...)
    return f"SUCCESS:\n{result.stdout}"
except subprocess.CalledProcessError as e:
    return f"ERROR (Exit Code {e.returncode}):\n{e.stderr}"
except Exception as e:
    return f"EXECUTION FAILED: {str(e)}"
```

### 2. Path Handling

Use `os.path.dirname(os.path.abspath(__file__))` for relative paths:

```python
script_dir = os.path.dirname(os.path.abspath(__file__))
SKILL_PATH = os.path.join(script_dir, "..", ".agent", "skills", ...)
```

### 3. Python Version Compatibility

Support both Python 2 and Python 3 naming:

```python
PYTHON_CMD = "python3"
if not os.path.exists(sys.executable):
    PYTHON_CMD = "python"
```

### 4. Tool Discovery

Check for files before trying to use them:

```python
if os.path.exists(MCP_SERVER_SCRIPT):
    # Use MCP mode
else:
    # Fallback to subprocess or show error
```

---

## Testing Your Implementation

After creating agent_client.py, test it:

```bash
# Test menu display
python agent_client.py "menu"

# Test LLM integration (if applicable)
LLM_URL=http://localhost:1234/v1/chat/completions python agent_client.py "测试查询"

# Test direct action (if applicable)
python agent_client.py --action list_tools
```

---

## Common Issues

### Issue 1: Import errors for mcp_client

**Problem:** `ModuleNotFoundError: No module named 'mcp_client'`

**Solution:** Ensure mcp_client.py is in the parent directory:

```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### Issue 2: MCP server not found

**Problem:** `MCP server not found at: ...`

**Solution:** Run installation script or create symlink:

```bash
bash install.sh  # For subprocess tools
# No symlink needed for local tools
```

### Issue 3: LLM connection fails

**Problem:** `Error connecting to LLM: ...`

**Solution:** Check LLM_URL is set and endpoint is available:

```bash
echo $LLM_URL
curl $LLM_URL  # Test endpoint
```

---

## Migration from Old Pattern

If you're converting an existing agent_client.py:

**Old pattern (deprecated):**

```python
# ❌ Don't use this pattern
from agent import call_mcp_tool  # This function doesn't exist!
```

**New pattern (correct):**

```python
# ✅ Use this pattern
from mcp_client import create_mcp_client

client = create_mcp_client(
    server_path=MCP_SERVER_SCRIPT,
    server_name="my-tool-mcp",
    is_external=False
)
```

---

## Additional Resources

- **MCP Protocol**: https://modelcontextprotocol.io
- **Unified Agent**: See `agent.py` for routing logic
- **Skill Registry**: See `.agent/skill_registry.json`
- **Code Style**: See `AGENTS.md` for conventions

---

**Last Updated**: 2025-01-25
