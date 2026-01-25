# 🎭 Playwright Tool

完整的 Playwright 浏览器自动化工具，支持 CLI 命令行和 MCP 服务器模式。

## 📦 特性

- ✅ **多浏览器支持**：Chromium、Firefox、WebKit
- 🚀 **MCP 集成**：可作为 MCP 服务器与 AI 助手集成
- 🎯 **丰富工具集**：导航、截图、内容提取、表单填写、点击、等待、JavaScript 执行
- 📝 **脚本模板**：支持命令行模板，简化常用操作
- 🔐 **安全性**：完整隔离、Trusted Events、Shadow DOM 穿透

## 📂 安装

### 前置要求
```bash
# 安装 Playwright 和 Python MCP 依赖
pip install playwright mcp
```

### 安装浏览器（可选）
```bash
# 安装所有支持的浏览器
npx playwright install chromium firefox webkit
# 或只安装特定浏览器
npx playwright install chromium
```

## 🚀 快速开始

### 模式 1：CLI 命令行（直接操作）

```bash
# 启动浏览器
python main.py launch --browser chromium --headless true

# 导航到 URL
python main.py navigate https://example.com

# 截图
python main.py screenshot --path screenshot.png

# 获取页面文本
python main.py navigate https://example.com --get-text
```

### 模式 2：MCP 服务器（AI 集成）

```bash
# 启动 MCP 服务器（推荐用于 AI 助手）
python main.py mcp-server --browser chromium --headless true --port 3000

# MCP 服务器会在 http://localhost:3000 上启动
# 在 Claude Desktop 或其他支持 MCP 的 AI 助手中配置此服务器
```

## 📋 命令参考

### 浏览器控制
```bash
# 启动浏览器
python main.py launch --browser chromium --headless false --timeout 60000

# 关闭浏览器
python main.py close

# 设置视口
python main.py viewport --width 1920 --height 1080
```

### 页面操作
```bash
# 导航并等待加载完成
python main.py navigate https://example.com --wait-until domcontentloaded --timeout 30000

# 截取页面标题
python main.py navigate https://github.com --get-text '{"selector": "h1"}'

# 截图
python main.py screenshot --full-page --path full_page.png

# 点击元素
python main.py navigate https://example.com/login --click '{"selector": "#submit-button"}'

# 填写表单
python main.py navigate https://example.com/login \
  --fill '{"selector": "#username", "value": "admin"}' \
  --fill '{"selector": "#password", "value": "password123"}'

# 类型文本
python main.py navigate https://example.com --type-text \
  '{"selector": "#search-box", "text": "Playwright"}'

# 等待元素出现
python main.py navigate https://example.com \
  --wait '{"selector": "#result", "state": "visible", "timeout": 10000}'

# 执行 JavaScript
python main.py evaluate "document.title"

# 获取所有链接
python main.py navigate https://example.com --get-links
```

### 高级功能
```bash
# 结构化数据提取（使用 JSON schema）
python main.py scrape '{
  "title": {"selector": "h1", "field_name": "text"},
  "price": {"selector": ".price", "field_name": "text"}
}'

# 批量操作
python main.py batch operations.json

# 运行测试
python main.py test tests/login.spec.ts

# 查看命令模板
python main.py templates
```

## 🎨 MCP 工具列表

当作为 MCP 服务器运行时，提供以下工具：

### 浏览器生命周期
- `browser_launch` - 启动浏览器实例
- `browser_close` - 关闭浏览器

### 导航和操作
- `browser_navigate` - 导航到 URL
- `page_screenshot` - 截取页面截图
- `page_get_text` - 提取页面文本
- `page_get_html` - 提取 HTML 内容
- `page_click` - 点击元素
- `page_fill` - 填写表单字段
- `page_type_text` - 类型文本到输入框
- `page_wait_for_selector` - 等待元素出现
- `page_evaluate` - 执行 JavaScript 代码
- `page_get_links` - 获取所有链接
- `page_get_info` - 获取页面信息
- `set_viewport` - 设置视口大小
- `execute_script` - 执行自定义 JavaScript
- `page_scrape` - 结构化数据提取（JSON schema）

### Agent 客户端集成

使用 `agent_client.py` 与 LLM 集成：

```bash
python agent_client.py "打开 GitHub 并截图" --llm-url http://localhost:1234/v1/chat/completions
```

支持中文自然语言指令：
- "帮我打开 github.com 并截图"
- "获取页面标题"
- "填写这个表单"
- "点击提交按钮"

## 📂 目录结构

```
playwright-tool/
├── main.py              # 主入口点
├── mcp_server.py         # MCP 服务器实现
├── agent_client.py        # LLM 集成客户端（可选）
├── templates.md           # 命令模板
├── requirements.txt       # Python 依赖
├── scripts/             # 可选脚本目录
└── README.md             # 本文件
```

## 🔧 技术细节

### MCP 协议实现
- 使用 `mcp.server` SDK 构建
- 标准化工具定义，符合 MCP 规范
- 异步处理所有浏览器操作
- 自动资源管理和清理

### 浏览器支持
- **Chromium**: 完整支持，当前版本 1.48.0
- **Firefox**: 完整支持，当前版本 1.48.0
- **WebKit**: 完整支持，当前版本 1.48.0

### 特性
- **Headless 模式**：所有浏览器支持
- **并发上下文**：支持多个独立页面上下文
- **Trusted Events**：真实浏览器输入管道
- **自动等待**：智能等待机制，减少不稳定性测试
- **Shadow DOM 穿透**：无缝访问 Shadow DOM 元素
- **视口控制**：自定义屏幕尺寸

## 📊 与现有工具集成

这个工具可以与您项目中其他工具集成使用：

```bash
# 与 news-aggregator-tool 一起使用
python news-aggregator-tool/agent_client.py "获取 GitHub 热门项目"
python playwright-tool/agent_client.py "截图保存结果"

# 作为 subprocess 调用
cd playwright-tool && python main.py navigate https://example.com --get-text
```

## 🛡 故障排除

### 常见问题

**1. 浏览器未安装**
```bash
# 安装浏览器
npx playwright install chromium
```

**2. MCP 模块未安装**
```bash
pip install mcp
```

**3. 端口被占用**
```bash
# 使用不同端口
python main.py mcp-server --port 3001
```

**4. 元素未找到**
```bash
# 使用更长的超时时间
python main.py navigate https://example.com --timeout 60000
```

## 📝 注意事项

- **性能优化**：重用浏览器上下文，避免重复启动
- **安全考虑**：不要在命令行中传递敏感信息
- **错误处理**：所有命令都返回 JSON 格式结果，便于自动化处理
- **调试模式**：检查浏览器开发者工具查看详细日志

## 📄 License

Apache-2.0 License

---

**💡 提示**：
- 使用 `templates` 命令查看所有可用模板
- 支持批量操作，提高效率
- MCP 模式需要 `mcp` Python 包
