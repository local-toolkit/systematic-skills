"""
External Functions Registry for Monty
Provides safe host functions that Monty can call
"""

import subprocess
import sys
import json
import os
from typing import Dict, Callable, Any, List

# Registry of external functions available to Monty
import importlib.util
from pathlib import Path

# Registry of external functions available to Monty
EXTERNAL_FUNCTIONS: Dict[str, Callable] = {}


def register_external_function(name: str):
    """Decorator to register external function."""

    def decorator(func: Callable):
        EXTERNAL_FUNCTIONS[name] = func
        return func

    return decorator


# === News Aggregation Functions ===


@register_external_function("fetch_news")
def fetch_news(source: str, limit: int = 10, keyword: str = None) -> list:
    """
    Fetch news from aggregator tool.

    Args:
        source: News source (hackernews, weibo, github, etc.)
        limit: Maximum number of items (default: 10)
        keyword: Comma-separated keywords to filter (optional)

    Returns:
        List of news items with title, url, etc.
    """
    from pathlib import Path

    tool_dir = Path(__file__).parent.parent.parent / "news-aggregator-expert" / "tool"
    main_py = tool_dir / "main.py"

    if not main_py.exists():
        return [{"error": f"News aggregator tool not found at {main_py}"}]

    cmd = [sys.executable, str(main_py), "--source", source, "--limit", str(limit)]
    if keyword:
        cmd.extend(["--keyword", keyword])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return [{"error": result.stderr}]

        # Parse JSON output
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return [{"error": "Timeout fetching news"}]
    except json.JSONDecodeError as e:
        return [{"error": f"Failed to parse news result: {e}"}]
    except Exception as e:
        return [{"error": f"Unexpected error: {e}"}]


@register_external_function("fetch_hackernews")
def fetch_hackernews(limit: int = 10, keyword: str = None) -> list:
    """Fetch Hacker News (convenience wrapper)."""
    return fetch_news(source="hackernews", limit=limit, keyword=keyword)


@register_external_function("fetch_weibo")
def fetch_weibo(limit: int = 10, keyword: str = None) -> list:
    """Fetch Weibo trending (convenience wrapper)."""
    return fetch_news(source="weibo", limit=limit, keyword=keyword)


@register_external_function("fetch_github_trending")
def fetch_github_trending(limit: int = 10, keyword: str = None) -> list:
    """Fetch GitHub trending (convenience wrapper)."""
    return fetch_news(source="github", limit=limit, keyword=keyword)


# === PDF/Document Functions ===


@register_external_function("download_pdf")
def download_pdf(url: str) -> str:
    """
    Download PDF from URL.

    Args:
        url: URL of the PDF to download

    Returns:
        Path to downloaded PDF file
    """
    from pathlib import Path

    tool_dir = Path(__file__).parent.parent.parent / "pdf-downloader-expert" / "tool"
    main_py = tool_dir / "main.py"

    if not main_py.exists():
        return f"Error: PDF downloader tool not found at {main_py}"

    cmd = [sys.executable, str(main_py), url]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            return f"Error downloading PDF: {result.stderr}"

        # Extract path from output
        output = result.stdout.strip()
        if "Successfully downloaded:" in output:
            path = output.split("Successfully downloaded:")[-1].strip()
            return path
        else:
            return output

    except subprocess.TimeoutExpired:
        return "Error: Timeout downloading PDF"
    except Exception as e:
        return f"Error downloading PDF: {e}"


@register_external_function("read_file")
def read_file(path: str) -> str:
    """
    Read file contents (restricted paths only).

    Args:
        path: Path to file

    Returns:
        File contents as string
    """
    # Security: Only allow reading from specific directories
    allowed_paths = [
        "/tmp/monty/",
        "./paper_audit/inbox/",
        os.path.expanduser("~/Downloads/"),
    ]

    # Normalize path
    abs_path = os.path.abspath(path)

    # Check if path is allowed
    allowed = False
    for allowed_base in allowed_paths:
        abs_base = os.path.abspath(allowed_base)
        if abs_path.startswith(abs_base):
            allowed = True
            break

    if not allowed:
        return f"Error: Access denied to path: {path}"

    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


