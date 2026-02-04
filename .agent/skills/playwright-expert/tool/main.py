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
import time
from pathlib import Path

# Import MCP module
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool
except ImportError:
    # MCP might be optional for core CLI features
    pass

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
        nav_parser.add_argument('--get-text', action='store_true', help='Get page text after navigation')
        nav_parser.add_argument('--screenshot', action='store_true', help='Take screenshot after navigation')
        
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
        click_parser.add_argument('selector', type=str,
                                  help='CSS selector for element to click')
        click_parser.add_argument('--timeout', type=int, default=5000,
                                  help='Timeout in milliseconds (default: 5000)')
        
        # Fill command
        fill_parser = subparsers.add_parser('fill', help='Fill form fields')
        fill_parser.add_argument('--selector', type=str, help='CSS selector')
        fill_parser.add_argument('--value', type=str, help='Value to fill')
        fill_parser.add_argument('--timeout', type=int, default=5000,
                                help='Timeout in milliseconds (default: 5000)')
        
        # Type command
        type_parser = subparsers.add_parser('type', help='Type text into an element')
        type_parser.add_argument('--selector', type=str, help='CSS selector')
        type_parser.add_argument('--text', type=str, help='Text to type')
        type_parser.add_argument('--delay', type=int, default=50,
                                help='Delay between keystrokes in ms (default: 50)')
        type_parser.add_argument('--timeout', type=int, default=5000,
                                help='Timeout in milliseconds (default: 5000)')
        
        # Wait command
        wait_parser = subparsers.add_parser('wait', help='Wait for an element')
        wait_parser.add_argument('selector', type=str, help='CSS selector to wait for')
        wait_parser.add_argument('--timeout', type=int, default=30000,
                                help='Timeout in milliseconds (default: 30000)')
        wait_parser.add_argument('--state', choices=['attached', 'visible', 'hidden'],
                                default='visible', help='Element state (default: visible)')
        
        # Evaluate command
        eval_parser = subparsers.add_parser('evaluate', help='Execute JavaScript code')
        eval_parser.add_argument('code', type=str, help='JavaScript code to execute')
        
        # Get links command
        links_parser = subparsers.add_parser('get-links', help='Get all links from page')
        
        # Get info command
        info_parser = subparsers.add_parser('info', help='Get page information')
        
        # Viewport command
        viewport_parser = subparsers.add_parser('viewport', help='Change viewport size')
        viewport_parser.add_argument('--width', type=int, default=1280,
                                      help='Viewport width in pixels (default: 1280)')
        viewport_parser.add_argument('--height', type=int, default=720,
                                      help='Viewport height in pixels (default: 720)')
        
        # Scrape command
        scrape_parser = subparsers.add_parser('scrape', help='Scrape structured data using JSON schema')
        scrape_parser.add_argument('--schema', type=str, help='JSON schema')
        scrape_parser.add_argument('--timeout', type=int, default=10000,
                                       help='Timeout in milliseconds (default: 10000)')
        
        # Batch command
        batch_parser = subparsers.add_parser('batch', help='Execute batch operations from JSON file')
        batch_parser.add_argument('file', type=str, help='JSON file with batch operations')
        
        # Show templates
        subparsers.add_parser('templates', help='Show available command templates')
        
        return parser
    
    def _run_mcp_server(self, args):
        """Run the MCP server."""
        print(f"\n🚀 Starting Playwright MCP Server...")
        print(f"   Browser: {args.browser}")
        print(f"   Headless: {args.headless}")
        cmd = [sys.executable, str(MCP_SERVER_SCRIPT)]
        try:
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            print(f"\n🛑 MCP Server stopped by user")
        return 0

    def _run_browser_command(self, args):
        """Run a browser automation command directly using sync Playwright."""
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser_type = getattr(args, 'browser', 'chromium')
            headless = getattr(args, 'headless', True)
            
            launch_options = {"headless": headless}
            if browser_type == 'chromium':
                browser = p.chromium.launch(**launch_options)
            elif browser_type == 'firefox':
                browser = p.firefox.launch(**launch_options)
            else:
                browser = p.webkit.launch(**launch_options)
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            try:
                if args.command == 'navigate':
                    wait_until = args.wait_until
                    if wait_until == 'commit': wait_until = 'domcontentloaded'
                    page.goto(args.url, wait_until=wait_until, timeout=args.timeout)
                    print(f"✅ Navigated to {args.url}")
                    print(f"Title: {page.title()}")
                    
                    if args.get_text:
                        print("\n--- Page Content ---")
                        print(page.content()[:1000] + "...")
                    if args.screenshot:
                        page.screenshot(path="screenshot.png")
                        print("✅ Screenshot saved to screenshot.png")
                
                elif args.command == 'launch':
                    print(f"✅ Browser {browser_type} launched successfully.")
                
                elif args.command == 'get-text':
                    if args.selector:
                        print(page.locator(args.selector).inner_text())
                    else:
                        print(page.content())
                
                elif args.command == 'evaluate':
                    print(page.evaluate(args.code))
                
                # ... add other direct implementations if needed ...
                
            except Exception as e:
                print(f"❌ Error: {e}")
                return 1
            finally:
                browser.close()
        return 0

    def _show_templates(self):
        """Display command templates."""
        if TEMPLATES_PATH.exists():
            print(TEMPLATES_PATH.read_text())
        else:
            print("❌ Templates file not found")
    
    def run(self):
        """Main entry point."""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return 1
            
        # Register signal handler
        signal.signal(signal.SIGINT, signal_handler)
        
        if args.command == 'mcp-server':
            return self._run_mcp_server(args)
        elif args.command == 'templates':
            self._show_templates()
            return 0
        else:
            return self._run_browser_command(args)

def main():
    cli = PlaywrightCLI()
    sys.exit(cli.run())

if __name__ == '__main__':
    main()
