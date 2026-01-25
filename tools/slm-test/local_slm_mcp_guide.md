# 本地 SLM + MCP + Claude Skills 高效整合方案

这个方案旨在利用本地算力（Local SLM），通过 LM Studio 的原生 MCP 支持，结合 Claude 的 Skills 理念，打造一个高效、隐私、免费的智能助手。

## 1. 核心架构 (Core Architecture)

*   **大脑 (Brain):** 本地 SLM (推荐 Qwen 2.5 Coder 或 Llama 3.1)。
*   **运行环境 (Runtime):** LM Studio (v0.3.17 及以上)。
*   **手脚 (Hands):** MCP Servers (Model Context Protocol)。
*   **知识 (Knowledge):** "Skills" (通过 System Prompt 注入的流程知识)。

## 2. 模型选择 (The Brain)

SLM 的短板通常是**工具调用 (Tool Calling)** 和 **复杂指令遵循能力**。为了能跑通 MCP，我们必须选择在 Function Calling 上经过针对性训练的模型。

| 模型 | 推荐参数量 | 推荐理由 | 备注 |
| :--- | :--- | :--- | :--- |
| **Qwen 2.5 Coder** | 7B / 14B / 32B | **首选推荐**。目前的开源 Coding/Tool use 之王。对指令跟随极其敏感，非常适合理解 MCP 的工具定义。 | 14B 是性价比之选，大部分 12GB+ 显存显卡可跑。 |
| **Llama 3.1** | 8B | 生态好，但 8B base 版本工具调用能力较弱。建议寻找 **Function Calling Fine-tune** 版本 (如 HammerAI, Hermes)。 | 纯官方版 8B 可能经常格式错误。 |
| **Mistral Small 3** | 22B | 能力强，但对显存要求稍高 (24GB 推荐)。 | 逻辑非常严密。 |

**方案建议:** 下载 **Qwen 2.5 Coder 14B Instruct (GGUF)**。

## 3. 环境配置 (Runtime Setup)

LM Studio 从 v0.3.17 开始支持 MCP。它兼容 Cursor 的 `mcp.json` 格式。

### 步骤 1: 准备 LM Studio
确保安装最新版 LM Studio。

### 步骤 2: 配置 MCP (The Tools)
LM Studio 会读取配置好的 MCP Server。你需要编辑 LM Studio 的配置（通常在界面的 "Developer" 或 "Settings" -> "MCP" 区域，或者手动创建配置文件）。

**示例 config (`mcp.json`):**
假设我们要让 LLM 能够操作本地文件系统（这是最强大的能力之一）。

你需要先安装 `@modelcontextprotocol/server-filesystem` (需要 Node.js 环境)。

```bash
npx @modelcontextprotocol/server-filesystem /home/user/workspace/
```

在 LM Studio 中配置 (参考):
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/your/allowed/directory"
      ]
    },
    "git": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git"
      ]
    }
  }
}
```
*注意：Windows 用户可能需要使用绝对路径或 `cmd /c npx`.*

## 4. Skills 的整合 (The Knowledge)

"Claude Skills" 本质上是 **[流程说明] + [工具定义]**。
*   **工具定义:** 由 MCP Server 自动处理 (LM Studio 会自动把 MCP 工具转成 OpenAI 格式的 Tool definitions 喂给模型)。
*   **流程说明:** 这部分需要你手动传达给 SLM。

### "Skill Loader" 方案

我们在 LM Studio 中通过 **System Prompt (系统提示词)** 来加载具体的 Skill。

**操作流程:**
1.  找到你想用的 Claude Skill 的 `SKILL.md` (例如 "Data Analysis Skill" 或 "Coding Assistant Skill")。
2.  复制其中的 **Instructions** 部分。
3.  在 LM Studio 的 **System Prompt** 区域，粘贴以下模板：

```markdown
You are an intelligent assistant powered by Qwen 2.5 Coder.
You have access to the following tools via Model Context Protocol (MCP).

=== SKILL INSTRUCTIONS ===
[在此处粘贴 SKILL.md 的核心指令内容]
==========================

Please follow the instructions above strictly to solve the user's request.
```

### 为什么这样做？
SLM 的上下文窗口有限。不要一次性把 10 个 Skills 都塞进去。**按需加载**。
*   想写代码 -> 粘贴 "Code Architect" 的 Skill Prompt。
*   想分析数据 -> 粘贴 "Data Analyst" 的 Skill Prompt。

### 局限性提示 (Limitations)
虽然逻辑上能跑通，但 **LM Studio 的 UI 体验不同于 Claude Desktop**：
*   **无实时预览 (No Artifact Preview):** 如果模型生成了 React 组件或 HTML，你只能看到代码块，无法像 Claude 那样直接看到渲染后的网页。
*   **无计算机控制 (No Computer Use/Beta):** LM Studio 更多是作为“聊天 + 工具执行”，而不是接管你的鼠标键盘。

## 5. 验证与演示 (Verification)

**测试案例:** 让 AI 帮你重构一个 Python 文件。

1.  **启动:** LM Studio 加载 Qwen 2.5 Coder 14B。
2.  **MCP:** 启用 `filesystem` MCP Server，指向你的项目目录。
3.  **Prompt:**
    > "Help me refactor `main.py`. First, read the file properties to understand its size. Then read the content. Then suggest a refactoring plan."
4.  **观察:**
    *   模型应该首先调用 `filesystem` 的 `read_file_info` 或 `ls`。
    *   收到结果后，再次调用 `read_file`。
    *   最后给出建议。

## 6. 成功率评估 (Success Factors)

*   **成功关键点:** 模型的 Tool Calling 格式是否标准。Qwen 2.5 Coder 非常稳。
*   **潜在坑点:**
    *   **上下文长度:** 如果文件太大，SLM (8k-32k context) 可能会“遗忘”之前的步骤。建议使用 LM Studio 的 "Context Overflow Policy" 设置为 "Rolling Window"。
    *   **复杂推理:** 如果 Skill 包含非常隐晦的逻辑（例如 "第3步如果失败则跳转第1步但要修改参数..."），SLM 可能会执行错误。你需要把 Prompt 写得更直白。

## 总结
这个方案 **完全可行**。
核心是：**Qwen 2.5 Coder (模型) + LM Studio (MCP Host) + 手动注入 Skill System Prompt**。
这能让你在本地免费体验 90% 的 Claude + MCP 的能力。
