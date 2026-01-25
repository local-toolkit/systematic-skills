# 统一 MCP 架构设计文档

## 概述

本文档描述了为统一 MCP（Model Context Protocol）集成而设计的标准化架构。这个架构解决了之前 trendradar-tool 中出现的问题，并为所有未来的工具开发提供了标准模式。

---

## 问题根源回顾

### 原始问题

trendradar-tool 的 `agent_client.py` 假设了一个不存在的函数：

```python
# ❌ 错误的假设
from agent import call_mcp_tool  # 这个函数不存在！
```

### 根本原因

1. **缺乏统一的 MCP 客户端规范**：每个工具独立实现 MCP 集成
2. **没有标准化的 agent_client.py 模板**：开发者容易参考错误的模式
3. **技能注册表不完整**：没有标记工具类型（subprocess/MCP/meta）
4. **文档不一致**：没有明确的 MCP 集成指导

---

## 架构设计

### 核心组件

```
/
├── mcp_client.py                    # 统一 MCP 客户端（NEW）
├── agent.py                        # 统一路由器
├── .agent/
│   ├── skills/                     # 技能知识库
│   ├── templates/                   # 代码模板（NEW）
│   │   └── agent_client_template.md
│   ├── workflows/                    # 工作流文档（NEW）
│   │   └── tool_development_guide.md
│   ├── skill_registry.json            # 技能注册表
│   └── task.md                     # 任务跟踪（可选）
└── scripts/
    ├── discover_skills.py            # 技能发现工具（已增强）
    └── create_tool.py              # 工具生成脚本（NEW）
```

---

## 工具类型体系

### 类型 1：Subprocess 工具

**适用场景**：简单的命令行工具，不需要 MCP 协议

**代表工具**：
- yt-dlp-tool
- news-aggregator-tool
- imgconv-tool

**特征**：
- 有 `main.py` 作为核心实现
- 使用 `subprocess.run()` 执行
- 无 MCP 服务器
- 简单的 CLI 接口

**实现模式**：
```python
# agent_client.py
INTEGRATION_TYPE = "subprocess"

def run_tool(**kwargs):
    cmd = [python_exe, TOOL_SCRIPT]
    result = subprocess.run(cmd, ...)
    return result
```

---

### 类型 2：MCP 服务器工具

**适用场景**：需要与 AI 助手深度集成的工具

**代表工具**：
- playwright-tool（本地 MCP）
- trendradar-tool（外部 MCP）

**特征**：
- 有 `mcp_server.py` 实现 MCP 协议
- 使用 `mcp_client.py` 统一客户端
- 提供 10+ 标准化工具
- 异步执行

**实现模式**：
```python
# agent_client.py
INTEGRATION_TYPE = "mcp"

from mcp_client import create_mcp_client

client = create_mcp_client(
    server_path="mcp_server.py",
    server_name="my-tool-mcp",
    is_external=False  # True for external MCP like TrendRadar
)

async def run_tool(action: str, **kwargs):
    result = await client.call_tool(action, **kwargs)
    return result
```

**MCP 服务器实现**：
```python
# mcp_server.py
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

---

### 类型 3：元技能

**适用场景**：提供指导而非执行的技能

**代表工具**：
- literature-search-expert
- mcp-builder-expert
- tool-development-expert

**特征**：
- 无 `main.py` 或 `mcp_server.py`
- 仅显示 `SKILL.md` 内容
- 统一 agent.py 处理路由和显示

**实现模式**：
```python
# agent_client.py（简化）
INTEGRATION_TYPE = "meta"

def main():
    # 统一 agent.py 会自动显示 SKILL.md
    print(load_skill_context())
