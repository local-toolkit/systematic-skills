---
name: monty-expert
version: 2026.02.07
description: Python code execution interpreter with 29+ integrated external functions (news, PDF, image, video, paper audit, playwright, utility). Use for writing Python code, multi-step data processing, complex logic combining multiple APIs, calculations, data transformations, or when user needs programmatic control.
status: active
type: execution
---

# Monty Python Interpreter Expert

Secure, minimal Python interpreter written in Rust for AI code execution.

## What is Monty?

A minimal, secure Python interpreter written in Rust for use by AI. Monty avoids the cost, latency, complexity of full container-based sandboxes.

**Key advantages:**
- **Ultra-fast startup**: <1ms vs Docker ~200ms
- **Secure sandbox**: No filesystem/network/env access unless explicitly allowed
- **Designed for AI**: Run code written by LLMs safely
- **Resource controlled**: Memory, time, and stack depth limits

## Core Features

### ✅ What Monty CAN do:
- Run a reasonable subset of Python code (enough for agents to express logic)
- Call functions on the host (only functions you give it access to)
- Run type checking (supports full modern Python type hints with `ty`)
- Be snapshotted to bytes at external function calls (store/restore interpreter state)
- Startup extremely fast (<1μs to go from code to execution result)
- Be called from Rust, Python, or JavaScript
- Control resource usage (track memory, allocations, stack depth, execution time)
- Collect stdout and stderr and return to caller
- Run async or sync code on the host

### ❌ What Monty CANNOT do:
- Use the standard library (except: `sys`, `typing`, `asyncio`)
- Use third-party libraries (like Pydantic, numpy, pandas)
- Define classes (support coming soon)
- Use match statements (support coming soon)

## Usage Patterns

### Pattern 1: Basic Execution

Simple one-shot code execution:

```bash
# Direct execution
python tools/monty-executor-tool/agent_client.py --code 'x = 42; print(x)'

# With inputs
python tools/monty-executor-tool/agent_client.py --code 'result = sum(inputs["data"]); result' --inputs '{"data": [1,2,3,4,5]}'

# From file
python tools/monty-executor-tool/agent_client.py --file script.py
```

### Pattern 2: Iterative Execution with External Functions

Use `start()` and `resume()` to handle external function calls iteratively:

```python
code = """
data = fetch_news(source="hackernews", limit=5)
print(f"Fetched {len(data)} items")
"""

# This will call fetch_news() external function
```

### Pattern 3: State Serialization

Both `Monty` and `MontySnapshot` can be serialized to bytes and restored:

```python
# Serialize parsed code
m = pydantic_monty.Monty('x + 1', inputs=['x'])
data = m.dump()

# Later, restore and run
m2 = pydantic_monty.Monty.load(data)
print(m2.run(inputs={'x': 41}))  # 42
```

## When to Use Monty vs Traditional Tools

### ✅ Use Monty for:
1. **Complex multi-step data processing** - multiple data transformations/calculations
2. **Combining multiple tools/APIs** - need to compose results from different sources
3. **Fast response required** - <1ms startup is critical
4. **Conditional logic** - AI needs to express branching/logic
5. **Looping/iteration** - processing lists or repeating operations
6. **Data aggregation** - collecting and summarizing from multiple sources

**Example**: "Analyze Hacker News AI articles, extract keywords, and generate summary"

### ❌ Use traditional tools for:
1. **Simple single-step operations** - e.g., "download this video" → yt-dlp-tool
2. **Need full Python stdlib** - file I/O, networking, complex data structures
3. **Need third-party libraries** - numpy, pandas, scikit-learn
4. **Direct API calls** - simple fetch/store operations

**Example**: "下载这个视频 https://example.com/video.mp4" → yt-dlp-expert

## External Functions Integration

Monty allows calling host functions for operations it cannot do itself (network, file I/O).

### Available External Functions

#### News Aggregation Functions
- `fetch_news(source, limit, keyword)` - Fetch news from aggregator tool
- `fetch_hackernews(limit, keyword)` - Fetch Hacker News
- `fetch_weibo(limit, keyword)` - Fetch Weibo trending
- `fetch_github_trending(limit, keyword)` - Fetch GitHub trending

#### PDF/Document Functions
- `download_pdf(url)` - Download PDF to paper_audit/inbox
- `read_file(path)` - Read file contents (restricted paths)
- `write_file(path, content)` - Write file (restricted paths)

#### Media Functions
- `convert_image(input_path, output_path, format)` - Convert image format
- `download_video(url, format)` - Download video with yt-dlp

#### Utility Functions
- `print(*args)` - Print to stdout
- `len(obj)` - Get length
- `type(obj)` - Get type

### Using External Functions

```python
# Basic usage
news = fetch_news(source="hackernews", limit=10)
print(f"Fetched {len(news)} items")

# Complex pipeline
ai_news = fetch_news("hackernews", 20, "AI")
pdf_urls = [item['url'] for item in ai_news if item['url'].endswith('.pdf')]
pdfs = [download_pdf(url) for url in pdf_urls[:3]]
return {"downloaded": len(pdfs), "paths": pdfs}
```

