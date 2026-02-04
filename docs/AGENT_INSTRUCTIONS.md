# AGENT_INSTRUCTIONS.md

## 1. Project Architecture

The AI Agent toolset consists of two core components:

- **Skills**: Expert knowledge bases located in `.agent/skills/{name}-expert/SKILL.md`
- **Tools**: Execution scripts located in `.agent/skills/{name}-expert/tool/agent_client.py`

## 2. Execution Workflow

When a user submits a task request, the AI should follow these steps:

### Step 1: Analyze User Request

Identify the task type and determine the required skill.

### Step 2: Locate Corresponding Skill

Find the corresponding `SKILL.md` file in the `.agent/skills/` directory.

### Step 3: Locate Execution Tool

Find the tool directory within the skill package (usually `.agent/skills/{name}-expert/tool/`).

### Step 4: Review Execution Entry Point

Read `agent_client.py` to understand the tool interface and calling method.

### Step 5: Execute Task

Use the unified command: `python3 core/agent.py "<user request>"`
Or directly: `python3 .agent/skills/{name}-expert/tool/agent_client.py "<user request>"`

## 3. Current Available Tools Mapping

| Skill Name                  | Tool Directory                              | Description                                                          | Status |
| --------------------------- | ------------------------------------------- | -------------------------------------------------------------------- | ------ |
| anthropics-skills-expert    | .agent/skills/anthropics-skills-expert/tool | Expert for browsing and porting skills from the of...                | Active |
| clawdbot-integration-expert | (Not Applicable)                            | Automated integration of systematic-skills into Cl...                | Active |
| imgconv-expert              | .agent/skills/imgconv-expert/tool           | Professional image processing expert based on suns...                | Active |
| literature-search-expert    | (Not Applicable)                            | 资深文献计量学专家与智能检索系统。                                   | Active |
| mcp-builder-expert          | (Not Applicable)                            | Guide for creating high-quality MCP (Model Context...                | Active |
| news-aggregator-expert      | .agent/skills/news-aggregator-expert/tool   | Comprehensive news aggregator that fetches, filter...                | Active |
| paper-audit-expert          | .agent/skills/paper-audit-expert/tool       | Rigorous academic auditing workflow (Stanford 3-Pa...                | Active |
| pdf-downloader-expert       | .agent/skills/pdf-downloader-expert/tool    | PDF Link Downloader and Archiving Expert. Automati...                | Active |
| playwright-expert           | .agent/skills/playwright-expert/tool        | Professional web testing and automation expert for...                | Active |
| tool-development-expert     | (Not Applicable)                            | Meta-skill for standardizing AI creation of new sk...                | Active |
| vtt-recitation-expert       | .agent/skills/vtt-recitation-expert/scripts | Converts VTT subtitle files into Obsidian-friendly...                | Active |
| yt-dlp-expert               | .agent/skills/yt-dlp-expert/tool            | 工业级媒体提取协议。强制执行依赖校验与流选择逻辑，杜绝无效参数组合。 | Active |

## 4. Tool Execution Standards

- Each tool directory must contain `agent_client.py` as the execution entry point.
- Execution command format: `python3 .agent/skills/{name}-expert/tool/agent_client.py "<request content>"`
- Tools should return execution results and error information.
- Tool interfaces should accept user requests as command-line arguments.

## 5. Error Handling Strategy

- **Skill not found**: Inform user that the requested function is not currently supported.
- **Tool not found**: Inform user that the tool is not implemented yet.
- **Execution failed**: Provide specific troubleshooting suggestions based on the error.

## 6. Adding New Tools Guide

1. Create skill file: `.agent/skills/{function-name}-expert/SKILL.md`
2. Create tool directory: `.agent/skills/{function-name}-expert/tool/`
3. Implement execution entry: `.agent/skills/{function-name}-expert/tool/agent_client.py`
4. Update the mapping table using `python scripts/sync_docs.py`
5. Test the tool to ensure it works correctly.

## 7. Quick Reference

```
Skills Directory: .agent/skills/
Tool Entry Example: python3 .agent/skills/yt-dlp-expert/tool/agent_client.py "Download video..."
Unified Entry Example: python3 core/agent.py "Get news from hacker news"
```

## 8. Naming Conventions

- **Skill names**: `{function-name}-expert`
- **Tool directories**: `.agent/skills/{name}-expert/tool`
- Example: `yt-dlp-expert` skill -> `.agent/skills/yt-dlp-expert/tool`

## 9. Unified Agent Entry Point

### Quick Start

```bash
# Single entry point for all tasks
python core/agent.py "your request here"

# Examples
python core/agent.py "下载这个视频 https://www.youtube.com/watch?v=xxx"
python core/agent.py "帮我找找 AI 相关的论文"
```

### How It Works

1. **Discover Skills**: Automatically scans `.agent/skills/` directory.
2. **AI Selection**: Analyzes request to select most appropriate skill.
3. **Route Execution**:
   - Execution skills: Routes to `tool/agent_client.py`.
   - Meta skills: Displays guidance from `SKILL.md`.

### Maintaining Documentation

When adding new skills/tools:

```bash
# Regenerate skill registry and update documentation tables
python scripts/discover_skills.py
python scripts/sync_docs.py
```

### Skill Metadata

Each `SKILL.md` should include YAML frontmatter:

```yaml
---
name: skill-name-expert
description: Brief description
status: active
type: execution # or 'meta'
---
```

See `AGENTS.md` for complete development documentation.
