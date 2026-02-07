# Monty Integration Guide

## 概述

本指南说明如何将新的技能集成到 Monty 外部函数系统，使 AI 可以在 Monty 代码中调用这些技能。

## 快速开始

### 1. 检查技能类型

首先确定您的技能类型：

- **执行技能** (Execution Skills): 需要集成 ✅
  - 有 main.py 或 mcp_server.py
  - 执行实际任务（下载、处理等）
  - 例如：news-aggregator, pdf-downloader, imgconv, yt-dlp, paper-audit

- **元技能** (Meta Skills): 不需要集成 ⏭️
  - 仅提供指导文档
  - 没有执行代码
  - 例如：mcp-builder-expert, literature-search-expert, frontend-design-expert

### 2. 外部函数位置

所有外部函数定义在：
```
.agent/skills/monty-expert/tool/external_functions.py
```

## 集成步骤

### Step 1: 编写外部函数

在 `external_functions.py` 中添加新函数，使用 `@register_external_function` 装饰器：

```python
@register_external_function("my_skill_function")
def my_skill_function(param1: str, param2: int = 10) -> dict:
    """
    函数描述（AI 会读取这个）
    
    Args:
        param1: 参数1描述
        param2: 参数2描述（可选，默认值）
    
    Returns:
        返回值描述
    """
    from pathlib import Path
    import subprocess
    import sys
    import json
    
    # 1. 定位工具目录
    tool_dir = Path(__file__).parent.parent.parent / "my-skill-expert" / "tool"
    main_py = tool_dir / "main.py"
    
    if not main_py.exists():
        return {"error": f"Tool not found at {main_py}"}
    
    # 2. 构建命令
    cmd = [sys.executable, str(main_py)]
    # 添加命令行参数...
    
    try:
        # 3. 执行工具
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return {"error": result.stderr}
        
        # 4. 解析返回结果
        return json.loads(result.stdout)
        
    except subprocess.TimeoutExpired:
        return {"error": "Timeout executing tool"}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse output: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}
```

### Step 2: 测试函数

```bash
# 1. 列出所有外部函数（确认已注册）
python .agent/skills/monty-expert/tool/main.py --list-external-funcs | grep my_skill

# 2. 测试函数执行
python .agent/skills/monty-expert/tool/main.py \
  --use-external-funcs \
  --code 'result = my_skill_function("value", 20); print(result)'
```

### Step 3: 更新文档

更新以下文档：

1. **AGENTS.md** - 添加到集成表格：
   ```markdown
   | `my-skill-expert` | `.agent/skills/my-skill-expert/tool/` | 描述 | ✅ Integrated | 2 |
   ```

2. **MONTY_INTEGRATION_SUMMARY.md** - 更新：
   - "Existing Tools Integrated" 部分
   - "Priority 2" 部分（如果是新技能）

## 集成模式

### 模式 1: Subprocess 工具（最常见）

适用于简单的 CLI 工具：

```python
@register_external_function("download_file")
def download_file(url: str) -> str:
    """Download file from URL."""
    from pathlib import Path
    
    tool_dir = Path(__file__).parent.parent.parent / "downloader-expert" / "tool"
    main_py = tool_dir / "main.py"
    
    cmd = [sys.executable, str(main_py), url]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: Timeout"
```

### 模式 2: MCP 服务器

适用于复杂的 MCP 工具（如 playwright）：

```python
@register_external_function("web_scrape")
def web_scrape(url: str, selector: str = None) -> dict:
    """Scrape web content using Playwright MCP."""
    from pathlib import Path
    import sys
    
    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"
    
    if not mcp_server_path.exists():
        return {"error": "MCP server not found"}
    
    # 添加路径
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    try:
        from mcp_client import MCPClient
        
        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False
        )
        
        # 调用 MCP 工具
        result = client.call_tool_sync("navigate", url=url)
        
        if selector:
            result = client.call_tool_sync("get_text", selector=selector)
        
        return {"result": result}
        
    except Exception as e:
        return {"error": f"MCP call failed: {e}"}
```

### 模式 3: 临时文件处理

适用于需要文件输入的工具：

