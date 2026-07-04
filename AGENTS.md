# AGENTS.md

## Build/Lint/Test Commands

### Frontend (Next.js - `fuck_the_exam/frontend/`)

```bash
# Development
npm run dev              # Start dev server on 0.0.0.0:3000
npm run build            # Build for production
npm run start            # Start production server
npm run lint             # Run ESLint
```

### Backend (FastAPI - `fuck_the_exam/backend/`)

```bash
# Development
cd fuck_the_exam && uvicorn backend.main:app --reload --port 28888
# Or using python
python -m backend.main

# Testing (if pytest is configured)
pytest                    # Run all tests
pytest tests/specific_test.py -v  # Run single test file
pytest tests/ -k "test_name" -v   # Run tests matching pattern
```

### Tool Execution (Python scripts)

```bash
# yt-dlp-tool
cd .agent/skills/yt-dlp-expert/tool && python agent_client.py "<query>"
python main.py <url> [options]

# news-aggregator-tool
cd .agent/skills/news-aggregator-expert/tool && python agent_client.py "<query>"
python main.py --source hackernews --limit 10 --keyword "AI" --deep

# imgconv-tool
cd .agent/skills/imgconv-expert/tool && python agent_client.py "<query>"
python main.py --action convert --input image.png --output image.jpg --format jpeg

# Backend standalone scripts
python add_data.py       # Add knowledge data
python debug_db.py       # Debug database
```

## Environment Configuration

- **Backend Port**: 28888
- **Frontend Port**: 3000 (local), 23333 (Docker)
- **Knowledge Base Path**: `backend/knowledge_base/`
- **Questions Storage**: `backend/json_questions/`
- **Database**: SQLite at `backend/n1_app.db`

## Code Style Guidelines

### Python (Backend & Tools)

- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Imports**: Group stdlib, third-party, local imports (separated by blank lines)
- **Types**: Use type hints from `typing` module (List, Optional, Dict, Any)
- **Database**: SQLAlchemy ORM with declarative models
- **API**: Pydantic BaseModel for request/response schemas
- **Error Handling**: Raise HTTPException from FastAPI for API errors

Example:

