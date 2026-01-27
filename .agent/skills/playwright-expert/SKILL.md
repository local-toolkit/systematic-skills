---
name: playwright
description: Professional web testing and automation expert for Playwright framework. Specializes in browser automation, end-to-end testing, web scraping, and MCP server integration.
status: active
type: execution
---

# Playwright Expert Skill

## Agent Instructions

### Goal Definition

- **Explicitly state goals**: clearly define what you want to extract or interact with.
- **Context is key**: Provide relevant page structure or selectors if known.

### Interaction Rules

1. **Navigation**: Use `browser_navigate` to start.
2. **Selectors**: Prefer stable selectors (ID, data-testid) over fragile ones (long XPaths).
3. **Dynamic Content**: Always use `page_wait_for_selector` before interacting with elements that might be loading.
4. **Error Handling**: If a tool fails, analyze the error message and try a different selector or wait longer.
5. **Cleanup**: Always call `browser_close` when the task is finished.

## MCP Server Tools

### Lifecycle & Navigation

- `browser_launch(browser_type="chromium", headless=True)`: Launch browser.
- `browser_navigate(url, wait_until="load")`: Navigate to URL.
- `browser_close()`: Close browser and cleanup resources.
- `set_viewport(width, height)`: Set window size.

### Inspection & Extraction

- `page_screenshot(path, full_page=False, selector=None)`: Save screenshot.
- `page_get_text(selector=None)`: Get text content (full page or element).
- `page_get_html(selector=None)`: Get HTML content.
- `page_get_links()`: Get all links as {text, href} objects.
- `page_get_info()`: Get current title and URL.

### Interaction

- `page_click(selector)`: Click element.
- `page_fill(selector, value)`: Fill form input.
- `page_type_text(selector, text)`: Type like a user.
- `page_evaluate(script)`: Execute JavaScript in browser context.
- `page_wait_for_selector(selector, state="visible")`: Wait for element presence/visibility.