@register_external_function("write_file")
def write_file(path: str, content: str) -> str:
    """
    Write content to file (restricted paths only).

    Args:
        path: Path to write to
        content: Content to write

    Returns:
        Path to written file
    """
    # Security: Only allow writing to specific directories
    allowed_paths = [
        "/tmp/monty/",
        "./paper_audit/inbox/",
        os.path.expanduser("~/Downloads/"),
    ]

    # Create directories if needed
    abs_path = os.path.abspath(path)

    # Check if path is allowed
    allowed = False
    for allowed_base in allowed_paths:
        abs_base = os.path.abspath(allowed_base)
        if abs_path.startswith(abs_base):
            allowed = True
            break

    if not allowed:
        return f"Error: Access denied to path: {path}"

    try:
        # Create directory if needed
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)

        return abs_path
    except Exception as e:
        return f"Error writing file: {e}"


# === Image Conversion Functions ===


@register_external_function("convert_image")
def convert_image(input_path: str, output_path: str, format: str = "jpeg") -> str:
    """
    Convert image using imgconv tool.

    Args:
        input_path: Path to input image
        output_path: Path to output image
        format: Target format (jpeg, png, webp, etc.)

    Returns:
        Path to converted image
    """
    from pathlib import Path

    tool_dir = Path(__file__).parent.parent.parent / "imgconv-expert" / "tool"
    main_py = tool_dir / "main.py"

    if not main_py.exists():
        return f"Error: imgconv tool not found at {main_py}"

    cmd = [
        sys.executable,
        str(main_py),
        "--action",
        "convert",
        "--input",
        input_path,
        "--output",
        output_path,
        "--format",
        format,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return f"Error converting image: {result.stderr}"

        return output_path

    except subprocess.TimeoutExpired:
        return "Error: Timeout converting image"
    except Exception as e:
        return f"Error converting image: {e}"


# === Video Download Functions ===


@register_external_function("download_video")
def download_video(url: str, format: str = "best") -> str:
    """
    Download video using yt-dlp tool.

    Args:
        url: URL of video to download
        format: Video format (best, mp4, audio-only, etc.)

    Returns:
        Path to downloaded video
    """
    from pathlib import Path

    tool_dir = Path(__file__).parent.parent.parent / "yt-dlp-expert" / "tool"
    main_py = tool_dir / "main.py"

    if not main_py.exists():
        return f"Error: yt-dlp tool not found at {main_py}"

    cmd = [sys.executable, str(main_py), url, "--format", format]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout for video download
        )

        if result.returncode != 0:
            return f"Error downloading video: {result.stderr}"

        # Extract path from output
        output = result.stdout.strip()
        if "SUCCESS:" in output:
            # Parse the success output to find the file path
            lines = output.split("\n")
            for line in lines:
                if line.startswith("[download]") and "Destination:" in line:
                    path = line.split("Destination:")[-1].strip()
                    return path
        return output

    except subprocess.TimeoutExpired:
        return "Error: Timeout downloading video"
    except Exception as e:
        return f"Error downloading video: {e}"


# === Paper Audit Functions ===


@register_external_function("paper_audit_extract")
def paper_audit_extract(pdf_path: str) -> dict:
    """
    Extract PDF content for academic audit analysis.

    Args:
        pdf_path: Path to PDF file to extract

    Returns:
        Dictionary with extracted content and metadata
    """
    from pathlib import Path

    tool_dir = Path(__file__).parent.parent.parent / "paper-audit-expert" / "tool"
    main_py = tool_dir / "main.py"

    if not main_py.exists():
        return {"error": f"Paper audit tool not found at {main_py}"}

    cmd = [sys.executable, str(main_py), pdf_path]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            return {"error": result.stderr}

        # Parse JSON output
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return {"error": "Timeout extracting PDF"}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse extraction result: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}


@register_external_function("paper_audit_analyze")
def paper_audit_analyze(content: str, strictness: str = "standard") -> dict:
    """
    Perform academic audit on paper content.

    Args:
        content: Paper content or extracted text to analyze
        strictness: Analysis level (standard, rigorous, lenient)

    Returns:
        Dictionary with audit results, scores, and recommendations
    """
    from pathlib import Path

    tool_dir = Path(__file__).parent.parent.parent / "paper-audit-expert" / "tool"
    main_py = tool_dir / "main.py"

    if not main_py.exists():
        return {"error": f"Paper audit tool not found at {main_py}"}

    cmd = [sys.executable, str(main_py), "--analyze", "--strictness", strictness]

    # Write content to temp file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        temp_path = f.name

    cmd.extend(["--content-file", temp_path])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

        if result.returncode != 0:
            return {"error": result.stderr}

        # Parse JSON output
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return {"error": "Timeout analyzing paper"}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse analysis result: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}
    finally:
        # Clean up temp file
        try:
            import os

            os.unlink(temp_path)
        except:
            pass