```python
@register_external_function("analyze_text")
def analyze_text(content: str, mode: str = "standard") -> dict:
    """Analyze text content."""
    from pathlib import Path
    import tempfile
    import json
    import os
    
    tool_dir = Path(__file__).parent.parent.parent / "analyzer-expert" / "tool"
    main_py = tool_dir / "main.py"
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        cmd = [sys.executable, str(main_py), "--mode", mode, "--file", temp_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return {"error": result.stderr}
        
        return json.loads(result.stdout)
        
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_path)
        except:
            pass
```

## 常见问题排查

### 问题 1: 函数未显示在列表中

**症状**：
```bash
python .agent/skills/monty-expert/tool/main.py --list-external-funcs | grep my_func
# 没有输出
```

**原因**：
- 忘记使用 `@register_external_function` 装饰器
- 函数名拼写错误

**解决**：
```python
# 错误 ❌
def my_function():
    pass

# 正确 ✅
@register_external_function("my_function")
def my_function():
    pass
```

### 问题 2: 工具未找到

**症状**：
```python
{"error": "Tool not found at /path/to/tool"}
```

**原因**：
- 路径错误
- 技能目录名称不匹配

**解决**：
```python
# 检查实际路径
from pathlib import Path

# 打印路径调试
print(Path(__file__).parent.parent)
# 应该是: /path/to/systematic-skills/.agent/skills

# 确认技能目录名称
tool_dir = Path(__file__).parent.parent.parent / "my-skill-expert" / "tool"
# 注意: 是 "my-skill-expert" 不是 "my_skill_expert"
```

### 问题 3: 解析 JSON 失败

**症状**：
```python
{"error": "Failed to parse output: Expecting value: line 1 column 1 (char 0)"}
```

**原因**：
- 工具输出不是 JSON 格式
- 工具输出包含非 JSON 文本

**解决**：
```python
# 方案 1: 先输出，再解析
result = subprocess.run(cmd, capture_output=True, text=True)
print("Raw output:", result.stdout)  # 调试输出

# 方案 2: 提取 JSON 部分
output = result.stdout.strip()
if output.startswith("{") or output.startswith("["):
    return json.loads(output)
else:
    # 尝试从输出中提取 JSON
    import re
    json_match = re.search(r'\{.*\}', output)
    if json_match:
        return json.loads(json_match.group())
```

### 问题 4: 超时错误

**症状**：
```python
{"error": "Timeout executing tool"}
```

**原因**：
- 超时时间设置太短
- 工具执行时间过长

**解决**：
```python
# 根据实际执行时间调整 timeout
result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5分钟
```

### 问题 5: 参数传递错误

**症状**：
```python
{"error": "Tool returned non-zero exit status 2"}
```

**原因**：
- 命令行参数顺序错误
- 参数类型不匹配

**解决**：
```python
# 1. 确认工具的实际参数格式
# 先手动运行工具测试
python /path/to/tool/main.py --help

# 2. 构建正确的命令
cmd = [sys.executable, str(main_py)]

# 添加参数（注意格式）
cmd.extend(["--input", input_path])  # ❌ 错误
cmd.extend(["--output", str(output_path)])  # ✅ 正确（转换路径为字符串）
cmd.extend(["--format", "jpeg"])
cmd.extend(["--quality", "90"])

# 3. 打印命令调试
print("Executing:", " ".join(cmd))
```

## 最佳实践

### 1. 错误处理

始终捕获所有可能的异常：

```python
try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode != 0:
        return {
            "error": result.stderr,
            "exit_code": result.returncode
        }
    
    return json.loads(result.stdout)
    
except subprocess.TimeoutExpired:
    return {"error": "Timeout", "command": str(cmd)}
except json.JSONDecodeError as e:
    return {"error": f"JSON parse error: {e}", "raw_output": result.stdout}
except FileNotFoundError:
    return {"error": f"Tool not found: {main_py}"}
except Exception as e:
    return {"error": f"Unexpected error: {e}", "type": type(e).__name__}
```

### 2. 类型提示

使用类型提示提高代码可读性：

```python
from typing import Dict, Optional, List

@register_external_function("search_documents")
def search_documents(query: str, limit: int = 10, filters: Dict = None) -> List[Dict]:
    """Search documents with optional filters."""
    if filters is None:
        filters = {}
    # ...
```