```

---

## 统一 MCP 客户端 (mcp_client.py)

### 功能

`mcp_client.py` 提供了统一的 MCP 集成接口：

```python
class MCPClient:
    """统一的 MCP 客户端"""

    async def call_tool(self, tool_name: str, **kwargs) -> str:
        """调用 MCP 工具"""

    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有可用工具"""

    def call_tool_sync(self, tool_name: str, **kwargs) -> str:
        """同步包装器"""
```

### 使用示例

**本地 MCP 服务器：**
```python
from mcp_client import create_mcp_client

client = create_mcp_client(
    server_path="mcp_server.py",
    server_name="my-tool-mcp",
    is_external=False
)

result = client.call_tool_sync("tool_name", param="value")
```

**外部 MCP 服务器（TrendRadar）：**
```python
client = create_mcp_client(
    server_path="~/TrendRadar/mcp_server/server.py",
    server_name="trendradar-mcp",
    is_external=True
)

result = client.call_tool_sync("get_latest_news", limit=50)
```

---

## 模板系统

### agent_client_template.md

位置：`.agent/templates/agent_client_template.md`

**功能**：
- 支持所有三种工具类型
- 占位符系统：`{{TOOL_NAME}}`, `{{INTEGRATION_TYPE}}` 等
- 预生成的代码结构
- 详细的填空指南

**支持的配置：**
- subprocess 工具的完整实现
- MCP 工具的完整实现
- 元技能的简化实现

---

## 开发工作流

### 工作流 1：使用模板创建新工具

```bash
# 1. 创建工具目录
python scripts/create_tool.py my-tool --type subprocess

# 2. 进入工具目录
cd my-tool-tool

# 3. 编辑 agent_client.py
# 已有模板，只需替换占位符

# 4. 实现核心逻辑
# subprocess: 实现 main.py
# MCP: 实现 mcp_server.py

# 5. 注册技能
cd ..
python scripts/discover_skills.py
```

### 工作流 2：增强现有工具

```bash
# 1. 更新为使用 mcp_client.py
# 复制模板并适配

# 2. 更新 requirements.txt
# 添加 mcp>=0.9.0（如果是 MCP 工具）

# 3. 测试
python agent_client.py "menu"
python agent_client.py "测试命令"
```

---

## 技能注册表增强

### 新增字段

```json
{
  "name": "skill-name-expert",
  "function_name": "skill-name",
  "type": "execution",           // "execution" | "meta"
  "integration": "subprocess",   // "subprocess" | "mcp" | "none"
  "has_main": true,              // 新字段
  "has_mcp_server": false,       // 新字段
  "is_external": false,           // 新字段（仅用于 external MCP）
  "tool_dir": "{skill-name}-tool",
  "description": "...",
  "status": "active",
  "path": "/path/to/skill",
  "skill_md": "/path/to/SKILL.md"
}
```

### 字段说明

| 字段 | 说明 | 值 |
|------|------|-----|
| `integration` | 集成方式 | subprocess, mcp, none |
| `has_main` | 是否有 main.py | true, false |
| `has_mcp_server` | 是否有 mcp_server.py | true, false |
| `is_external` | 是否为外部 MCP | true, false |

---

## 文档更新

### AGENTS.md 新增内容

已添加 `MCP Integration Patterns` 部分，包括：

1. **工具类型定义**：subprocess, MCP 服务器, 元技能
2. **每种类型的实现模式**
3. **正确的 MCP 集成方式**
4. **反模式（不要做什么）**

---

## 迁移指南

### 迁移现有工具到新架构

**步骤 1：识别工具类型**
- 检查是否有 `main.py` → subprocess 工具
- 检查是否有 `mcp_server.py` → MCP 工具
- 都没有 → 元技能

**步骤 2：使用模板**
```bash
# 从模板创建新的 agent_client.py
cp .agent/templates/agent_client_template.md {tool}-tool/agent_client.py
```

**步骤 3：适配占位符**
- 替换 `{{TOOL_NAME}}` 为实际工具名
- 设置 `{{INTEGRATION_TYPE}}` 为正确类型
- 实现/移除特定功能的代码

**步骤 4：测试和验证**
- 运行技能发现脚本
- 测试菜单显示
- 测试工具执行

---

## 测试清单

在创建或修改工具后，请验证：

- [ ] **语法检查**：`python3 -m py_compile agent_client.py`
- [ ] **导入检查**：`python3 -c "from mcp_client import create_mcp_client"`
- [ ] **菜单显示**：`python agent_client.py "menu"` 正常工作
- [ ] **直接操作**：`python agent_client.py --action test` 工作（如适用）
- [ ] **技能注册**：`python scripts/discover_skills.py` 包含新技能
- [ ] **文档完整**：`README.md` 已更新
- [ ] **依赖完整**：所有依赖在 `requirements.txt` 中
- [ ] **错误处理**：所有外部调用都有 try-except 块

---

## 依赖关系

### MCP 工具依赖

```txt
# requirements.txt for MCP tools
requests>=2.32.5,<3.0.0
mcp>=0.9.0
# ... 其他依赖
```

### Subprocess 工具依赖

```txt
# requirements.txt for subprocess tools
requests>=2.32.5,<3.0.0
# ... 其他依赖
```

---

## 常见问题和解决方案

### 问题 1：ImportError for mcp_client

**错误**：`ModuleNotFoundError: No module named 'mcp_client'`

**原因**：没有将父目录添加到 sys.path

**解决**：
```python
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_client import create_mcp_client
```

### 问题 2：MCP server not found

**错误**：`MCP server not found at: ...`

**原因**：MCP 服务器路径不正确或未安装

**解决**：运行安装脚本或创建符号链接
```bash
# 对于外部 MCP（如 TrendRadar）
git clone https://github.com/sansan0/TrendRadar.git ~/TrendRadar
cd trendradar-tool
ln -s ~/TrendRadar/mcp_server trendradar-mcp
```

### 问题 3：错误的 MCP 集成模式

**错误**：`from agent import call_mcp_tool`

**原因**：假设了不存在的统一 MCP 客户端

**解决**：使用新的 `mcp_client.py`
```python
# ❌ 错误
from agent import call_mcp_tool

# ✅ 正确
from mcp_client import create_mcp_client

client = create_mcp_client(
    server_path="mcp_server.py",
    server_name="my-tool-mcp"
)
```

---

## 架构优势

### 1. 统一性

所有 MCP 工具使用相同的客户端实现：
- 代码复用
- 统一错误处理
- 一致的 API

### 2. 可维护性

清晰的目录结构和模板：
- 新开发者容易理解
- 减少重复代码
- 文档即模板

### 3. 可扩展性

工具类型系统允许轻松添加新类型：
- 当前支持：subprocess, MCP, meta
- 未来可扩展：如 gRPC, WebSocket 等

### 4. 标准化

所有工具遵循相同的规范：
- 命名约定
- 代码结构
- 文档格式

---

## 文件清单

### 已创建/更新的文件

| 文件 | 路径 | 说明 |
|------|------|------|
| `mcp_client.py` | `/mcp_client.py` | 统一 MCP 客户端 |
| `agent_client_template.md` | `/.agent/templates/agent_client_template.md` | agent_client.py 模板 |
| `tool_development_guide.md` | `/.agent/workflows/tool_development_guide.md` | 工具开发指南 |
| `discover_skills.py` | `/scripts/discover_skills.py` | 技能发现（已增强） |
| `create_tool.py` | `/scripts/create_tool.py` | 工具生成脚本（新） |
| `AGENTS.md` | `/AGENTS.md` | 主文档（已更新） |

### 已修复的文件

| 文件 | 路径 | 修复内容 |
|------|------|--------|
| `agent_client.py` | `/trendradar-tool/agent_client.py` | 使用正确的 MCP 集成 |
| `requirements.txt` | `/trendradar-tool/requirements.txt` | 添加 mcp>=0.9.0 |

---

## 使用示例

### 创建新的 subprocess 工具

```bash
# 1. 生成工具脚手架
python scripts/create_tool.py my-video-tool --type subprocess \
    --description "视频下载工具"

# 2. 实现核心逻辑
cd my-video-tool
# 编辑 main.py 实现你的工具逻辑

# 3. 注册技能
cd ..
python scripts/discover_skills.py

# 4. 测试
cd my-video-tool
python agent_client.py "menu"
```

### 创建新的 MCP 工具

```bash
# 1. 生成工具脚手架
python scripts/create_tool.py my-automation-tool --type mcp \
    --description "浏览器自动化工具"

# 2. 实现 MCP 服务器
cd my-automation-tool
# 编辑 mcp_server.py 实现 MCP 工具

# 3. 注册技能
cd ..
python scripts/discover_skills.py

# 4. 测试
cd my-automation-tool
python agent_client.py "menu"
```

### 迁移现有工具

```bash
# 示例：迁移某个工具到新的 MCP 架构
cd existing-tool

# 1. 从模板创建新的 agent_client.py
cp ../.agent/templates/agent_client_template.md agent_client.py

# 2. 适配占位符
# 编辑 agent_client.py，设置 TOOL_NAME, INTEGRATION_TYPE 等

# 3. 实现或调整 MCP 集成
# 根据工具类型实现

# 4. 更新 requirements.txt
# 添加 mcp>=0.9.0（如需要）

# 5. 测试
python agent_client.py "menu"
```

---

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                  统一 agent.py (路由器)              │
│                                                       │
│  ┌──────────────────┬──────────────────────┐         │
│  │                  │                  │           │
│  ▼                  ▼                  ▼           │
│ ┌─────────┐     ┌──────────┐    ┌────────┐  │
│ │ Subprocess│    │MCP Server │    │ Meta    │  │
│ │  工具    │    │   工具    │    │ 技能    │  │
│ └────┬────┘    └──────┬─────┘    └────────┘  │
│      │                  │                      │     │
│      ▼                  ▼                      │     │
│ ┌─────────┐     ┌────────────────────────┐       │
│ │ mcp_client.py    │  mcp_client.py       │       │
│ │ (统一客户端)   │  (统一客户端)         │       │
│ └────┬──────┘    └──────┬─────────┘       │
│      │                        │                  │     │
│      ▼                        ▼                  │     │
│ ┌────────────┐        ┌──────────────┐             │
│ │MCP Server 1│        │MCP Server 2  │ (外部)    │
│ │(本地,如     │        │(外部,如     │             │
│ │playwright)  │        │TrendRadar)   │             │
│ └────────────┘        └──────────────┘             │
└───────────────────────────────────────────────────────┘
```

---

## 未来扩展

### 可能的增强

1. **工具生成器**：完整的 CLI 工具
   - 自动生成 main.py
   - 自动生成 agent_client.py
   - 自动生成测试

2. **配置管理**：统一配置系统
   - 全局配置文件
   - 工具特定配置
   - 环境变量支持

3. **插件系统**：动态工具加载
   - 运行时加载工具
   - 热重载
   - 依赖管理

4. **日志系统**：标准化日志
   - 统一日志格式
   - 日志级别控制
   - 日志聚合

---

## 总结

这个统一 MCP 架构提供了：

✅ **统一的 MCP 集成**：所有工具使用相同的客户端模式
✅ **标准化的开发流程**：从创建到测试的完整工作流
✅ **清晰的文档体系**：模板、指南、参考文档
✅ **类型系统**：三种工具类型，明确的实现指导
✅ **错误预防**：通过标准化避免常见错误
✅ **可扩展性**：支持未来工具类型的添加

### 核心成果

1. **mcp_client.py**：统一的 MCP 客户端实现
2. **模板系统**：标准化的代码生成模板
3. **开发指南**：完整的工具开发工作流
4. **增强的脚本**：技能发现和工具生成
5. **更新的文档**：AGENTS.md 包含 MCP 集成模式

---

**文档版本**：1.0
**最后更新**：2025-01-25
