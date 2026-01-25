#!/usr/bin/env python3
"""
Playwright Tool - Main entry point for browser automation and MCP server.
支持直接命令行操作和 MCP 服务器模式。
"""

import argparse
import asyncio
import json
import os
import signal
import subprocess
import sys
from pathlib import Path

# Import MCP module
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool
except ImportError:
    print("⚠️  Warning: MCP module not installed. MCP features require 'mcp' package.")
    print("Install with: pip install mcp")
    print("Continuing with CLI-only mode...")

MCP_SERVER_SCRIPT = Path(__file__).parent / "mcp_server.py"
TEMPLATES_PATH = Path(__file__).parent / "templates.md"


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print(f"\n🛑 Received signal {sig}")
    sys.exit(0)


class PlaywrightCLI:
    """Command-line interface for Playwright automation."""
    
    def __init__(self):
        self.parser = self._create_parser()
        
    def _create_parser(self):
        """Create argument parser with all subcommands."""
        parser = argparse.ArgumentParser(
            description="Playwright - Web testing and automation tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="Examples:\n"
                    "  Navigate and screenshot:  python main.py navigate https://example.com --screenshot\n"
                    "  Get page text:         python main.py navigate https://example.com --get-text\n"
                    "  MCP server:            python main.py mcp-server\n"
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # MCP server command
        mcp_parser = subparsers.add_parser('mcp-server', help='Start MCP server for AI integration')
        mcp_parser.add_argument('--browser', choices=['chromium', 'firefox', 'webkit'], 
                                default='chromium', help='Browser type (default: chromium)')
        mcp_parser.add_argument('--headless', action='store_true', default=True,
                                help='Run in headless mode (default: True)')
        mcp_parser.add_argument('--port', type=int, default=3000,
                                help='Port for MCP server (default: 3000)')
        mcp_parser.add_argument('--transport', choices=['stdio', 'sse'], default='stdio',
                                help='Transport type (default: stdio)')
        
        # Browser commands
        browser_parser = subparsers.add_parser('launch', help='Launch a browser instance')
        browser_parser.add_argument('--browser', choices=['chromium', 'firefox', 'webkit'],
                                 default='chromium', help='Browser type (default: chromium)')
        browser_parser.add_argument('--headless', action='store_true', default=True,
                                 help='Run in headless mode (default: True)')
        browser_parser.add_argument('--timeout', type=int, default=30000,
                                 help='Timeout in milliseconds (default: 30000)')
        
        # Navigation commands
        nav_parser = subparsers.add_parser('navigate', help='Navigate to a URL')
        nav_parser.add_argument('url', help='URL to navigate to')
        nav_parser.add_argument('--wait-until', choices=['load', 'networkidle', 'domcontentloaded', 'commit'],
                                 default='load', help='Wait condition (default: load)')
        nav_parser.add_argument('--timeout', type=int, default=30000,
                                 help='Timeout in milliseconds (default: 30000)')
        
        # Screenshot command
        ss_parser = subparsers.add_parser('screenshot', help='Take a screenshot')
        ss_parser.add_argument('--path', type=str, default=None,
                            help='Path to save screenshot')
        ss_parser.add_argument('--full-page', action='store_true', default=False,
                            help='Capture full page screenshot (default: False)')
        ss_parser.add_argument('--selector', type=str, default=None,
                            help='CSS selector to capture specific element')
        
        # Get text command
        get_text_parser = subparsers.add_parser('get-text', help='Extract text from page')
        get_text_parser.add_argument('--selector', type=str, default=None,
                                    help='CSS selector to extract text from (optional)')
        get_text_parser.add_argument('--timeout', type=int, default=5000,
                                    help='Timeout in milliseconds (default: 5000)')
        
        # Get HTML command
        get_html_parser = subparsers.add_parser('get-html', help='Extract HTML from page')
        get_html_parser.add_argument('--selector', type=str, default=None,
                                     help='CSS selector to extract HTML from (optional)')
        get_html_parser.add_argument('--timeout', type=int, default=5000,
                                     help='Timeout in milliseconds (default: 5000)')
        
        # Click command
        click_parser = subparsers.add_parser('click', help='Click on an element')
        click_parser.add_argument('selector', type=str, required=True,
                                  help='CSS selector for element to click')
        click_parser.add_argument('--timeout', type=int, default=5000,
                                  help='Timeout in milliseconds (default: 5000)')
        
        # Fill command
        fill_parser = subparsers.add_parser('fill', help='Fill form fields')
        fill_parser.add_argument('--data', type=str, required=True,
                                help='JSON string with selector/value pairs')
        fill_parser.add_argument('--timeout', type=int, default=5000,
                                help='Timeout in milliseconds (default: 5000)')
        
        # Type command
        type_parser = subparsers.add_parser('type', help='Type text into an element')
        type_parser.add_argument('--selector', type=str, required=True,
                                help='CSS selector for input element')
        type_parser.add_argument('--text', type=str, required=True,
                                help='Text to type')
        type_parser.add_argument('--delay', type=int, default=50,
                                help='Delay between keystrokes in ms (default: 50)')
        type_parser.add_argument('--timeout', type=int, default=5000,
                                help='Timeout in milliseconds (default: 5000)')
        
        # Wait command
        wait_parser = subparsers.add_parser('wait', help='Wait for an element')
        wait_parser.add_argument('--selector', type=str, required=True,
                                help='CSS selector to wait for')
        wait_parser.add_argument('--timeout', type=int, default=30000,
                                help='Timeout in milliseconds (default: 30000)')
        wait_parser.add_argument('--state', choices=['attached', 'visible', 'hidden'],
                                default='visible', help='Element state (default: visible)')
        
        # Evaluate command
        eval_parser = subparsers.add_parser('evaluate', help='Execute JavaScript code')
        eval_parser.add_argument('code', type=str, required=True,
                                  help='JavaScript code to execute')
        
        # Get links command
        links_parser = subparsers.add_parser('get-links', help='Get all links from page')
        
        # Get info command
        info_parser = subparsers.add_parser('info', help='Get page information')
        
        # Close command
        close_parser = subparsers.add_parser('close', help='Close browser')
        
        # Viewport command
        viewport_parser = subparsers.add_parser('viewport', help='Change viewport size')
        viewport_parser.add_argument('--width', type=int, default=1280,
                                      help='Viewport width in pixels (default: 1280)')
        viewport_parser.add_argument('--height', type=int, default=720,
                                      help='Viewport height in pixels (default: 720)')
        
        # Execute script command
        script_parser = subparsers.add_parser('execute-script', help='Execute JavaScript code')
        script_parser.add_argument('code', type=str, required=True,
                                        help='JavaScript code to execute')
        
        # Scrape command
        scrape_parser = subparsers.add_parser('scrape', help='Scrape structured data using JSON schema')
        scrape_parser.add_argument('--schema', type=str, required=True,
                                       help='JSON schema defining data to extract')
        scrape_parser.add_argument('--timeout', type=int, default=10000,
                                       help='Timeout in milliseconds (default: 10000)')
        
        # Batch command
        batch_parser = subparsers.add_parser('batch', help='Execute batch operations from JSON file')
        batch_parser.add_argument('file', type=str, required=True,
                                      help='JSON file with batch operations')
        
        # Run tests command
        test_parser = subparsers.add_parser('test', help='Run Playwright tests')
        test_parser.add_argument('spec', type=str, help='Test spec file to run')
        
        # Show templates
        templates_parser = subparsers.add_parser('templates', help='Show available command templates')
        
        return parser
    
    def _run_mcp_server(self, args):
        """Run the MCP server."""
        print(f"\n🚀 Starting Playwright MCP Server...")
        print(f"   Browser: {args.browser}")
        print(f"   Headless: {args.headless}")
        print(f"   Port: {args.port}")
        print(f"   Transport: {args.transport}")
        print(f"\n💡 Use with Claude Desktop or AI assistant that supports MCP!")
        print(f"   MCP server URL: http://localhost:{args.port}")
        print(f"\n🔧 Press Ctrl+C to stop the server\n")
        
        # Prepare environment for MCP server
        env = os.environ.copy()
        env['PLAYWRIGHT_BROWSER_TYPE'] = args.browser
        env['PLAYWRIGHT_HEADLESS'] = str(args.headless)
        env['PLAYWRIGHT_PORT'] = str(args.port)
        
        # Run MCP server
        cmd = [sys.executable, str(MCP_SERVER_SCRIPT)]
        try:
            process = subprocess.Popen(
                cmd,
                env=env,
                text=True
            )
            
            # Wait for process to complete
            process.wait()
            return 0
            
        except KeyboardInterrupt:
            print(f"\n🛑 MCP Server stopped by user")
            return 130
        except Exception as e:
            print(f"❌ Error starting MCP server: {e}")
            return 1
    
    def _run_browser_command(self, args):
        """Run a browser automation command via MCP server subprocess."""
        # Import the direct Python modules
        from playwright.sync_api import sync_playwright
        import time
        
        # Parse operation type
        operation = {
            'launch': {
                'browser_type': getattr(args, 'browser', 'chromium'),
                'headless': getattr(args, 'headless', True)
            },
            'navigate': {
                'url': getattr(args, 'url', ''),
                'wait_until': getattr(args, 'wait_until', 'load'),
                'timeout': getattr(args, 'timeout', 30000)
            },
            'screenshot': {
                'path': getattr(args, 'path', None),
                'full_page': getattr(args, 'full_page', False),
                'selector': getattr(args, 'selector', None)
            },
            'get-text': {
                'selector': getattr(args, 'selector', None),
                'timeout': getattr(args, 'timeout', 5000)
            },
            'get-html': {
                'selector': getattr(args, 'selector', None),
                'timeout': getattr(args, 'timeout', 5000)
            },
            'click': {
                'selector': getattr(args, 'selector', ''),
                'timeout': getattr(args, 'timeout', 5000)
            },
            'fill': {
                'data': getattr(args, 'data', ''),
                'timeout': getattr(args, 'timeout', 5000)
            },
            'type': {
                'selector': getattr(args, 'selector', ''),
                'text': getattr(args, 'text', ''),
                'delay': getattr(args, 'delay', 50),
                'timeout': getattr(args, 'timeout', 5000)
            },
            'wait': {
                'selector': getattr(args, 'selector', ''),
                'timeout': getattr(args, 'timeout', 30000),
                'state': getattr(args, 'state', 'visible')
            },
            'evaluate': {
                'code': getattr(args, 'code', '')
            },
            'get-links': {},
            'info': {},
            'viewport': {
                'width': getattr(args, 'width', 1280),
                'height': getattr(args, 'height', 720)
            },
            'execute-script': {
                'code': getattr(args, 'code', '')
            },
            'scrape': {
                'schema': getattr(args, 'schema', ''),
                'timeout': getattr(args, 'timeout', 10000)
            },
            'close': {}
        }.get(args.command, {})
        
        if not operation:
            print(f"❌ Unknown command: {args.command}")
            return 1
        
        # Prepare command for MCP server
        mcp_cmd = [
            sys.executable,
            str(MCP_SERVER_SCRIPT),
            'mcp-server',
            '--browser', 'chromium',
            '--headless',
        ]
        
        print(f"\n🔧 Executing: {args.command} {json.dumps(operation, ensure_ascii=False)}")
        
        # Execute via subprocess
        result = subprocess.run(
                mcp_cmd,
                capture_output=True,
                text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Success")
            if result.stdout:
                print(result.stdout)
            return 0
        else:
            print(f"❌ Error (Exit Code {result.returncode})")
            if result.stderr:
                print(result.stderr)
            return 1
    
    def _show_templates(self):
        """Display command templates."""
        try:
            with open(TEMPLATES_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            print(content)
        except Exception as e:
            print(f"❌ Error reading templates: {e}")
    
    def _run_batch(self, file_path):
        """Execute batch operations from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                operations = json.load(f)
        except Exception as e:
            print(f"❌ Error reading batch file: {e}")
            return 1
        
        if not isinstance(operations, list):
            print(f"❌ Batch file must contain an array of operations")
            return 1
        
        print(f"📋 Processing {len(operations)} operations from {file_path}...")
        
        results = []
        for i, op in enumerate(operations, 1):
            print(f"  [{i}/{len(operations)}] {op.get('action', 'unknown')}", end='', flush=True)
            
            # Prepare command for MCP server
            op_json = json.dumps(op, ensure_ascii=False)
            mcp_cmd = [
                sys.executable,
                str(MCP_SERVER_SCRIPT),
                'mcp-server',
                '--browser', 'chromium',
                '--headless',
                '--execute',
                op_json
            ]
            
            result = subprocess.run(
                    mcp_cmd,
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                print(f"    ✅ Success")
                if result.stdout:
                    try:
                        data = json.loads(result.stdout)
                        print(f"    Result: {json.dumps(data, ensure_ascii=False)[:200]}...")
                    except:
                        print(f"    Output: {result.stdout[:200]}...")
                    results.append(True)
            else:
                print(f"    ❌ Error")
                if result.stderr:
                    print(f"    {result.stderr[:100]}")
                results.append(False)
        
        success_count = sum(results)
        print(f"\n📊 Batch complete: {success_count}/{len(operations)} operations succeeded")
        return 0 if success_count == len(operations) else 1
    
    def _run_tests(self, spec):
        """Run Playwright tests using npx playwright test."""
        print(f"🧪 Running tests: {spec}")
        
        cmd = ['npx', 'playwright', 'test', spec]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Tests completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ Tests failed (Exit Code {result.returncode})")
            if result.stderr:
                print(result.stderr)
        
        return result.returncode
    
    def run(self):
        """Main entry point."""
        args = self.parser.parse_args()
        
        # Register signal handler
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Route to appropriate handler
        if args.command == 'mcp-server':
            return self._run_mcp_server(args)
        
        elif args.command == 'templates':
            return self._show_templates()
        
        elif args.command == 'batch':
            return self._run_batch(args.file)
        
        elif args.command == 'test':
            return self._run_tests(args.spec)
        
        else:
            return self._run_browser_command(args)


def main():
    """Main entry point."""
    cli = PlaywrightCLI()
    
    # Check if command is provided
    if len(sys.argv) == 1:
        print("❌ No command specified")
        print("\nUse: python main.py <command> [options]")
        print("\nAvailable commands:")
        print("  mcp-server    - Start MCP server")
        print("  launch       - Launch a browser instance")
        print("  navigate      - Navigate to a URL")
        print("  screenshot    - Take a screenshot")
        print("  get-text     - Extract text from page")
        print("  get-html      - Extract HTML from page")
        print("  click         - Click on an element")
        print("  fill          - Fill form fields")
        print("  type          - Type text into an element")
        print("  wait          - Wait for an element")
        print("  evaluate      - Execute JavaScript code")
        print("  get-links     - Get all links from page")
        print("  info          - Get page information")
        print("  close         - Close browser")
        print("  viewport       - Change viewport size")
        print("  execute-script- Execute JavaScript code")
        print("  scrape         - Scrape structured data")
        print("  batch         - Execute batch operations from file")
        print("  test          - Run Playwright tests")
        print("  templates     - Show command templates")
        print("\nExamples:")
        print("  python main.py launch --browser chromium --headless false")
        print("  python main.py navigate https://github.com --screenshot --path screenshot.png")
        print("  python main.py mcp-server --browser chromium --port 3000")
        sys.exit(1)
    
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
