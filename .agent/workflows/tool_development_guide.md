#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Development Guide

Standardized guide for creating new tools and skills in this workspace.
Follow these guidelines to ensure consistency and proper integration.
"""

## Tool Architecture Overview

```
Workspace/
├── agent.py                    # Unified agent (skill routing)
├── mcp_client.py               # Unified MCP client (NEW)
├── .agent/
│   ├── skills/
│   │   ├── {skill-name}-expert/
│   │   │   └── SKILL.md           # Knowledge base
│   ├── templates/
│   │   └── agent_client_template.md # Agent client template (NEW)
│   └── skill_registry.json       # Auto-generated skill registry
├── {tool-name}-tool/
│   ├── agent_client.py            # AI-powered entry point
│   ├── main.py                  # Core tool implementation
│   ├── mcp_server.py            # MCP server (optional)
│   ├── requirements.txt           # Dependencies
│   ├── config/                  # Configuration
│   ├── templates.md             # Command templates
│   └── README.md               # Documentation
└── scripts/
    ├── discover_skills.py        # Auto-generate skill registry
    └── create_tool.py          # Tool scaffolding (FUTURE)
```

---

## Tool Types

### Type 1: Subprocess Tools

**Best for:** Simple CLI tools without MCP

**Examples:** yt-dlp-tool, news-aggregator-tool, imgconv-tool

**Characteristics:**
- Have `main.py` as core implementation
- Use `subprocess.run()` to execute
- No MCP server needed
- Simple command-line interface

**Requirements:**
```
{tool-name}-tool/
├── main.py              # Core implementation
├── agent_client.py       # Entry point (use template!)
├── requirements.txt       # Dependencies
├── templates.md         # Optional: command templates
└── README.md           # Documentation
```

**agent_client.py Pattern:**
```python
# Use template from .agent/templates/agent_client_template.md
INTEGRATION_TYPE = "subprocess"

def run_tool(**kwargs):
    cmd = [python_exe, TOOL_SCRIPT]
    # Convert kwargs to CLI args
    result = subprocess.run(cmd, ...)
    return result
```

---

### Type 2: MCP Server Tools

**Best for:** Tools needing deep AI integration via MCP protocol

**Examples:** playwright-tool, trendradar-tool (external)

**Characteristics:**
- Have `mcp_server.py` implementing MCP protocol
- Use `mcp_client.py` for integration
- Provide 10+ tools with standardized schema
- Async execution

**Requirements:**
```
{tool-name}-tool/
├── mcp_server.py        # MCP server implementation
├── agent_client.py       # Entry point (use template!)
├── requirements.txt       # Must include: mcp>=0.9.0
├── templates.md         # Optional: command templates
└── README.md           # Documentation
```

**agent_client.py Pattern:**
```python
# Use template from .agent/templates/agent_client_template.md
INTEGRATION_TYPE = "mcp"

from mcp_client import create_mcp_client

client = create_mcp_client(
    server_path=MCP_SERVER_SCRIPT,
    server_name="my-tool-mcp",
    is_external=False  # True for external MCP like TrendRadar
)

async def run_tool(action: str, **kwargs):
    result = await client.call_tool(action, **kwargs)
    return result
```

**External MCP Pattern (like TrendRadar):**
```python
INTEGRATION_TYPE = "mcp"
MCP_SERVER_PATH = "~/TrendRadar/mcp_server/server.py"  # External path
IS_EXTERNAL_MCP = True
```

---

### Type 3: Meta Skills

**Best for:** Skills that provide guidance only

**Examples:** literature-search-expert, mcp-builder-expert, tool-development-expert

**Characteristics:**
- No `main.py` or `mcp_server.py`
- Display `SKILL.md` content
- Provide guidance and instructions
- Type: "meta" in skill registry

**Requirements:**
```
.agent/skills/{skill-name}-expert/
└── SKILL.md           # Knowledge base only
```

**Unified agent.py handles these:**
- When queried, displays SKILL.md content
- User gets guidance, no execution

---

## Skill Registry Format

### Registry Entry Structure

```json
{
  "name": "{skill-name}-expert",
  "function_name": "skill-name",
  "type": "execution",           // "execution" | "meta"
  "integration": "subprocess",   // "subprocess" | "mcp" | "none"
  "has_main": true,              // true for execution tools
  "has_mcp_server": false,       // true for MCP server tools
  "is_external": false,           // true for external MCP (TrendRadar)
  "tool_dir": "{tool-name}-tool",
  "description": "...",
  "status": "active",
  "path": "/path/to/skill",
  "skill_md": "/path/to/SKILL.md"
}
```

### Field Descriptions

| Field | Required | Values | Description |
|--------|----------|---------|-------------|
| `name` | ✅ | `{skill-name}-expert` | Skill name (expert suffix) |
| `function_name` | ✅ | `{skill-name}` | Short function name |
| `type` | ✅ | `execution` | `meta` | Skill type |
| `integration` | ✅ | `subprocess` | `mcp` | `none` | Integration method |
| `has_main` | ✅ | `true` | `false` | Has main.py |
| `has_mcp_server` | ❌ | `true` | `false` | Has mcp_server.py |
| `is_external` | ❌ | `true` | `false` | External MCP server |
| `tool_dir` | ✅ | `{tool-name}-tool` | Tool directory name |
| `description` | ✅ | string | Tool description |
| `status` | ✅ | `active` | `inactive` | Skill status |
| `path` | ✅ | string | Absolute path to skill |
| `skill_md` | ✅ | string | Absolute path to SKILL.md |

---

## Step-by-Step: Creating a New Tool

### Option A: Subprocess Tool

1. **Create directory:**
   ```bash
   mkdir my-tool-tool
   cd my-tool-tool
   ```

2. **Copy and adapt template:**
   ```bash
   cp ../.agent/templates/agent_client_template.md agent_client.py
   # Edit placeholders: {{TOOL_NAME}}, etc.
   ```

3. **Implement main.py:**
   ```python
   #!/usr/bin/env python3
   import argparse
   import sys

   def main():
       parser = argparse.ArgumentParser()
       parser.add_argument("--param1")
       args = parser.parse_args()
       # Your tool logic here

   if __name__ == "__main__":
       main()
   ```

4. **Create requirements.txt:**
   ```
   requests>=2.32.5
   # Add your dependencies
   ```

5. **Create SKILL.md:**
   ```bash
   mkdir -p ../.agent/skills/my-tool-expert
   cd ../.agent/skills/my-tool-expert
   # Create comprehensive SKILL.md
   ```

6. **Register skill:**
   ```bash
   cd ..
   python scripts/discover_skills.py
   ```

7. **Test:**
   ```bash
   cd my-tool-tool
   python agent_client.py "menu"
   python agent_client.py "test command"
   ```

### Option B: MCP Server Tool

1. **Create directory and requirements:**
   ```bash
   mkdir my-mcp-tool
   cd my-mcp-tool

   cat > requirements.txt << EOF
   mcp>=0.9.0
   # Add other dependencies
   EOF
   ```

2. **Implement mcp_server.py:**
   ```python
   from mcp.server import Server
   from mcp.server.stdio import stdio_server

   server = Server("my-mcp-server", "1.0.0")

   @server.tool()
   def my_tool(param1: str) -> str:
       return f"Received: {param1}"

   async def main():
       async with stdio_server() as (read, write):
           async with Server(read, write) as server:
               await server.run()
   ```

3. **Copy agent_client.py template:**
   ```bash
   cp ../.agent/templates/agent_client_template.md agent_client.py
   # Set: INTEGRATION_TYPE = "mcp"
   # Set: IS_EXTERNAL_MCP = False
   # Implement MCP client integration
   ```

4. **Register and test:**
   ```bash
   cd ..
   python scripts/discover_skills.py
   cd my-mcp-tool
   python agent_client.py "menu"
   ```

### Option C: External MCP Tool (TrendRadar pattern)

1. **Install external MCP server:**
   ```bash
   # TrendRadar example
   git clone https://github.com/sansan0/TrendRadar.git ~/TrendRadar
   cd ~/TrendRadar
   pip install -r requirements.txt
   ```

2. **Create tool directory:**
   ```bash
   mkdir trendradar-tool
   cd trendradar-tool
   ```

3. **Create symlink:**
   ```bash
   # For external MCP servers
   ln -s ~/TrendRadar/mcp_server trendradar-mcp
   ```

4. **Copy agent_client.py template:**
   ```bash
   cp ../.agent/templates/agent_client_template.md agent_client.py
   # Set: INTEGRATION_TYPE = "mcp"
   # Set: IS_EXTERNAL_MCP = True
   # Set: MCP_SERVER_PATH = "trendradar-mcp/server.py"
   ```

5. **Create requirements.txt:**
   ```
   mcp>=0.9.0
   ```

---

## Unified MCP Client Usage

The new `mcp_client.py` provides unified MCP integration:

### Importing

```python
# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_client import MCPClient, create_mcp_client
```

### Creating Client

```python
# For local MCP server
client = create_mcp_client(
    server_path="mcp_server.py",
    server_name="my-tool-mcp",
    is_external=False
)

# For external MCP server (like TrendRadar)
client = create_mcp_client(
    server_path="~/TrendRadar/mcp_server/server.py",
    server_name="trendradar-mcp",
    is_external=True
)
```

### Calling Tools

```python
# Asynchronous (preferred)
result = await client.call_tool("tool_name", param1="value1")

# Synchronous wrapper
result = client.call_tool_sync("tool_name", param1="value1")
```

### Listing Tools

```python
tools = await client.list_tools()
for tool in tools:
    print(f"{tool['name']}: {tool['description']}")
```

---

## Common Patterns and Anti-Patterns

### ✅ DO: Use mcp_client.py

```python
# Correct pattern
from mcp_client import create_mcp_client

client = create_mcp_client(
    server_path="mcp_server.py",
    server_name="my-mcp"
)

result = client.call_tool_sync("tool_name", param="value")
```

### ❌ DON'T: Assume non-existent functions

```python
# Wrong pattern (caused the bug!)
from agent import call_mcp_tool  # This doesn't exist!

# Always check if function exists before importing
```

### ✅ DO: Use subprocess for simple tools

```python
# Correct pattern for subprocess tools
import subprocess

cmd = [python_exe, TOOL_SCRIPT, "--param", "value"]
result = subprocess.run(cmd, capture_output=True, text=True)
```

### ❌ DON'T: Mix patterns inconsistently

```python
# Wrong: subprocess tool trying to use MCP
import subprocess
# ... subprocess.run(...)

# But also trying to import MCP
from mcp import Client  # Not needed!

# Pick one pattern and stick to it
```

---

## Testing Checklist

Before committing a new tool, verify:

- [ ] Syntax check: `python3 -m py_compile agent_client.py`
- [ ] Import check: `python3 -c "from mcp_client import create_mcp_client"`
- [ ] Menu display: `python agent_client.py "menu"` works
- [ ] Direct action: `python agent_client.py --action test` works (if applicable)
- [ ] Skill registration: `python ../scripts/discover_skills.py` includes new skill
- [ ] Documentation: `README.md` is complete
- [ ] Requirements: All dependencies in `requirements.txt`
- [ ] Error handling: Try-except blocks for all external calls

---

## Migration Guide

### Converting Existing Tools

If you have an old tool using the wrong pattern:

1. **Identify the pattern:**
   - Does it use `subprocess.run(main.py)`? → Subprocess tool
   - Does it assume MCP client from agent.py? → Broken MCP tool

2. **Select correct template:**
   - Subprocess: Use `INTEGRATION_TYPE = "subprocess"`
   - MCP: Use `INTEGRATION_TYPE = "mcp"`

3. **Copy template:**
   ```bash
   cp .agent/templates/agent_client_template.md {tool}-tool/agent_client.py
   ```

4. **Adapt placeholders:**
   - Set `{{TOOL_NAME}}` to actual name
   - Set `{{INTEGRATION_TYPE}}` correctly
   - Add tool-specific code

5. **Test thoroughly:**
   - Menu display works
   - Tool execution works
   - Error handling works

---

## File Standards

### agent_client.py

- Shebang: `#!/usr/bin/env python3`
- Encoding: `# -*- coding: utf-8 -*-`
- Imports: Group stdlib, third-party, local
- Functions: Type hints from `typing` module
- Error handling: Try-except with descriptive messages

### SKILL.md

- Frontmatter: Name and description
- Structure: Clear sections with headers
- Content: Comprehensive tool documentation
- Language: Chinese for Chinese tools, English otherwise

### requirements.txt

- Versions: Pin major versions: `package>=1.0.0,<2.0.0`
- Format: One package per line
- MCP tools: Always include `mcp>=0.9.0`

### README.md

- Badge: Tool type and status
- Features: List main capabilities
- Installation: Prerequisites and steps
- Usage: Examples for common tasks
- Troubleshooting: Common issues and solutions

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'mcp_client'"

**Cause:** Not adding parent directory to sys.path

**Solution:**
```python
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### Issue: "MCP server not found"

**Cause:** MCP server path incorrect or not installed

**Solution:** Run installation script or create symlink

### Issue: "ImportError: cannot import name 'call_mcp_tool'"

**Cause:** Using deprecated pattern

**Solution:** Use `mcp_client.py` module instead:
```python
from mcp_client import create_mcp_client
```

---

## Resources

- **Unified Agent**: `agent.py`
- **MCP Client**: `mcp_client.py`
- **Template**: `.agent/templates/agent_client_template.md`
- **Registry**: `.agent/skill_registry.json`
- **Code Style**: `AGENTS.md`
- **MCP Protocol**: https://modelcontextprotocol.io

---

**Last Updated**: 2025-01-25