@register_external_function("paper_audit_visualize")
def paper_audit_visualize(audit_data: dict, output_path: str = None) -> str:
    """
    Generate SVG visualization from audit results.

    Args:
        audit_data: Dictionary with audit results from paper_audit_analyze
        output_path: Optional output path for SVG file

    Returns:
        SVG content or path to generated file
    """
    from pathlib import Path

    tool_dir = Path(__file__).parent.parent.parent / "paper-audit-expert" / "tool"
    generate_svg = tool_dir / "generate_svg.py"

    if not generate_svg.exists():
        return {"error": f"SVG generator not found at {generate_svg}"}

    # Write audit data to temp file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(audit_data, f)
        temp_path = f.name

    cmd = [sys.executable, str(generate_svg), "--input", temp_path]
    if output_path:
        cmd.extend(["--output", output_path])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return {"error": result.stderr}

        # Return SVG content or file path
        if output_path:
            return output_path
        else:
            return result.stdout
    except subprocess.TimeoutExpired:
        return {"error": "Timeout generating visualization"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}
    finally:
        # Clean up temp file
        try:
            import os

            os.unlink(temp_path)
        except:
            pass


# === Utility Functions ===


@register_external_function("print")
def safe_print(*args) -> str:
    """
    Print to stdout (safe wrapper).

    Args:
        *args: Values to print

    Returns:
        Printed string
    """
    output = " ".join(str(arg) for arg in args)
    print(output)
    return output


@register_external_function("len")
def safe_len(obj) -> int:
    """
    Get length of object (safe wrapper).

    Args:
        obj: Object to get length of

    Returns:
        Length of object
    """
    try:
        return len(obj)
    except TypeError:
        return 0


@register_external_function("type")
def safe_type(obj) -> str:
    """
    Get type of object (safe wrapper).

    Args:
        obj: Object to get type of

    Returns:
        Type name as string
    """
    return type(obj).__name__


# === Playwright-Expert Functions ===


@register_external_function("playwright_browser_launch")
def playwright_browser_launch(
    browser_type: str = "chromium", headless: bool = True, timeout: int = 30000
) -> dict:
    """
    Launch a Playwright browser instance.

    Args:
        browser_type: Browser type (chromium, firefox, webkit)
        headless: Run in headless mode
        timeout: Timeout in milliseconds

    Returns:
        Dictionary with success status
    """
    from pathlib import Path
    import subprocess
    import sys
    import json

    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return {"error": f"MCP server not found at {mcp_server_path}"}

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from mcp_client import MCPClient

        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False,
        )

        result = client.call_tool_sync(
            "browser_launch",
            browser_type=browser_type,
            headless=headless,
            timeout=timeout,
        )
        return {"result": result}

    except Exception as e:
        return {"error": f"MCP call failed: {e}"}


@register_external_function("playwright_navigate")
def playwright_navigate(url: str, wait_until: str = "load") -> dict:
    """
    Navigate browser to specified URL.

    Args:
        url: URL to navigate to
        wait_until: Wait condition (load, domcontentloaded, networkidle)

    Returns:
        Dictionary with navigation result
    """
    from pathlib import Path
    import subprocess
    import sys
    import json

    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return {"error": f"MCP server not found at {mcp_server_path}"}

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from mcp_client import MCPClient

        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False,
        )

        result = client.call_tool_sync(
            "browser_navigate", url=url, wait_until=wait_until
        )
        return {"result": result}

    except Exception as e:
        return {"error": f"MCP call failed: {e}"}


@register_external_function("playwright_close")
def playwright_close() -> dict:
    """
    Close browser and cleanup resources.

    Returns:
        Dictionary with success status
    """
    from pathlib import Path
    import subprocess
    import sys
    import json

    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return {"error": f"MCP server not found at {mcp_server_path}"}

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from mcp_client import MCPClient

        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False,
        )

        result = client.call_tool_sync("browser_close")
        return {"result": result}

    except Exception as e:
        return {"error": f"MCP call failed: {e}"}


@register_external_function("playwright_set_viewport")
def playwright_set_viewport(width: int, height: int) -> dict:
    """
    Set browser window size.

    Args:
        width: Window width in pixels
        height: Window height in pixels

    Returns:
        Dictionary with success status
    """
    from pathlib import Path
    import subprocess
    import sys
    import json

    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return {"error": f"MCP server not found at {mcp_server_path}"}

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from mcp_client import MCPClient

        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False,
        )

        result = client.call_tool_sync("set_viewport", width=width, height=height)
        return {"result": result}

    except Exception as e:
        return {"error": f"MCP call failed: {e}"}


