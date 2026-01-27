# Skills Integration Guide for AI Assistants

## Quick Integration Prompt

````
请帮我将 /Users/xujintao/Documents/workspace/systematic-skills/.agent/skills 目录下的所有自定义 skills 集成到 Clawdbot 工作区。

执行步骤：
1. 创建符号链接：将 .agent/skills/*-expert 链接到 ~/clawd/skills/
2. 创建工具链接：将 tools/ 目录链接到 ~/clawd/tools/
3. 重启 Clawdbot gateway

具体命令：
```bash
# 1. 链接所有 skills
for skill in /Users/xujintao/Documents/workspace/systematic-skills/.agent/skills/*-expert; do
  skill_name=$(basename "$skill")
  ln -sf "$skill" ~/clawd/skills/"$skill_name"
done

# 2. 链接 tools 目录
ln -sf /Users/xujintao/Documents/workspace/systematic-skills/tools ~/clawd/tools

# 3. 重启 gateway
clawdbot gateway restart
````

验证：

- 运行 `clawdbot skills list` 确认所有 skills 状态为 "ready"
- 在 Telegram 测试：`/news_aggregator 总结一下 hacker 头条`

```

## Directory Structure Reference

```

~/clawd/
├── skills/ → symlinks to .agent/skills/\*-expert/
│ ├── news-aggregator-expert/
│ ├── playwright-expert/
│ ├── yt-dlp-expert/
│ ├── paper-audit-expert/
│ ├── imgconv-expert/
│ ├── pdf-downloader-expert/
│ ├── literature-search-expert/
│ ├── mcp-builder-expert/
│ └── tool-development-expert/
└── tools/ → symlink to actual tools directory
├── news-aggregator-tool/
├── playwright-tool/
├── yt-dlp-tool/
├── paper-audit-tool/
├── imgconv-tool/
└── pdf-downloader-tool/

````

## Available Skills

### Tool-Based (Executable)
1. **news-aggregator-expert**: Multi-source news aggregation (HN, GitHub, etc.)
2. **playwright-expert**: Browser automation and web scraping
3. **yt-dlp-expert**: Media downloading and stream extraction
4. **paper-audit-expert**: Academic paper analysis (Stanford 3-Pass)
5. **imgconv-expert**: Image conversion and optimization
6. **pdf-downloader-expert**: Academic PDF retrieval

### Meta-Skills (Guidance Only)
7. **literature-search-expert**: Research methodology and search strategies
8. **mcp-builder-expert**: MCP server development standards
9. **tool-development-expert**: Skill/tool creation protocol

## Adding New Skills

When creating a new skill:

1. **Create skill directory**: `.agent/skills/{name}-expert/SKILL.md`
2. **Create tool directory**: `tools/{name}-tool/`
3. **Add execution path** in SKILL.md:
   ```markdown
   ### Execution (CRITICAL)
   Always execute using the absolute path:
   \`\`\`bash
   python3 /Users/xujintao/Documents/workspace/systematic-skills/tools/{name}-tool/agent_client.py "QUERY"
   \`\`\`
````

4. **Re-run integration**: The symlinks will automatically pick up new skills

## Troubleshooting

**Issue**: AI says "no implementation found"

- **Cause**: Missing `~/clawd/tools` symlink
- **Fix**: Run step 2 from the integration prompt

**Issue**: Skills not showing in `clawdbot skills list`

- **Cause**: Missing SKILL.md or incorrect frontmatter
- **Fix**: Verify SKILL.md has proper YAML frontmatter with `name:` field

**Issue**: Permission denied when executing scripts

- **Cause**: Scripts not executable
- **Fix**: `chmod +x tools/*/agent_client.py`