## Code Templates

### Template 1: News Analysis
```python
# Fetch AI news
news = fetch_news(source="hackernews", limit=20, keyword="AI")

# Analyze and summarize
ai_news = [item for item in news if 'AI' in item['title']]

# Group by source or keyword
for item in ai_news[:5]:
    print(f"• {item['title']}")
    print(f"  URL: {item['url']}\n")

return {"count": len(ai_news), "top": ai_news[:5]}
```

### Template 2: PDF Batch Processing
```python
# PDF URLs to download
pdf_urls = [
    "https://arxiv.org/pdf/2301.07041.pdf",
    "https://arxiv.org/pdf/2302.04761.pdf"
]

# Download all PDFs
downloaded_paths = []
for url in pdf_urls:
    try:
        path = download_pdf(url)
        downloaded_paths.append(path)
    except Exception as e:
        print(f"Failed to download {url}: {e}")

return {"downloaded": len(downloaded_paths), "paths": downloaded_paths}
```

### Template 3: Data Pipeline
```python
# Fetch news
tech_news = fetch_news("hackernews", limit=10, keyword="AI")

# Download relevant PDFs
pdf_urls = [item['url'] for item in tech_news if item['url'].endswith('.pdf')]
pdf_paths = [download_pdf(url) for url in pdf_urls[:3]]

# Read and analyze
summaries = []
for path in pdf_paths:
    content = read_file(path)
    summaries.append({
        "path": path,
        "length": len(content),
        "preview": content[:100]
    })

return {"processed": len(summaries), "summaries": summaries}
```

## Security Features

- **No filesystem access** - unless via external functions
- **No network access** - unless via external functions
- **No environment variables** - isolated from host
- **Resource limits** - memory, time, stack depth controlled
- **Type safety** - optional type checking with `ty`

## Performance

- **Startup time**: <1μs
- **Runtime**: Similar to CPython (generally 5x faster to 5x slower)
- **Memory**: ~4.5MB package size
- **Comparison**:
  - Monty: ~0.06ms startup
  - Docker: ~195ms startup
  - Pyodide: ~2800ms startup

## Comparison with Alternatives

| Technology | Language | Security | Startup | Cost | Setup | File Access | Snapshotting |
|------------|----------|----------|---------|------|-------|-------------|--------------|
| **Monty** | Partial | Strict | 0.06ms | Free | Easy | Controlled | Easy |
| Docker | Full | Good | 195ms | Free | Medium | Easy | Medium |
| Pyodide | Full | Poor | 2800ms | Free | Medium | Easy | Hard |
| sandboxing service | Full | Strict | 1033ms | Paid | Medium | Hard | Medium |
| YOLO Python | Full | None | 0.1-30ms | Free | Easy | Easy | Hard |

## Best Practices

1. **Keep code simple** - Monty is designed for AI-generated code snippets
2. **Use external functions** for complex operations (network, file I/O)
3. **Set timeouts** to prevent infinite loops (default: 30s)
4. **Test inputs** before execution
5. **Avoid side effects** - Monty is not for persistent state
6. **Prefer Monty** for multi-step operations vs single tool calls

## Integration with Pydantic AI

Monty powers code-mode in Pydantic AI:

```python
from pydantic_ai import Agent
from pydantic_ai.toolsets.code_mode import CodeModeToolset
from pydantic_ai.toolsets.function import FunctionToolset

toolset = FunctionToolset()

@toolset.tool
def get_weather(city: str) -> dict:
    """Get current weather for a city."""
    return {'city': city, 'temp_c': 18, 'conditions': 'partly cloudy'}

toolset = CodeModeToolset(toolset)

agent = Agent('anthropic:claude-sonnet-4-5', toolsets=[toolset])
result = agent.run_sync('Compare weather in London, Paris, and Tokyo.')
```

## CLI Usage

```bash
# Direct execution
python tools/monty-executor-tool/agent_client.py --code 'print("Hello, World!")'

# With external functions
python tools/monty-executor-tool/agent_client.py --code 'result = fetch_news("hackernews", 5); print(len(result))'

# From file
python tools/monty-executor-tool/agent_client.py --file script.py

# With inputs
python tools/monty-executor-tool/agent_client.py --code 'x + y' --inputs '{"x": 10, "y": 20}'
```

## Python API Usage

```python
import pydantic_monty

code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
fib(x)
"""

m = pydantic_monty.Monty(code, inputs=['x'])
result = m.run(inputs={'x': 10})
print(result)  # 55
```

## Installation

```bash
pip install pydantic-monty
```

## Documentation

- GitHub: https://github.com/pydantic/monty
- PyPI: https://pypi.org/project/pydantic-monty/
- Pydantic AI: https://github.com/pydantic/pydantic-ai

## Status

**Experimental** - This project is still in development. Support for classes, match statements, and more stdlib modules is coming soon.
