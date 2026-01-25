#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified MCP Client - Standardized MCP Tool Integration

This module provides a unified client for all tools that need MCP (Model Context Protocol) integration.
It abstracts away the complexity of connecting to MCP servers and calling tools.

Usage:
    from mcp_client import MCPClient

    # For tool with local MCP server
    client = MCPClient("my-tool-mcp/server.py", "my-tool-mcp")
    result = client.call_tool("tool_name", param1="value1")

    # For external MCP server (like TrendRadar)
    client = MCPClient("~/TrendRadar/mcp_server/server.py", "trendradar-mcp", is_external=True)
    result = client.call_tool("get_latest_news", limit=50)
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from mcp import Client
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


class MCPClientError(Exception):
    """MCP client error."""
    pass


class MCPClient:
    """
    Unified MCP client for tool integration.

    Supports two modes:
    1. Local MCP server: tool has its own mcp_server.py
    2. External MCP server: uses external MCP server (like TrendRadar)
    """

    def __init__(
        self,
        server_path: str,
        server_name: str,
        python_exe: Optional[str] = None,
        is_external: bool = False,
        timeout: int = 60
    ):
        """
        Initialize MCP client.

        Args:
            server_path: Path to MCP server script (relative or absolute)
            server_name: Name of the MCP server (for error messages)
            python_exe: Python executable to use (default: sys.executable)
            is_external: True if this is an external MCP server
            timeout: Timeout in seconds for MCP calls
        """
        # Expand server path
        self.server_path = Path(server_path).expanduser().resolve()

        # Validate server exists
        if not self.server_path.exists():
            raise MCPClientError(
                f"MCP server not found at: {self.server_path}\n"
                f"Please install the server first."
            )

        self.server_name = server_name
        self.python_exe = python_exe or sys.executable
        self.is_external = is_external
        self.timeout = timeout
        self._client = None

        if not MCP_AVAILABLE:
            raise MCPClientError(
                "MCP package not installed. Please install:\n"
                "  pip install mcp\n\n"
                "Add to requirements.txt: mcp>=0.9.0"
            )

    async def _connect(self):
        """Establish connection to MCP server."""
        try:
            # Start MCP server via stdio
            read, write = await stdio_client(
                [str(self.python_exe), str(self.server_path), "--transport", "stdio"]
            )

            # Create client
            self._client = Client(read, write)

            # Initialize connection
            await self._client.initialize()

            # List available tools (for debugging)
            tools = await self._client.list_tools()
            return tools
        except Exception as e:
            raise MCPClientError(f"Failed to connect to MCP server: {e}")

    async def call_tool(self, tool_name: str, **kwargs) -> str:
        """
        Call an MCP tool.

        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool arguments

        Returns:
            Tool result as string

        Raises:
            MCPClientError: If tool call fails
        """
        try:
            # Connect if not already connected
            if not self._client:
                await self._connect()

            # Call tool
            result = await self._client.call_tool(tool_name, kwargs)

            # Extract text content from result
            if result.content:
                text_content = []
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        text_content.append(content_item.text)
                    elif hasattr(content_item, 'data'):
                        # Binary data (like images)
                        text_content.append(f"[Binary data: {len(content_item.data)} bytes]")
                return "\n".join(text_content) if text_content else str(result.content)

            return str(result.content)

        except Exception as e:
            raise MCPClientError(f"Tool call failed: {e}")

    def call_tool_sync(self, tool_name: str, **kwargs) -> str:
        """
        Synchronous wrapper for async call_tool.

        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool arguments

        Returns:
            Tool result as string
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.call_tool(tool_name, **kwargs))
            loop.close()
            return result
        except Exception as e:
            return f"ERROR: {str(e)}"

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools from MCP server.

        Returns:
            List of tool information dictionaries
        """
        if not self._client:
            await self._connect()

        tools = await self._client.list_tools()

        # Convert to dictionaries for easier access
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in tools
        ]

    async def close(self):
        """Close MCP connection."""
        if self._client:
            try:
                await self._client.close()
            except Exception as e:
                print(f"Warning: Error closing MCP connection: {e}")
            finally:
                self._client = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.close())
        except Exception:
            pass


class SubprocessToolClient:
    """
    Simple subprocess client for tools that don't need MCP.

    For simple tools that just have main.py and handle CLI arguments.
    """

    def __init__(
        self,
        script_path: str,
        tool_name: str,
        python_exe: Optional[str] = None
    ):
        """
        Initialize subprocess tool client.

        Args:
            script_path: Path to main.py script
            tool_name: Name of the tool (for error messages)
            python_exe: Python executable to use
        """
        self.script_path = Path(script_path).expanduser().resolve()
        self.tool_name = tool_name
        self.python_exe = python_exe or sys.executable

        if not self.script_path.exists():
            raise FileNotFoundError(f"Tool script not found: {self.script_path}")

    def call(self, **kwargs) -> str:
        """
        Call tool via subprocess.

        Args:
            **kwargs: Command-line arguments

        Returns:
            Tool output as string
        """
        # Build command
        cmd = [str(self.python_exe), str(self.script_path)]

        # Convert kwargs to CLI arguments
        for key, value in kwargs.items():
            if value is not None and value is not False:
                # Convert underscores to dashes
                arg_name = f"--{key.replace('_', '-')}"
                if isinstance(value, bool) and value:
                    cmd.append(arg_name)
                elif not isinstance(value, bool):
                    cmd.extend([arg_name, str(value)])

        print(f"\n🚀 Executing: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return f"SUCCESS:\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"ERROR (Exit Code {e.returncode}):\n{e.stderr}\n{e.stdout}"
        except Exception as e:
            return f"EXECUTION FAILED: {str(e)}"


# Convenience functions for backward compatibility
def create_mcp_client(
    server_path: str,
    server_name: str,
    is_external: bool = False
) -> MCPClient:
    """
    Create MCP client with default settings.

    Args:
        server_path: Path to MCP server
        server_name: Server name
        is_external: True for external servers

    Returns:
        MCPClient instance
    """
    return MCPClient(
        server_path=server_path,
        server_name=server_name,
        is_external=is_external
    )


def create_subprocess_client(script_path: str, tool_name: str) -> SubprocessToolClient:
    """
    Create subprocess client with default settings.

    Args:
        script_path: Path to main.py
        tool_name: Tool name

    Returns:
        SubprocessToolClient instance
    """
    return SubprocessToolClient(
        script_path=script_path,
        tool_name=tool_name
    )


if __name__ == "__main__":
    # Test MCP client
    import argparse

    parser = argparse.ArgumentParser(description="Test MCP client")
    parser.add_argument("server_path", help="Path to MCP server")
    parser.add_argument("--tool", default="list_tools", help="Tool to call")
    parser.add_argument("--is-external", action="store_true", help="External MCP server")

    args = parser.parse_args()

    if args.tool == "list_tools":
        async def test_list():
            client = MCPClient(args.server_path, "test", is_external=args.is_external)
            tools = await client.list_tools()
            print(f"Available tools ({len(tools)}):")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description'][:50]}")

        asyncio.run(test_list())
    else:
        client = MCPClient(args.server_path, "test", is_external=args.is_external)
        result = client.call_tool_sync(args.tool, test=True)
        print(result)
