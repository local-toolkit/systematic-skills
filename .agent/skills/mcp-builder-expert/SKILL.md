---
name: mcp-builder-expert
description: Guide for creating high-quality MCP (Model Context Protocol) servers.
license: Complete terms in LICENSE.txt
---

# MCP Builder Expert

Strict standards for building MCP servers.

## 1. Project Structure & Stack

- **TypeScript (Recommended)**: Best SDK support. Use `web-fetch` for `typescript-sdk` README.
- **Python**: Use `python-sdk` README.
- **Transport**: Streamable HTTP (remote) or stdio (local).

## 2. Implementation Checklist

1.  **API Coverage**: Prioritize comprehensive endpoint coverage over "smart" tools.
2.  **Naming**: `resource_action` (e.g., `github_create_issue`).
3.  **Input Schema**: Use Zod (TS) or Pydantic (Py). detailed descriptions are mandatory.
4.  **Output**: Always return `structuredContent` or JSON when possible.
5.  **Error Handling**: Return actionable error messages, not just stack traces.

## 3. Tool Design Rules

- **Atomic**: One tool = one discrete action or API call.
- **Descriptions**: Concise but complete. Agent uses this for selection.
- **Hints**: Set `readOnlyHint`, `destructiveHint`, `idempotentHint` correctly.

## 4. Evaluation Protocol

Before shipping, create `evaluation.xml` with 10 QA pairs:

- **Independent**: No dependencies between questions.
- **Read-only**: Non-destructive.
- **Complex**: Requires multiple tool calls.
- **Verifiable**: Deterministic answers.

## 5. Reference Resources

- **Sitemap**: `https://modelcontextprotocol.io/sitemap.xml`
- **SDKs**: Fetch from GitHub (`modelcontextprotocol/typescript-sdk`, `python-sdk`).
