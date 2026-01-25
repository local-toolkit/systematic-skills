---
name: playwright
description: Professional web testing and automation expert for Playwright framework. Specializes in browser automation, end-to-end testing, web scraping, and MCP server integration.
status: active
type: execution
---

# Playwright Expert Skill

## Overview

This skill provides expert knowledge on using the Playwright framework for web testing, automation, and browser control. Playwright enables reliable cross-browser testing for Chromium, Firefox, and WebKit with a single API.

## Key Capabilities

### Browser Support
- **Chromium**: Full support (current version tracks Chromium)
- **Firefox**: Full support
- **WebKit**: Full support
- **Headless execution**: Supported on all platforms
- **Mobile emulation**: Device profiles, geolocation, viewport customization

### Core Features
- **Resilient Testing**: Auto-wait mechanisms reduce flaky tests
- **Web-first Assertions**: Dynamic web-specific checks with automatic retries
- **Full Isolation**: Separate browser contexts with zero overhead
- **Multi-everything**: Multiple tabs, origins, and users simultaneously
- **Trusted Events**: Real browser input pipeline, hover interactions, dynamic controls
- **Shadow DOM Piercing**: Seamless frame and shadow DOM access

## Usage Patterns

### 1. Installation

```bash
# Initialize project
npm init playwright@latest

# Or create new project
npm init playwright@latest new-project

# Install dependencies
npm install -D @playwright/test

# Install browsers (optional)
npx playwright install chromium firefox webkit
```

### 2. Basic Testing

```typescript
import { test, expect } from '@playwright/test';

test('basic page load', async ({ page }) => {
  await page.goto('https://playwright.dev');
  await expect(page).toHaveTitle('Playwright');
});
```

### 3. Web Scraping

```typescript
import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();

// Navigate and extract data
await page.goto('https://example.com');
const title = await page.title();
const content = await page.textContent('h1');

await browser.close();
```

### 4. MCP Integration

Playwright can be integrated as an MCP (Model Context Protocol) server, allowing AI assistants to:

- Navigate to web pages
- Extract content and data
- Take screenshots
- Interact with forms and buttons
- Execute JavaScript in browser context

## Advanced Features

### Codegen
- Generate tests by recording user actions
- Save tests in multiple languages (TypeScript, JavaScript, Python, .NET, Java)

### Playwright Inspector
- Inspect pages and generate selectors
- Step through test execution
- Explore execution logs
- View click points

### Trace Viewer
- Capture execution screencast
- Live DOM snapshots
- Action explorer
- Test source and logs
- Investigate test failures

## Best Practices

### Avoiding Flaky Tests
1. **Use auto-wait**: Playwright waits for actionable elements before actions
2. **Rich introspection events**: Use locator events for robust element detection
3. **Configure retry strategy**: Built-in retry mechanisms eliminate temporary failures
4. **Use tracing**: Capture traces for debugging flaky tests

### Performance Optimization
1. **Reuse browser contexts**: Log in once and reuse across tests
2. **Use headless mode**: Faster execution when UI not needed
3. **Concurrent execution**: Run tests in parallel when possible
4. **Disable unnecessary features**: Turn off videos/screenshots in CI

### Security Considerations
1. **Never expose secrets**: Use environment variables for API keys
2. **Handle authentication securely**: Store credentials outside code
3. **Sanitize inputs**: Validate and escape user-provided data
4. **Use HTTPS**: Ensure all network requests use secure protocols
5. **CORS awareness**: Understand cross-origin restrictions

## Common Use Cases

### End-to-End Testing
- User authentication flows
- E-commerce checkout processes
- Form submissions and validations
- Multi-page workflows

### Web Scraping
- Data extraction from websites
- Monitoring page changes
- Automated content aggregation
- Price tracking and comparison

### Browser Automation
- Form filling and submission
- Navigation and interaction sequences
- Screenshot and PDF generation
- Data export workflows

## MCP Server Tools

### Basic Navigation
- `navigate_to(url)`: Navigate to a specific URL
- `screenshot()`: Capture page screenshot
- `get_page_info()`: Get title, URL, and metadata

### Content Extraction
- `get_text(selector)`: Extract text content
- `get_html(selector)`: Extract HTML content
- `get_links()`: Get all links on page
- `get_all_text()`: Get full page text content

### Interaction
- `click(selector)`: Click on an element
- `fill_form(data)`: Fill form fields
- `type_text(selector, text)`: Type text into an element
- `scroll_to_element(selector)`: Scroll to specific element

### Advanced
- `execute_script(script)`: Run JavaScript in page context
- `wait_for_selector(selector)`: Wait for element to appear
- `evaluate(func)`: Execute custom JavaScript function
- `set_viewport(width, height)`: Change browser viewport

## Resources

- **Official Docs**: https://playwright.dev/docs
- **API Reference**: https://playwright.dev/docs/api
- **Examples**: https://playwright.dev/docs/class-playwright
- **GitHub**: https://github.com/microsoft/playwright
- **Discord**: https://aka.ms/playwright/discord

## Troubleshooting

### Common Issues

**Browser not found**
- Install browsers: `npx playwright install`
- Check system requirements: https://playwright.dev/docs/intro

**Timeout issues**
- Increase default timeout: `test.setTimeout(30000)`
- Use specific wait strategies: `await page.waitForSelector(...)`

**Selector issues**
- Use Playwright Inspector to generate selectors
- Try different selector strategies: CSS, XPath, text
- Check for Shadow DOM: Use `page.locator('shadow-root >> .element')`

### Performance Tips

1. **Launch browser once**: Reuse browser instance across multiple operations
2. **Use context pooling**: Create multiple contexts in parallel
3. **Cache results**: Store intermediate results to avoid re-fetching
4. **Disable unnecessary features**: Turn off videos, traces in production

## Integration with AI Agents

When using Playwright with AI assistants:

1. **Be explicit about goals**: Clearly state what you want to achieve
2. **Provide context**: Share relevant page structure for better understanding
3. **Use selectors effectively**: Prefer stable selectors over fragile ones
4. **Handle dynamic content**: Wait for lazy-loaded content
5. **Error handling**: Always wrap operations in try-catch blocks
6. **Clean up resources**: Close browsers and contexts after use
