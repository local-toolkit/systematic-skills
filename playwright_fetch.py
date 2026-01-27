#!/usr/bin/env python3
"""
Script to fetch article content using Playwright
"""

import asyncio
import json
from playwright.async_api import async_playwright


async def fetch_article_content(url):
    """Fetch article content using Playwright"""
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Set viewport size
        await page.set_viewport_size({"width": 1280, "height": 720})

        # Navigate to URL
        print(f"Navigating to: {url}")
        await page.goto(url, wait_until="networkidle", timeout=30000)

        # Wait a bit for content to load
        await page.wait_for_timeout(3000)

        # Get page title
        title = await page.title()
        print(f"Page title: {title}")

        # Try to get article content
        # Common selectors for article content
        selectors = [
            "article",
            ".article-content",
            ".content",
            ".post-content",
            ".entry-content",
            '[class*="content"]',
            '[class*="article"]',
            "main",
            '[role="main"]',
        ]

        content = ""
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    content = await element.inner_text()
                    if content.strip():
                        print(f"Found content using selector: {selector}")
                        break
            except Exception as e:
                print(f"Selector {selector} failed: {e}")
                continue

        # If no specific content found, get full page text
        if not content.strip():
            print("No specific content found, getting full page text")
            content = await page.inner_text("body")

        # Get page URL
        current_url = page.url

        # Close browser
        await browser.close()

        return {
            "url": current_url,
            "title": title,
            "content": content[:5000] + "..." if len(content) > 5000 else content,
        }


async def main():
    url = "https://wallstreetcn.com/articles/3764192"

    try:
        result = await fetch_article_content(url)
        print("\n" + "=" * 50)
        print("ARTICLE CONTENT:")
        print("=" * 50)
        print(f"URL: {result['url']}")
        print(f"Title: {result['title']}")
        print(f"\nContent:")
        print(result["content"])
        print("=" * 50)

        # Save to file
        with open("article_content.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nContent saved to article_content.json")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
