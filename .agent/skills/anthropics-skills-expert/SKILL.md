---
name: anthropics-skills-expert
version: 1.0.0
description: Expert for browsing and porting skills from the official Anthropics Skills repository.
status: active
type: execution
---

# Anthropics Skills Expert

This manager skill allows you to explore and install skills directly from the official [Anthropics Skills Repository](https://github.com/anthropics/skills).

## Features

- **Inventory**: Lists all available skills in the remote repository.
- **Porting**: (Coming Soon) Automatically downloads and adapts an Anthropics skill into your local workspace format (`-expert` + `-tool`).

## Usage

### 1. List Available Skills

View the list of skills currently available in the repository.

```bash
python3 /Users/xujintao/Documents/workspace/systematic-skills/tools/anthropics-skills-tool/agent_client.py list
```

### 2. Search (Greppable)

```bash
python3 /Users/xujintao/Documents/workspace/systematic-skills/tools/anthropics-skills-tool/agent_client.py list | grep "analysis"
```

## Configuration

- **Source Repo**: `https://github.com/anthropics/skills`
- **Cache Dir**: `.tmp/anthropics_skills_cache`