@register_external_function("playwright_screenshot")
def playwright_screenshot(
    path: str, full_page: bool = False, selector: str = None
) -> dict:
    """
    Take screenshot of current page or element.

    Args:
        path: Path to save screenshot
        full_page: Capture full page (False = visible area only)
        selector: CSS selector (if None, capture full page)

    Returns:
        Dictionary with screenshot result
    """
    from pathlib import Path
    import subprocess
    import sys
    import json

    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return {"error": f"MCP server not found at {mcp_server_path}"}

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from mcp_client import MCPClient

        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False,
        )

        result = client.call_tool_sync(
            "page_screenshot", path=path, full_page=full_page, selector=selector
        )
        return {"result": result}

    except Exception as e:
        return {"error": f"MCP call failed: {e}"}


@register_external_function("playwright_get_text")
def playwright_get_text(selector: str = None) -> str:
    """
    Extract text content from page or element.

    Args:
        selector: CSS selector (if None, get full page text)

    Returns:
        Text content
    """
    from pathlib import Path
    import subprocess
    import sys
    import json

    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return {"error": f"MCP server not found at {mcp_server_path}"}

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from mcp_client import MCPClient

        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False,
        )

        result = client.call_tool_sync("page_get_text", selector=selector)
        return {"result": result}

    except Exception as e:
        return {"error": f"MCP call failed: {e}"}


@register_external_function("playwright_get_html")
def playwright_get_html(selector: str = None) -> str:
    """
    Get HTML content from page or element.

    Args:
        selector: CSS selector (if None, get full page HTML)

    Returns:
        HTML content
    """
    from pathlib import Path
    import subprocess
    import sys
    import json

    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return {"error": f"MCP server not found at {mcp_server_path}"}

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from mcp_client import MCPClient

        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False,
        )

        result = client.call_tool_sync("page_get_html", selector=selector)
        return {"result": result}

    except Exception as e:
        return {"error": f"MCP call failed: {e}"}


@register_external_function("playwright_get_links")
def playwright_get_links() -> list:
    """
    Get all links on the current page.

    Returns:
        List of {text, href} objects
    """
    from pathlib import Path
    import subprocess
    import sys
    import json

    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return {"error": f"MCP server not found at {mcp_server_path}"}

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from mcp_client import MCPClient

        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False,
        )

        result = client.call_tool_sync("page_get_links")
        return {"result": result}

    except Exception as e:
        return {"error": f"MCP call failed: {e}"}


@register_external_function("playwright_get_info")
def playwright_get_info() -> dict:
    """
    Get current page information (URL, title, etc.).

    Returns:
        Dictionary with page metadata
    """
    from pathlib import Path
    import subprocess
    import sys
    import json

    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return {"error": f"MCP server not found at {mcp_server_path}"}

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from mcp_client import MCPClient

        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False,
        )

        result = client.call_tool_sync("page_get_info")
        return {"result": result}

    except Exception as e:
        return {"error": f"MCP call failed: {e}"}


@register_external_function("playwright_click")
def playwright_click(selector: str) -> dict:
    """
    Click element by CSS selector.

    Args:
        selector: CSS selector of element to click

    Returns:
        Dictionary with click result
    """
    from pathlib import Path
    import subprocess
    import sys
    import json

    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return {"error": f"MCP server not found at {mcp_server_path}"}

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from mcp_client import MCPClient

        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False,
        )

        result = client.call_tool_sync("page_click", selector=selector)
        return {"result": result}

    except Exception as e:
        return {"error": f"MCP call failed: {e}"}


@register_external_function("playwright_fill")
def playwright_fill(selector: str, value: str) -> dict:
    """
    Fill input field with value.

    Args:
        selector: CSS selector of input element
        value: Value to fill

    Returns:
        Dictionary with fill result
    """
    from pathlib import Path
    import subprocess
    import sys
    import json

    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return {"error": f"MCP server not found at {mcp_server_path}"}

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from mcp_client import MCPClient

        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False,
        )

        result = client.call_tool_sync("page_fill", selector=selector, value=value)
        return {"result": result}

    except Exception as e:
        return {"error": f"MCP call failed: {e}"}


