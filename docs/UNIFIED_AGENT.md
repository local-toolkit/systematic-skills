# Unified Agent System

## Overview

The Unified Agent System provides a single entry point (`agent.py`) for all tools in the repository. It automatically discovers available skills, selects the appropriate one based on your request, and routes execution accordingly.

## Quick Start

```bash
# Basic usage
python agent.py "your request here"

# Examples
python agent.py "下载这个视频 https://www.youtube.com/watch?v=xxx"
python agent.py "Create a new MCP server for GitHub API"
python agent.py "Help me develop a tool for literature search"
```

## Architecture

```
agent.py (Unified Entry Point)
    ├─→ Discovers skills from .agent/skills/
    ├─→ Uses AI to select appropriate skill
    ├─→ Routes execution:
    │   ├─→ Execution skills: {name}-tool/agent_client.py
    │   └─→ Meta skills: Display guidance from SKILL.md
```

## Components

### 1. Skill Discovery (`scripts/discover_skills.py`)
- Scans `.agent/skills/*/SKILL.md` directories
- Parses YAML frontmatter metadata
- Checks for corresponding `{name}-tool/` directories
- Generates `.agent/skill_registry.json`

### 2. Unified Agent (`agent.py`)
- Loads skill registry
- Analyzes user request with AI
- Selects most suitable skill (prefers execution over meta)
- Routes execution or displays guidance

### 3. Documentation Sync (`scripts/sync_docs.py`)
- Reads skill registry
- Updates AGENTS.md and AGENT_INSTRUCTIONS.md
- Auto-updates skill-to-tool mapping tables

## Skill Metadata Format

Each SKILL.md should include YAML frontmatter:

```yaml
---
name: skill-name-expert
description: Brief description of what this skill does
tool_dir: tool-directory-name  # Optional, auto-detected if omitted
status: active
type: execution  # or 'meta' for meta-skills
---
```

## Adding New Skills/Tools

1. Create skill directory:
   ```bash
   mkdir -p .agent/skills/{name}-expert
   ```

2. Create SKILL.md with frontmatter:
   ```bash
   .agent/skills/{name}-expert/SKILL.md
   ```

3. Create tool directory (if needed):
   ```bash
   mkdir {name}-tool
   ```

4. Implement `agent_client.py`:
   ```bash
   {name}-tool/agent_client.py
   ```

5. Run discovery and sync:
   ```bash
   python scripts/discover_skills.py
   python scripts/sync_docs.py
   ```

## File Structure

```
/mnt/c/Users/xujin/workspace/Tools/
├── agent.py                      # Unified entry point
├── scripts/
│   ├── discover_skills.py          # Skill discovery
│   └── sync_docs.py              # Documentation sync
├── .agent/
│   ├── skills/                   # Skill definitions
│   │   ├── {name}-expert/
│   │   │   └── SKILL.md
│   │   └── ...
│   └── skill_registry.json       # Auto-generated
├── AGENTS.md                    # Auto-updated
└── AGENT_INSTRUCTIONS.md         # Auto-updated
```

## AI Selection Logic

The agent uses the following priority when selecting skills:

1. **Prefer execution skills** over meta-skills when multiple options exist
2. **Match keywords** in skill names and descriptions
3. **Ask user** if no clear match or multiple equally suitable options
4. **Display guidance** for meta-skills (no tool directory)

## Supported AI Services

The unified agent tries AI services in order:

1. **OpenAI-compatible API** (if `OPENAI_API_KEY` or `OPENAI_BASE_URL` set)
2. **Local LLM** via HTTP API (checks common endpoints)
3. **Fallback** to manual user selection

## Error Handling

- **No skill matches**: Asks user to make a decision
- **Multiple matches**: Selects most suitable (execution skills prioritized)
- **Tool not found**: Displays error with guidance
- **Execution failed**: Shows tool output and exit code
