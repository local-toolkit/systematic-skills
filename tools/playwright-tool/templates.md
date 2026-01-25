# 🎭 Playwright Tool 命令模板

请回复序号（如 "1"）或直接复制指令来执行任务。

## 🌐 页面操作

**1. 打开网站并截图**
```bash
python main.py navigate "https://example.com" --screenshot
```

**2. 获取页面标题和文本**
```bash
python main.py navigate "https://example.com" --get-text
```

**3. 填写表单**
```bash
python main.py navigate "https://example.com/login" \
  --fill '{"selector": "#username", "value": "admin"}' \
  --fill '{"selector": "#password", "value": "password123"}'
```

## 🔍 内容提取

**4. 提取所有链接**
```bash
python main.py navigate "https://example.com" --get-links
```

**5. 提取特定元素文本**
```bash
python main.py navigate "https://example.com" --get-text '{"selector": ".title"}'
```

**6. 提取 HTML 内容**
```bash
python main.py navigate "https://example.com" --get-html '{"selector": ".content"}'
```

## 🖱️ 交互操作

**7. 点击按钮**
```bash
python main.py navigate "https://example.com" --click '{"selector": "#submit-button"}'
```

**8. 类型文本**
```bash
python main.py navigate "https://example.com" --type-text '{"selector": "#search-box", "text": "Playwright"}'
```

**9. 等待元素出现**
```bash
python main.py navigate "https://example.com" \
  --wait-for '{"selector": "#result", "state": "visible", "timeout": 10000}'
```

## 🎯 高级功能

**10. 执行 JavaScript 代码**
```bash
python main.py evaluate "document.title"
```

**11. 结构化数据提取**
```bash
python main.py scrape '{
  "page_title": {selector": "h1", field_name: "text"},
  "price": {selector": ".price", field_name: "text"},
  "description": {selector": ".description", field_name: "text"}
}'
```

**12. 设置视口大小**
```bash
python main.py set-viewport '{"width": 1920, "height": 1080}'
```

## 🐧 浏览器控制

**13. 启动浏览器**
```bash
python main.py launch --browser chromium --headless false
```

**14. 关闭浏览器**
```bash
python main.py close
```

**15. 更改视口**
```bash
python main.py set-viewport '{"width": 1280, "height": 720}'
```

## 🔧 MCP 模式

**16. 启动 MCP 服务器**
```bash
python mcp_server.py &
```

**17. 使用 agent 客户端（需要 LLM）**
```bash
python agent_client.py "帮我打开 GitHub 并截图" --llm-url http://localhost:1234/v1/chat/completions
```

## 📱 移动模拟

**18. 移动设备模拟**
```bash
python main.py navigate "https://example.com" \
  --mobile "iPhone 13 Pro" \
  --geolocation '{"latitude": 37.7749, "longitude": -122.4194}'
```

## 🕵 等待条件

**19. 等待页面加载**
```bash
python main.py navigate "https://example.com" --wait-until domcontentloaded
```

**20. 等待网络空闲**
```bash
python main.py navigate "https://example.com" --wait-until networkidle
```

## 🔒 安全操作

**21. 清除所有 Cookies**
```bash
python main.py evaluate "document.cookie.split(';').forEach(c => c = c.trim()).filter(c => c).forEach(c => document.cookie = c + ';=; expires=' + new Date(Date.now() + 86400000).toUTCString() + '; path=/')"
```

**22. 获取存储的凭据**
```bash
python main.py evaluate "JSON.stringify(localStorage)"
```

## 📊 批量操作

**23. 批量截屏多个页面**
```bash
python main.py batch '[
  {"url": "https://site1.com", "action": "screenshot"},
  {"url": "https://site2.com", "action": "screenshot"},
  {"url": "https://site3.com", "action": "screenshot"}
]'
```

**24. 批量提取数据**
```bash
python main.py batch-scrape '[
  {"url": "https://site1.com", "schema": "{...}"},
  {"url": "https://site2.com", "schema": "{...}"}
]'
```

## 🎨 测试相关

**25. 运行测试脚本**
```bash
python main.py test tests/example.spec.ts
```

**26. 生成测试代码**
```bash
python main.py codegen "tests/login.spec.ts"
```

**27. 查看追踪记录**
```bash
python main.py inspect trace.zip
```

## 💡 技巧

- **快捷命令**: 使用 `main.py` 别名或创建 shell 函数
- **环境变量**: 设置 `BROWSER_TYPE`, `HEADLESS`, `TIMEOUT` 等环境变量
- **组合操作**: 使用 JSON 参数组合多个操作
- **错误处理**: 所有命令都返回 JSON 格式的结果，便于解析
- **调试模式**: 使用 `--verbose` 标志查看详细输出

---

**💡 提示**：
- 所有返回值都是 JSON 格式
- 可以使用 `| jq` 或 `jq` 进一步处理输出
- 对于复杂操作，建议编写 Python 脚本而非直接命令行