@register_external_function("playwright_type")
def playwright_type(selector: str, text: str) -> dict:
    """
    Type text like a user (key-by-key).

    Args:
        selector: CSS selector of element
        text: Text to type

    Returns:
        Dictionary with type result
    """
    from pathlib import Path
    import subprocess
    import sys
    import json

    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return {"error": f"MCP server not found at {mcp_server_path}"}

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from mcp_client import MCPClient

        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False,
        )

        result = client.call_tool_sync("page_type_text", selector=selector, text=text)
        return {"result": result}

    except Exception as e:
        return {"error": f"MCP call failed: {e}"}


@register_external_function("playwright_evaluate")
def playwright_evaluate(script: str) -> Any:
    """
    Execute JavaScript code in browser context.

    Args:
        script: JavaScript code to execute

    Returns:
        Script execution result
    """
    from pathlib import Path
    import subprocess
    import sys
    import json

    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return {"error": f"MCP server not found at {mcp_server_path}"}

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from mcp_client import MCPClient

        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False,
        )

        result = client.call_tool_sync("page_evaluate", script=script)
        return {"result": result}

    except Exception as e:
        return {"error": f"MCP call failed: {e}"}


@register_external_function("playwright_wait_for_selector")
def playwright_wait_for_selector(
    selector: str, state: str = "visible", timeout: int = 5000
) -> dict:
    """
    Wait for element to appear.

    Args:
        selector: CSS selector to wait for
        state: Element state to wait for (visible, attached, hidden, detached)
        timeout: Timeout in milliseconds

    Returns:
        Dictionary with wait result
    """
    from pathlib import Path
    import subprocess
    import sys
    import json

    tool_dir = Path(__file__).parent.parent.parent / "playwright-expert" / "tool"
    mcp_server_path = tool_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return {"error": f"MCP server not found at {mcp_server_path}"}

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from mcp_client import MCPClient

        client = MCPClient(
            server_path=str(mcp_server_path),
            server_name="playwright-mcp",
            is_external=False,
        )

        result = client.call_tool_sync(
            "page_wait_for_selector", selector=selector, state=state, timeout=timeout
        )
        return {"result": result}

    except Exception as e:
        return {"error": f"MCP call failed: {e}"}


# === Registry Access Functions ===


def load_dynamic_skills():
    """
    Dynamically load external functions from other skills.
    Looks for .agent/skills/{skill_name}/tool/monty_adapter.py
    """
    skills_dir = Path(__file__).parent.parent.parent

    if not skills_dir.exists():
        return

    for skill_path in skills_dir.iterdir():
        if not skill_path.is_dir():
            continue

        # Check for monty_adapter.py
        adapter_path = skill_path / "tool" / "monty_adapter.py"
        if not adapter_path.exists():
            continue

        try:
            # Import module dynamically
            spec = importlib.util.spec_from_file_location(
                f"{skill_path.name}_adapter", adapter_path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Look for get_monty_functions()
                if hasattr(module, "get_monty_functions"):
                    functions = module.get_monty_functions()
                    if isinstance(functions, dict):
                        for name, func in functions.items():
                            if callable(func):
                                EXTERNAL_FUNCTIONS[name] = func
        except Exception as e:
            print(f"Error loading functions from {skill_path.name}: {e}", file=sys.stderr)


def get_external_functions() -> Dict[str, Callable]:
    """
    Get all registered external functions.

    Returns:
        Dictionary mapping function names to callables
    """
    load_dynamic_skills()
    return EXTERNAL_FUNCTIONS.copy()


def list_external_functions() -> Dict[str, str]:
    """
    List available external functions with docstrings.

    Returns:
        Dictionary mapping function names to descriptions
    """
    load_dynamic_skills()
    return {
        name: func.__doc__ or "No description"
        for name, func in EXTERNAL_FUNCTIONS.items()
    }


def get_function_signature(name: str) -> str:
    """
    Get function signature and description.

    Args:
        name: Function name

    Returns:
        Function signature and description
    """
    if name not in EXTERNAL_FUNCTIONS:
        return f"Function '{name}' not found"

    func = EXTERNAL_FUNCTIONS[name]
    doc = func.__doc__ or "No description"

    # Try to get signature
    try:
        import inspect

        sig = inspect.signature(func)
        return f"{name}{sig}\n\n{doc}"
    except Exception:
        return f"{name}\n\n{doc}"


if __name__ == "__main__":
    # Test: List all available external functions
    print("Available External Functions:")
    print("=" * 60)
    funcs = list_external_functions()
    for name, desc in sorted(funcs.items()):
        print(f"\n{name}:")
        print(f"  {desc}")
