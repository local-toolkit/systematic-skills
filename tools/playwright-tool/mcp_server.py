import asyncio
import json
import base64
import traceback
from typing import Any, Dict, List, Optional
from pathlib import Path
from urllib.parse import urlparse

# MCP imports
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

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
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
            )
        
        # Navigation and operations
        self.server.add_tool(
            Tool(
                name="browser_navigate",
                description="Navigate to a URL in browser",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to navigate to. Must start with http:// or https://",
                            "default": "",
                            "examples": ["https://example.com", "https://github.com"]
                        },
                        "wait_until": {
                            "type": "string",
                            "description": "Wait condition: 'load', 'networkidle', 'domcontentloaded', 'commit'",
                            "default": "load",
                            "enum": ["load", "networkidle", "domcontentloaded", "commit"]
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds",
                            "default": DEFAULT_TIMEOUT
                        }
                    }
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
            )
        
        self.server.add_tool(
            Tool(
                name="page_screenshot",
                description="Take a screenshot of current page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to save screenshot (optional)",
                            "examples": ["/path/to/screenshot.png", "./screenshot.png"]
                        },
                        "full_page": {
                            "type": "boolean",
                            "description": "Capture full page screenshot",
                            "default": False
                        },
                        "selector": {
                            "type": "string",
                            "description": "CSS selector to capture specific element (optional)",
                            "examples": ["#main-content", ".submit-button"]
                        }
                    }
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
            )
        
        self.server.add_tool(
            Tool(
                name="page_get_text",
                description="Extract text content from page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector to extract text from (optional)",
                            "examples": ["body", "h1", ".article-content"]
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds",
                            "default": 5000
                        }
                    }
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
            )
        
        self.server.add_tool(
            Tool(
                name="page_get_html",
                description="Extract HTML content from page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector to extract HTML from (optional)",
                            "examples": ["#content", ".main"]
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds",
                            "default": 5000
                        }
                    }
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
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
                            "description": "CSS selector for element to click",
                            "examples": ["#submit-button", "a[href]"]
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds",
                            "default": 5000
                        }
                    }
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
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
                            "description": "CSS selector for form element",
                            "examples": ["#username", "#password"]
                        },
                        "value": {
                            "type": "string",
                            "description": "Value to fill",
                            "examples": ["myusername", "password123"]
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds",
                            "default": 5000
                        }
                    }
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
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
                            "description": "CSS selector for input element",
                            "examples": ["#search-box", "#comment"]
                        },
                        "text": {
                            "type": "string",
                            "description": "Text to type",
                            "examples": ["Hello", "Playwright"]
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
                    }
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
            )
        
        self.server.add_tool(
            Tool(
                name="page_wait_for_selector",
                description="Wait for an element to appear in page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector to wait for",
                            "examples": ["#result", "#loading"]
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in milliseconds",
                            "default": 30000
                        },
                        "state": {
                            "type": "string",
                            "description": "Element state: 'attached', 'visible', 'hidden'",
                            "default": "visible",
                            "examples": ["visible", "hidden"]
                        }
                    }
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
            )
        
        self.server.add_tool(
            Tool(
                name="page_evaluate",
                description="Execute JavaScript in page context",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "script": {
                            "type": "string",
                            "description": "JavaScript code to execute",
                            "examples": ["document.title", "document.querySelectorAll('.item').length"]
                        }
                    }
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
            )
        
        self.server.add_tool(
            Tool(
                name="page_get_links",
                description="Get all links from current page",
                inputSchema={
                    "type": "object",
                    "properties": {}
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
            )
        
        self.server.add_tool(
            Tool(
                name="page_get_info",
                description="Get information about current page",
                inputSchema={
                    "type": "object",
                    "properties": {}
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
            )
        
        self.server.add_tool(
            Tool(
                name="browser_close",
                description="Close browser instance",
                inputSchema={
                    "type": "object",
                    "properties": {}
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
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
                            "default": 1280,
                            "examples": [1920, 1366]
                        },
                        "height": {
                            "type": "integer",
                            "description": "Viewport height in pixels",
                            "default": 720,
                            "examples": [1080, 768]
                        }
                    }
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
            )
        
        self.server.add_tool(
            Tool(
                name="execute_script",
                description="Execute custom JavaScript code in browser context",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "JavaScript code to execute",
                            "examples": ["alert('Hello')", "console.log('test')"]
                        }
                    }
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
            )
        
        # IMPROVED: page_scrape with structuredContent
        self.server.add_tool(
            name="page_scrape",
            description="Scrape structured data from page using JSON schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema": {
                        "type": "string",
                        "description": "JSON schema defining data to extract. Example: {\"title\": {\"selector\": \"h1\"}, \"price\": {\"selector\": \".price\"}}"
                        },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in milliseconds",
                        "default": 10000
                        }
                    }
                },
                "readOnly": False,
                "destructive": False,
                "idempotent": False,
                "openWorld": False
            )
        
        # IMPROVED: server initialization with capabilities
        capabilities = {
            "tools": {
                "browser_launch": True,
                "page_screenshot": True,
                "page_get_text": True,
                "page_get_html": True,
                "page_click": True,
                "page_fill": True,
                "page_type_text": True,
                "page_wait_for_selector": True,
                "page_evaluate": True,
                "page_get_links": True,
                "page_get_info": True,
                "browser_close": True,
                "set_viewport": True,
                "execute_script": True,
                "page_scrape": True
            },
            "browsers": PLAYWRIGHT_BROWSERS,
            "maxTimeout": DEFAULT_TIMEOUT,
            "supportsAuth": False,
            "supportsStreaming": True
        }