### 3. 文档字符串

提供清晰的文档字符串：

```python
@register_external_function("process_data")
def process_data(input_data: str, mode: str = "fast") -> dict:
    """
    Process input data with specified mode.
    
    Args:
        input_data: Raw input string to process
        mode: Processing mode ("fast" | "accurate" | "deep")
              - fast: Quick processing (default)
              - accurate: High accuracy, slower
              - deep: Deep analysis, slowest
    
    Returns:
        Dictionary with:
        - result: Processed data
        - metrics: Processing metrics (time, memory)
        - warnings: List of warnings (if any)
    
    Example:
        >>> process_data("sample data", mode="accurate")
        {"result": "...", "metrics": {...}}
    """
    # ...
```

### 4. 资源清理

使用 try/finally 确保资源清理：

```python
@register_external_function("create_temp_file")
def create_temp_file(content: str) -> str:
    """Create temporary file with content."""
    import tempfile
    import os
    
    temp_file = None
    
    try:
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        # 发生错误时清理文件
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        return {"error": f"Failed to create temp file: {e}"}
```

## 检查清单

集成新技能前，检查以下项目：

- [ ] 技能是执行技能（不是元技能）
- [ ] 技能有 main.py 或 mcp_server.py
- [ ] 使用 `@register_external_function` 装饰器
- [ ] 函数名使用 snake_case
- [ ] 提供清晰的文档字符串
- [ ] 处理所有可能的异常
- [ ] 设置合适的超时时间
- [ ] 清理临时资源
- [ ] 测试函数已注册：`--list-external-funcs`
- [ ] 测试函数执行：`--use-external-funcs`
- [ ] 更新 AGENTS.md
- [ ] 更新 MONTY_INTEGRATION_SUMMARY.md

## 示例：完整集成

以 "email-sender-expert" 为例：

### 1. 创建外部函数

```python
# .agent/skills/monty-expert/tool/external_functions.py

@register_external_function("send_email")
def send_email(to: str, subject: str, body: str, html: bool = False) -> dict:
    """
    Send email via email-sender tool.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        html: Whether body is HTML (default: False)
    
    Returns:
        Dictionary with status and message ID
    """
    from pathlib import Path
    import subprocess
    import sys
    import json
    
    tool_dir = Path(__file__).parent.parent.parent / "email-sender-expert" / "tool"
    main_py = tool_dir / "main.py"
    
    if not main_py.exists():
        return {"error": f"Email sender tool not found at {main_py}"}
    
    cmd = [sys.executable, str(main_py)]
    cmd.extend(["--to", to])
    cmd.extend(["--subject", subject])
    cmd.extend(["--body", body])
    if html:
        cmd.append("--html")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return {"error": result.stderr}
        
        output = result.stdout.strip()
        if "Sent:" in output:
            msg_id = output.split("Sent:")[-1].strip()
            return {"status": "success", "message_id": msg_id}
        else:
            return {"status": "success", "output": output}
            
    except subprocess.TimeoutExpired:
        return {"error": "Timeout sending email"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}
```

### 2. 测试集成

```bash
# 列出函数
python .agent/skills/monty-expert/tool/main.py --list-external-funcs | grep send_email

# 测试发送
python .agent/skills/monty-expert/tool/main.py \
  --use-external-funcs \
  --code 'result = send_email("test@example.com", "Test", "Hello World"); print(result)'
```

### 3. 更新文档

AGENTS.md:
```markdown
| `email-sender-expert` | `.agent/skills/email-sender-expert/tool/` | Email sending tool | ✅ Integrated | 1 |
```

MONTY_INTEGRATION_SUMMARY.md:
```markdown
- ✅ email-sender-expert → `send_email()` (1 function)
```

## 参考资源

- Monty 文档: `.agent/skills/monty-expert/SKILL.md`
- 开发标准: `.agent/skills/tool-development-expert/SKILL.md` Section 3.3
- 工具集成示例: `.agent/skills/monty-expert/tool/external_functions.py`
- 代码模板: `.agent/skills/monty-expert/tool/templates.md`

---

**最后更新**: 2026-02-07
**当前版本**: 15 外部函数 / 5 执行技能
