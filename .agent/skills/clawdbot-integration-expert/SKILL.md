---
name: clawdbot-integration-expert
description: Automated integration of systematic-skills into Clawdbot workspace. Handles symlink creation and gateway restart.
status: active
type: execution
---

# Clawdbot Integration Expert

Automates the integration of custom skills from `systematic-skills` into Clawdbot workspace.

## Agent Instructions

### Execution (CRITICAL)

Run the following commands to integrate all skills:

```bash
# 1. Create skills directory if not exists
mkdir -p ~/clawd/skills

# 2. Link all skills
# 2. Link all skills
REPO_ROOT="$(pwd)"
for skill in "$REPO_ROOT"/.agent/skills/*-expert; do
  skill_name=$(basename "$skill")
  ln -sf "$skill" ~/clawd/skills/"$skill_name"
done



# 4. Restart gateway
clawdbot gateway restart
```

### Verification

After integration, verify with:

```bash
clawdbot skills list
```

All skills should show status "ready".

### Test Commands

Try these in Clawdbot chat:

- `/news_aggregator 总结一下 hacker 头条`
- `帮我用 playwright 访问 google.com`
- `用 yt-dlp 下载这个视频的信息`

## Available Skills

### Tool-Based (6)

1. **news-aggregator-expert**: Multi-source news aggregation
2. **playwright-expert**: Browser automation
3. **yt-dlp-expert**: Media downloading
4. **paper-audit-expert**: Academic paper analysis
5. **imgconv-expert**: Image conversion
6. **pdf-downloader-expert**: PDF retrieval

### Meta-Skills (3)

7. **literature-search-expert**: Research methodology
8. **mcp-builder-expert**: MCP server development
9. **tool-development-expert**: Skill creation protocol

## Troubleshooting

**Issue**: "no implementation found"

- **Fix**: Ensure skills are linked correctly in `~/clawd/skills`

**Issue**: Skills not listed

- **Fix**: Check SKILL.md has proper YAML frontmatter

**Issue**: Permission denied

- **Fix**: `chmod +x tools/*/agent_client.py`
