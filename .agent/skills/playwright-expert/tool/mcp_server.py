#!/usr/bin/env python3
"""
Playwright MCP Server
MCP server for Playwright browser automation and web testing.
"""

import asyncio
import json
import base64
import traceback
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path
from urllib.parse import urlparse

# MCP imports
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
except ImportError:
    print("Error: MCP package not installed. Run 'pip install mcp'")
    sys.exit(1)

from playwright.async_api import async_playwright

# Configuration
PLAYWRIGHT_BROWSERS = ["chromium", "firefox", "webkit"]
DEFAULT_TIMEOUT = 30000
DEFAULT_HEADLESS = True

class PlaywrightMCPServer:
    """MCP Server for Playwright browser automation."""
    
    def __init__(self):
        self.server = Server("playwright-mcp-server", "1.0.0")
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.current_url = None
        
        # Register tools
        self._register_tools()
        self._register_handlers()
        
    def _register_tools(self):
        """Register all available MCP tools."""
        
        # Browser lifecycle
        self.server.add_tool(
            Tool(
                name="browser_launch",
                description="Launch a Playwright browser instance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "browser_type": {
                            "type": "string",
                            "description": "Browser type to launch",
                            "enum": PLAYWRIGHT_BROWSERS,
                            "default": "chromium"
                        },
                        "headless": {
                            "type": "boolean",
                            "description": "Run in headless mode",
                            "default": True
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds",
                            "default": DEFAULT_TIMEOUT
                        }
                    }
                }
            )
        )
        
        self.server.add_tool(
            Tool(
                name="browser_navigate",
                description="Navigate to a URL in the browser",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to navigate to"
                        },
                        "wait_until": {
                            "type": "string",
                            "description": "Wait condition: 'load', 'networkidle', 'domcontentloaded'",
                            "default": "load",
                            "enum": ["load", "networkidle", "domcontentloaded", "commit"]
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds",
                            "default": DEFAULT_TIMEOUT
                        }
                    },
                    "required": ["url"]
                }
            )
        )
        
        self.server.add_tool(
            Tool(
                name="page_screenshot",
                description="Take a screenshot of the current page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to save screenshot (optional)"
                        },
                        "full_page": {
                            "type": "boolean",
                            "description": "Capture full page screenshot",
                            "default": False
                        },
                        "selector": {
                            "type": "string",
                            "description": "CSS selector to capture specific element (optional)"
                        }
                    }
                }
            )
        )
        
        self.server.add_tool(
            Tool(
                name="page_get_text",
                description="Extract text content from the page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector to extract text from (optional)"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds",
                            "default": 5000
                        }
                    }
                }
            )
        )
        
        self.server.add_tool(
            Tool(
                name="page_get_html",
                description="Extract HTML content from the page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector to extract HTML from (optional)"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds",
                            "default": 5000
                        }
                    }
                }
            )
        )
        
        self.server.add_tool(
            Tool(
                name="page_click",
                description="Click on an element using CSS selector",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for element to click"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds",
                            "default": 5000
                        }
                    },
                    "required": ["selector"]
                }
            )
        )
        
        self.server.add_tool(
            Tool(
                name="page_fill",
                description="Fill form fields with data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for form element"
                        },
                        "value": {
                            "type": "string",
                            "description": "Value to fill"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds",
                            "default": 5000
                        }
                    },
                    "required": ["selector", "value"]
                }
            )
        )
        
        self.server.add_tool(
            Tool(
                name="page_type_text",
                description="Type text into an input field",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for input element"
                        },
                        "text": {
                            "type": "string",
                            "description": "Text to type"
                        },
                        "delay": {
                            "type": "integer",
                            "description": "Delay between keystrokes in ms",
                            "default": 50
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds",
                            "default": 5000
                        }
                    },
                    "required": ["selector", "text"]
                }
            )
        )
        
        self.server.add_tool(
            Tool(
                name="page_evaluate",
                description="Execute JavaScript in the page context",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "script": {
                            "type": "string",
                            "description": "JavaScript code to execute"
                        }
                    },
                    "required": ["script"]
                }
            )
        )
        
        self.server.add_tool(
            Tool(
                name="page_wait_for_selector",
                description="Wait for an element to appear in the page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector to wait for"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds",
                            "default": 30000
                        },
                        "state": {
                            "type": "string",
                            "description": "Element state: 'attached', 'visible', 'hidden'",
                            "default": "visible"
                        }
                    },
                    "required": ["selector"]
                }
            )
        )
        
        self.server.add_tool(
            Tool(
                name="page_get_links",
                description="Get all links from the current page",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        )
        
        self.server.add_tool(
            Tool(
                name="page_get_info",
                description="Get information about the current page (title, URL, etc.)",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        )
        
        self.server.add_tool(
            Tool(
                name="browser_close",
                description="Close the browser instance",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        )
        
        self.server.add_tool(
            Tool(
                name="set_viewport",
                description="Change browser viewport size",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "width": {
                            "type": "integer",
                            "description": "Viewport width in pixels",
                            "default": 1280
                        },
                        "height": {
                            "type": "integer",
                            "description": "Viewport height in pixels",
                            "default": 720
                        }
                    }
                }
            )
        )

    def _register_handlers(self):
        """Register tool handlers."""
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            try:
                if name == "browser_launch":
                    result = await self.browser_launch(**arguments)
                elif name == "browser_navigate":
                    result = await self.browser_navigate(**arguments)
                elif name == "page_screenshot":
                    result = await self.page_screenshot(**arguments)
                elif name == "page_get_text":
                    result = await self.page_get_text(**arguments)
                elif name == "page_get_html":
                    result = await self.page_get_html(**arguments)
                elif name == "page_click":
                    result = await self.page_click(**arguments)
                elif name == "page_fill":
                    result = await self.page_fill(**arguments)
                elif name == "page_type_text":
                    result = await self.page_type_text(**arguments)
                elif name == "page_evaluate":
                    result = await self.page_evaluate(**arguments)
                elif name == "page_wait_for_selector":
                    result = await self.page_wait_for_selector(**arguments)
                elif name == "page_get_links":
                    result = await self.page_get_links()
                elif name == "page_get_info":
                    result = await self.page_get_info()
                elif name == "browser_close":
                    result = await self.browser_close()
                elif name == "set_viewport":
                    result = await self.set_viewport(**arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
                
                return [TextContent(type="text", text=result)]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}\n{traceback.format_exc()}")]

    async def _ensure_browser(self, browser_type: str = "chromium", headless: bool = True, timeout: int = DEFAULT_TIMEOUT) -> None:
        if self.playwright is None:
            self.playwright = await async_playwright().start()
            
        if self.browser is None:
            if browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(headless=headless, timeout=timeout)
            elif browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(headless=headless, timeout=timeout)
            elif browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(headless=headless, timeout=timeout)
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")

    async def _ensure_context(self) -> None:
        if self.context is None:
            if self.browser is None:
                await self._ensure_browser()
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )

    async def _ensure_page(self, url: Optional[str] = None) -> None:
        await self._ensure_context()
        if self.page is None:
            self.page = await self.context.new_page()
        if url and self.page.url != url:
            await self.page.goto(url, wait_until="load", timeout=DEFAULT_TIMEOUT)

    async def browser_launch(self, browser_type: str = "chromium", headless: bool = True, timeout: int = DEFAULT_TIMEOUT) -> str:
        await self._ensure_browser(browser_type, headless, timeout)
        return json.dumps({"status": "success", "message": f"Browser {browser_type} launched"})

    async def browser_navigate(self, url: str, wait_until: str = "load", timeout: int = DEFAULT_TIMEOUT) -> str:
        await self._ensure_page()
        if not wait_until in ["load", "domcontentloaded", "networkidle", "commit"]:
            wait_until = "load"
        await self.page.goto(url, wait_until=wait_until, timeout=timeout)
        return json.dumps({"status": "success", "url": self.page.url, "title": await self.page.title()})

    async def page_screenshot(self, path: Optional[str] = None, full_page: bool = False, selector: Optional[str] = None) -> str:
        await self._ensure_page()
        actual_path = path or "screenshot.png"
        if selector:
            await self.page.locator(selector).screenshot(path=actual_path)
        else:
            await self.page.screenshot(path=actual_path, full_page=full_page)
        return json.dumps({"status": "success", "path": actual_path})

    async def page_get_text(self, selector: Optional[str] = None, timeout: int = 5000) -> str:
        await self._ensure_page()
        if selector:
            text = await self.page.locator(selector).inner_text(timeout=timeout)
        else:
            text = await self.page.content()
        return json.dumps({"status": "success", "text": text})

    async def page_get_html(self, selector: Optional[str] = None, timeout: int = 5000) -> str:
        await self._ensure_page()
        if selector:
            html = await self.page.locator(selector).inner_html(timeout=timeout)
        else:
            html = await self.page.content()
        return json.dumps({"status": "success", "html": html})

    async def page_click(self, selector: str, timeout: int = 5000) -> str:
        await self._ensure_page()
        await self.page.locator(selector).click(timeout=timeout)
        return json.dumps({"status": "success", "message": f"Clicked {selector}"})

    async def page_fill(self, selector: str, value: str, timeout: int = 5000) -> str:
        await self._ensure_page()
        await self.page.locator(selector).fill(value, timeout=timeout)
        return json.dumps({"status": "success", "message": f"Filled {selector}"})

    async def page_type_text(self, selector: str, text: str, delay: int = 50, timeout: int = 5000) -> str:
        await self._ensure_page()
        await self.page.locator(selector).type(text, delay=delay, timeout=timeout)
        return json.dumps({"status": "success", "message": f"Typed text into {selector}"})

    async def page_evaluate(self, script: str) -> str:
        await self._ensure_page()
        result = await self.page.evaluate(script)
        return json.dumps({"status": "success", "result": result})

    async def page_wait_for_selector(self, selector: str, timeout: int = 30000, state: str = "visible") -> str:
        await self._ensure_page()
        await self.page.wait_for_selector(selector, state=state, timeout=timeout)
        return json.dumps({"status": "success", "message": f"Selector {selector} is {state}"})

    async def page_get_links(self) -> str:
        await self._ensure_page()
        links = await self.page.evaluate("""() => Array.from(document.querySelectorAll('a')).map(a => ({text: a.innerText, href: a.href}))""")
        return json.dumps({"status": "success", "links": links})

    async def page_get_info(self) -> str:
        await self._ensure_page()
        info = {"title": await self.page.title(), "url": self.page.url}
        return json.dumps({"status": "success", "info": info})

    async def browser_close(self) -> str:
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        self.context = None
        self.page = None
        return json.dumps({"status": "success", "message": "Browser closed"})

    async def set_viewport(self, width: int, height: int) -> str:
        await self._ensure_page()
        await self.page.set_viewport_size({"width": width, "height": height})
        return json.dumps({"status": "success", "message": f"Viewport set to {width}x{height}"})

    async def cleanup(self):
        await self.browser_close()

    async def serve(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="playwright-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

async def main():
    server = PlaywrightMCPServer()
    try:
        await server.serve()
    finally:
        await server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