```python
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

def get_user(db: Session, user_id: int) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### JavaScript/React (Frontend)

- **Naming**: `camelCase` for variables/functions, `PascalCase` for components
- **Imports**: Absolute imports from `components/`, `lib/`, `contexts/`
- **Components**: Functional components with hooks (useState, useEffect)
- **Styling**: Tailwind CSS utility classes
- **State Management**: React Context for global state

Example:

```javascript
"use client";
import { useState, useEffect } from "react";
import { Card, CardHeader } from "../components/ui/card";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  // ...
}
```

### Project-Specific Conventions

#### Cursor Rules (from `.cursorrules`)

1. **Prioritize `.agent` Directory**: Check `.agent/skills/` and `.agent/workflows/` before implementing
2. **Use Specialized Scripts**: Prefer scripts in `.agent/skills/*/scripts/` over generic searches
3. **Workflow Adherence**: Follow `.agent/workflows/` SOPs for standard tasks
4. **Session Tracking**: Update `.agent/task.md` and `implementation_plan.md` for progress

#### File Organization

- **Backend**: `models.py` (DB models), `main.py` (FastAPI routes), `services/` (business logic)
- **Frontend**: `app/` (Next.js pages), `components/` (reusable UI), `lib/` (utilities)
- **Tools**: `{name}-tool/agent_client.py` as entry point

#### Error Handling

- **Backend**: Return 4xx/5xx HTTP status codes with descriptive messages
- **Frontend**: Display user-friendly error messages, log details to console
- **Tools**: Use subprocess error handling with try/except blocks

#### Database Conventions

- Use SQLAlchemy relationships with `back_populates`
- Add indexes on frequently queried fields (id, hash, knowledge_point)
- Use `server_default=func.now()` for timestamps
- Implement CASCADE delete on foreign keys

## Testing Notes

- No test framework detected in pyproject.toml
- Verify test commands before running (check for pytest, unittest, or custom test scripts)
- When adding tests, place them in `tests/` directory following Python test naming: `test_*.py` or `*_test.py`

## Quick Reference

```bash
# Start full stack
cd fuck_the_exam && npm run dev  # Terminal 1
cd fuck_the_exam && uvicorn backend.main:app --reload --port 28888  # Terminal 2

# Unified agent - single entry point for all tools
python core/agent.py "your request here"
```

## Unified Agent System

### Quick Start

```bash
# Single entry point for all tasks
python core/agent.py "下载这个视频 https://www.youtube.com/watch?v=xxx"
python core/agent.py "看看 Hacker News 有什么 AI 新闻"
python core/agent.py "Create a new MCP server for GitHub API"
```

### How It Works

1. **Auto-Discovery**: Scans `.agent/skills/` directory for all available skills
2. **AI Selection**: Analyzes request to select most appropriate skill
3. **Smart Routing**:
   - Execution skills: Routes to `{tool}/agent_client.py`
   - Meta skills: Displays guidance from SKILL.md

### Maintaining Documentation

```bash
# When adding new skills/tools, run:
python scripts/discover_skills.py  # Regenerate skill registry
python scripts/sync_docs.py      # Update AGENTS.md and AGENT_INSTRUCTIONS.md
```

See `UNIFIED_AGENT.md` for complete documentation.

## Agent Skills Directory

### Overview

The `.agent/skills/` directory contains expert knowledge bases (skills) that map to executable tools. Before implementing new functionality, always check if a relevant skill exists.

### Skills Directory Structure

```
.agent/
├── skills/
│   ├── {skill-name}-expert/
│   │   ├── SKILL.md          # Expert knowledge and usage instructions
│   │   └── tool/             # Implementation code (scripts, main.py, etc.)
│   │       ├── agent_client.py
│   │       └── main.py
│   └── ...
└── task.md                   # Session tracking (if present)
```

### Skill-to-Tool Mapping

| Skill Name | Tool Directory | Description | Status |
|-----------|---------------|-------------|--------|
| `anthropics-skills-expert` | `.agent/skills/anthropics-skills-expert/tool/` | Expert for browsing and porting skills f... | Active |
| `clawdbot-integration-expert` | (Meta-skill) | Automated integration of systematic-skil... | Active |
| `frontend-design-expert` | (Meta-skill) | Create distinctive, production-grade fro... | Active |
| `imgconv-expert` | `.agent/skills/imgconv-expert/tool/` | Professional image processing expert bas... | Active |
| `literature-search-expert` | (Meta-skill) | 资深文献计量学专家与智能检索系统。 | Active |
| `mcp-builder-expert` | (Meta-skill) | Guide for creating high-quality MCP (Mod... | Active |
| `monty-expert` | `.agent/skills/monty-expert/tool/` | Secure Python interpreter for AI code execution with <1ms startup | Active |
| `news-aggregator-expert` | `.agent/skills/news-aggregator-expert/tool/` | Comprehensive news aggregator that fetch... | Active |
| `paper-audit-expert` | `.agent/skills/paper-audit-expert/tool/` | Rigorous academic auditing workflow (Sta... | Active |
| `pdf-downloader-expert` | `.agent/skills/pdf-downloader-expert/tool/` | PDF Link Downloader and Archiving Expert... | Active |
| `playwright-expert` | `.agent/skills/playwright-expert/tool/` | Professional web testing and automation ... | Active |
| `tool-development-expert` | (Meta-skill) | Meta-skill for standardizing AI creation... | Active |
| `vtt-recitation-expert` | (Meta-skill) | Converts VTT subtitle files into Obsidia... | Active |
| `yt-dlp-expert` | `.agent/skills/yt-dlp-expert/tool/` | 工业级媒体提取协议。强制执行依赖校验与流选择逻辑，杜绝无效参数组合。 | Active |
| `english-learning-expert` | (Meta-skill) | 奶爸的英语教室 - 系统性英语学习方法指南（A1-C2全级别） | Active |




### Using Skills

1. **Before implementing**: Check `.agent/skills/` for relevant expertise
2. **Read the skill file**: Each skill has a `SKILL.md` with expert knowledge
3. **Locate the tool**: Find the corresponding `{name}-tool/` directory
4. **Execute via agent_client.py**: Use `python {tool}/agent_client.py "<query>"`

### Creating New Skills/Tools

1. Create skill: `.agent/skills/{function-name}-expert/SKILL.md`
2. Create tool: `{function-name}-tool/`
3. Create entry point: `{function-name}-tool/agent_client.py`
4. Update the mapping table in this file
5. Test thoroughly before use

### Naming Conventions

- **Skill names**: `{function-name}-expert` (e.g., `yt-dlp-expert`)
- **Tool directories**: `{function-name}-tool` (e.g., `yt-dlp-tool`)
- **Entry points**: `{tool}/agent_client.py` (always)

### MCP Integration Patterns

#### Tool Type 1: Subprocess Tools

**Best for:** Simple CLI tools without MCP
**Examples:** yt-dlp-tool, news-aggregator-tool, imgconv-tool

**Implementation:**

```python
# In agent_client.py
def run_tool(**kwargs):
    cmd = [python_exe, TOOL_SCRIPT]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result
```

**Characteristics:**

- Have `main.py` as core implementation
- Use `subprocess.run()` to execute
- No MCP server needed
- Simple command-line interface

---

#### Tool Type 3: Monty External Functions (NEW)

**Best for:** AI code execution with multi-step data processing and complex logic
**Examples:** monty-expert (this skill!)

**Usage:**
```python
# List all available functions
python .agent/skills/monty-expert/tool/main.py --list-external-funcs

# Execute Python code with external functions
python .agent/skills/monty-expert/tool/main.py --use-external-funcs --code '
    news = fetch_news("hackernews", 10)
    print(len(news))
'
```

**Integration:** External functions from various skills can be called from Monty code, enabling AI to combine multiple tools in a single execution.

**Key Features:**
- Ultra-fast startup (<1μs)
- Secure sandbox with restricted external access
- Support for complex Python logic (loops, conditions, data structures)
- State serialization for resumable operations

**Characteristics:**
- Have SKILL.md with expert knowledge
- Have external_functions.py with function registry
- Provide main.py or mcp_server.py for tool execution
- Can be used via --use-external-funcs flag

**Implementation:**
```python
# In external_functions.py
@register_external_function("tool_function")
def tool_function(param1: str) -> dict:
    from pathlib import Path
    import subprocess
    import sys
    import json
    
    tool_dir = Path(__file__).parent.parent.parent / "skill-name-expert" / "tool"
    main_py = tool_dir / "main.py"
    
    cmd = [sys.executable, str(main_py)]
    cmd.extend([...])
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode != 0:
        return {"error": result.stderr}
    
    return json.loads(result.stdout)
```

---

#### Tool Type 4: Meta Skills (Exempt from Monty Integration)

**Not Required for Monty Integration:**
- ❌ frontend-design-expert (UI/frontend only)
- ❌ mcp-builder-expert (documentation only)
- ❌ literature-search-expert (documentation only)
- **MCP Integration Patterns** section above

**Characteristics:**

- Have `mcp_server.py` implementing MCP protocol
- Use `mcp_client.py` for integration
- Provide 10+ tools with standardized schema
- Async execution

**Requirements:**

```txt
mcp>=0.9.0
```

---

#### Tool Type 3: Meta Skills

**Best for:** Skills that provide guidance only
**Examples:** literature-search-expert, mcp-builder-expert, tool-development-expert

**Implementation:**

```python
# In agent_client.py (minimal)
def main():
    # Display SKILL.md content
    print(load_skill_context())
```

**Characteristics:**

- No `main.py` or `mcp_server.py`
- Display `SKILL.md` content only
- Unified agent.py handles routing and display

---

### Anti-Patterns

#### ❌ DO NOT: Assume non-existent functions

```python
# Wrong pattern (caused bug!)
from agent import call_mcp_tool  # This function doesn't exist!
```

**Correct pattern:**

```python
# Use unified MCP client
from mcp_client import create_mcp_client

client = create_mcp_client(
    server_path="mcp_server.py",
    server_name="my-tool-mcp"
)
```

---

### Monty External Functions Integration

#### Overview

Monty provides a secure Python interpreter for AI code execution with <1ms startup. Skills can register external functions that Monty can call, enabling AI to combine multiple tools in a single execution.

#### Integrated Skills Status

| Skill Name | External Functions | Status | Functions Added |
|-----------|-------------------|--------|-----------------|
| `news-aggregator-expert` | fetch_news, fetch_hackernews, fetch_weibo, fetch_github_trending | ✅ Integrated | 4 |
| `pdf-downloader-expert` | download_pdf, read_file, write_file | ✅ Integrated | 3 |
| `imgconv-expert` | convert_image | ✅ Integrated | 1 |
| `yt-dlp-expert` | download_video | ✅ Integrated | 1 |
| `paper-audit-expert` | paper_audit_extract, paper_audit_analyze, paper_audit_visualize | ✅ Integrated | 3 |
| `playwright-expert` | (MCP type - direct integration available) | ⏸️ Pending | N/A |
| `anthropics-skills-expert` | (Meta-skill - exempt) | ⏭️ Exempt | N/A |

**Total Integrated:** 15 external functions from 5 execution skills

#### Usage Examples

```bash
# List all available external functions
python .agent/skills/monty-expert/tool/main.py --list-external-funcs

# Use news aggregator
python .agent/skills/monty-expert/tool/main.py --use-external-funcs --code '
    news = fetch_news("hackernews", 10, "AI")
    for item in news:
        print(item.get("title"))
'

# Combine multiple tools
python .agent/skills/monty-expert/tool/main.py --use-external-funcs --code '
    # Download PDF
    pdf_path = download_pdf("https://arxiv.org/pdf/2301.xxxxx.pdf")
    
    # Extract and analyze
    result = paper_audit_extract(pdf_path)
    audit = paper_audit_analyze(result.get("content", ""))
    
    # Visualize
    svg = paper_audit_visualize(audit)
    print("Audit score:", audit.get("score"))
'
```

#### Integration Requirements

For new execution skills to integrate with Monty:

1. Add external functions to `.agent/skills/monty-expert/tool/external_functions.py`
2. Use `@register_external_function` decorator
3. Call tools via subprocess or MCP client
4. Return JSON-serializable results
5. Handle errors gracefully with error dict format

See `.agent/skills/tool-development-expert/SKILL.md` Section 3.3 for complete integration guidelines.
