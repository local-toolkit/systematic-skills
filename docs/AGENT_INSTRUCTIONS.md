# AGENT_INSTRUCTIONS.md

## 1. Project Architecture

The AI Agent toolset consists of two core components:
- **Skills**: Expert knowledge bases located in `.agent/skills/{name}-expert/SKILL.md`
- **Tools**: Execution scripts located in `{name}-tool/agent_client.py`

## 2. Execution Workflow

When a user submits a task request, the AI should follow these steps:

### Step 1: Analyze User Request
Identify the task type and determine the required skill

### Step 2: Locate Corresponding Skill
Find the corresponding `SKILL.md` file in the `.agent/skills/` directory

### Step 3: Locate Execution Tool
Find the corresponding `{name}-tool/` directory based on the skill name

### Step 4: Review Execution Entry Point
Read `agent_client.py` to understand the tool interface and calling method

### Step 5: Execute Task
Use the command: `python3 {tool}/agent_client.py "<user request>"`

## 3. Current Available Tools Mapping

| Skill Name | Tool Directory | Description | Status |
|-----------|---------------|-------------|--------|
| imgconv-expert | tools/imgconv-tool |  | Active |
| literature-search-expert | (Not Applicable) | 璧勬繁鏂囩尞璁￠噺瀛︿笓瀹朵笌鏅鸿兘妫€绱㈢郴缁燂紝涓撻棬鐢ㄤ簬瀛︽湳鎵洸銆佹柟娉曡绛涢€夊強楂樼疆淇″害璇佹嵁鍚堟垚銆?| Active |
| mcp-builder-expert | (Not Applicable) | Guide for creating high-quality MCP (Model Context... | Active |
| news-aggregator-expert | tools/news-aggregator-tool | Comprehensive news aggregator that fetches, filter... | Active |
| paper-audit-expert | tools/paper-audit-tool | rigorous academic auditing workflow for research p... | Active |
| pdf-downloader-expert | tools/pdf-downloader-tool | PDF 閾炬帴涓嬭浇涓庡綊妗ｄ笓瀹躲€傝嚜鍔ㄥ寲浠?URL 鎻愬彇骞朵笅杞?PDF 鏂囦欢鍒?tools/paper_audit/i... | Active |
| playwright-expert | tools/playwright-tool | Professional web testing and automation expert for... | Active |
| tool-development-expert | (Not Applicable) | Meta-skill for standardizing AI creation of new sk... | Active |
| trendradar-expert | tools/trendradar-tool | Comprehensive Chinese news aggregation and trend a... | Active |
| yt-dlp-expert | tools/yt-dlp-tool | 宸ヤ笟绾у獟浣撴彁鍙栧崗璁€傚己鍒舵墽琛屼緷璧栨牎楠屼笌娴侀€夋嫨閫昏緫锛屾潨缁濇棤鏁堝弬鏁扮粍鍚堛€?| Active |








## 4. Tool Execution Standards

- Each tool directory must contain `agent_client.py` as the execution entry point
- Execution command format: `python3 {tool}/agent_client.py "<request content>"`
- Tools should return execution results and error information
- Tool interfaces should accept user requests as command-line arguments

## 5. Error Handling Strategy

- **Skill not found**: Inform user that the requested function is not currently supported
- **Tool not found**: Inform user that the tool is not implemented yet and cannot execute the task
- **Execution failed**: Provide specific troubleshooting suggestions based on the error information returned by the tool
- **Invalid parameters**: Guide user to provide correct input format based on the tool's requirements

## 6. Adding New Tools Guide

1. Create skill file: `.agent/skills/{function-name}-expert/SKILL.md`
2. Create tool directory: `{function-name}-tool/`
3. Implement execution entry: `{function-name}-tool/agent_client.py`
4. Update the mapping table in this document
5. Test the tool to ensure it works correctly

## 7. Quick Reference

```
Project Root: /mnt/c/Users/xujin/workspace/Tools
Skills Directory: .agent/skills/
Tool Entry Example: python3 yt-dlp-tool/agent_client.py "Download video..."
```

## 8. Naming Conventions

- **Skill names**: `{function-name}-expert`
- **Tool directories**: `{function-name}-tool`
- Example: `yt-dlp-expert` skill 鈫?`yt-dlp-tool` directory

## 9. Unified Agent Entry Point

### Quick Start
```bash
# Single entry point for all tasks
python agent.py "your request here"

# Examples
python agent.py "涓嬭浇杩欎釜瑙嗛 https://www.youtube.com/watch?v=xxx"
python agent.py "Create a new MCP server for GitHub API"
```

### How It Works
1. **Discover Skills**: Automatically scans `.agent/skills/` directory
2. **AI Selection**: Analyzes request to select most appropriate skill
3. **Route Execution**:
   - Execution skills: Routes to `{tool}/agent_client.py`
   - Meta skills: Displays guidance from SKILL.md

### Maintaining Documentation
When adding new skills/tools:
```bash
# Regenerate skill registry
python scripts/discover_skills.py

# Update AGENTS.md and AGENT_INSTRUCTIONS.md
python scripts/sync_docs.py
```

### Skill Metadata
Each SKILL.md should include YAML frontmatter for proper registration:
```yaml
---
name: skill-name-expert
description: Brief description
status: active
type: execution  # or 'meta'
---
```

See `UNIFIED_AGENT.md` for complete documentation of the unified agent system.
