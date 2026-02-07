#!/usr/bin/env python3
"""
Automated test suite for Monty external functions.
Tests all integrated external functions for basic functionality.
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Tuple, List


def run_monty_test(code: str, description: str, timeout: int = 30) -> Tuple[bool, str]:
    """
    Run a Monty test with external functions enabled.

    Returns:
        (success: bool, output: str)
    """
    print(f"\n[TEST] {description}")

    cmd = [
        sys.executable,
        ".agent/skills/monty-expert/tool/main.py",
        "--use-external-funcs",
        "--code",
        code,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode == 0:
            print(f"  ✅ PASS")
            return True, result.stdout
        else:
            print(f"  ❌ FAIL - Exit code: {result.returncode}")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
            return False, result.stderr

    except subprocess.TimeoutExpired:
        print(f"  ⏱️  TIMEOUT after {timeout}s")
        return False, "Timeout"
    except Exception as e:
        print(f"  ⚠️  EXCEPTION: {e}")
        return False, str(e)


def run_list_test() -> bool:
    """Test that all functions are registered."""
    print("\n" + "=" * 60)
    print("TEST: List all registered external functions")
    print("=" * 60)

    cmd = [
        sys.executable,
        ".agent/skills/monty-expert/tool/main.py",
        "--list-external-funcs",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            # Count registered functions
            lines = result.stdout.split("\n")
            func_count = sum(1 for line in lines if ":" in line and line.strip())

            print(f"\n  ✅ Found {func_count} registered functions")

            # Check for specific function groups
            expected_groups = {
                "News": [
                    "fetch_news",
                    "fetch_hackernews",
                    "fetch_weibo",
                    "fetch_github_trending",
                ],
                "PDF": ["download_pdf", "read_file", "write_file"],
                "Image": ["convert_image"],
                "Video": ["download_video"],
                "Paper Audit": [
                    "paper_audit_extract",
                    "paper_audit_analyze",
                    "paper_audit_visualize",
                ],
                "Playwright": [
                    "playwright_browser_launch",
                    "playwright_navigate",
                    "playwright_close",
                    "playwright_set_viewport",
                    "playwright_screenshot",
                    "playwright_get_text",
                    "playwright_get_html",
                    "playwright_get_links",
                    "playwright_get_info",
                    "playwright_click",
                    "playwright_fill",
                    "playwright_type",
                    "playwright_evaluate",
                    "playwright_wait_for_selector",
                ],
                "Utility": ["print", "len", "type"],
            }

            missing = []
            for group, funcs in expected_groups.items():
                for func in funcs:
                    if func not in result.stdout:
                        missing.append(f"{group}: {func}")

            if missing:
                print(f"  ⚠️  Missing functions: {missing}")
                return False
            else:
                print(f"  ✅ All expected functions found")
                return True
        else:
            print(f"  ❌ Failed to list functions")
            print(f"  Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"  ⚠️  EXCEPTION: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Monty External Functions Test Suite")
    print("=" * 60)

    # Test 1: List all functions
    test1_pass = run_list_test()

    # Test 2: Basic execution (no external functions)
    test2_pass, _ = run_monty_test(
        "print('hello from monty')",
        "Basic execution without external functions",
        timeout=10,
    )

    # Test 3: Utility functions
    test3_pass, _ = run_monty_test(
        "result = len([1,2,3,4,5]); print(result)",
        "Utility function: len",
        timeout=10,
    )

    test4_pass, _ = run_monty_test(
        "result = type(42); print(result)",
        "Utility function: type",
        timeout=10,
    )

    # Test 5: News aggregation (will fail if network unavailable)
    test5_pass, _ = run_monty_test(
        "news = fetch_hackernews(limit=3); print(f'Fetched: {len(news)}')",
        "News aggregation: fetch_hackernews",
        timeout=30,
    )

    # Test 6: File operations (create temp file)
    test6_pass, _ = run_monty_test(
        """
import os
os.makedirs('/tmp/monty', exist_ok=True)
result = write_file('/tmp/monty/test.txt', 'Hello Monty!')
print(f'Written: {len(result) > 20}')
""",
        "File operation: write_file",
        timeout=15,
    )

    test7_pass, _ = run_monty_test(
        "content = read_file('/tmp/monty/test.txt'); print(f'Read: {len(content) > 0}')",
        "File operation: read_file",
        timeout=10,
    )

    # Test 8: Paper audit (minimal test)
    test8_pass, _ = run_monty_test(
        "result = paper_audit_analyze('Sample content', 'standard'); print(f'Keys: {list(result.keys()) if isinstance(result, dict) else \"error\"}')",
        "Paper audit: paper_audit_analyze",
        timeout=20,
    )

    # Test 9: Playwright function registration (won't actually test execution)
    test9_pass, _ = run_monty_test(
        "import json; funcs = json.dumps({{k: v.__name__ if hasattr(v, '__name__') else str(v) for k, v in locals().items()}}); print('Playwright' in funcs if 'playwright_navigate' in str(funcs) else 'Missing')",
        "Playwright function availability check",
        timeout=10,
    )

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    tests = [
        ("List functions", test1_pass),
        ("Basic execution", test2_pass),
        ("Utility: len", test3_pass),
        ("Utility: type", test4_pass),
        ("News: fetch_hackernews", test5_pass),
        ("File: write_file", test6_pass),
        ("File: read_file", test7_pass),
        ("Paper audit: analyze", test8_pass),
        ("Playwright: availability", test9_pass),
    ]

    passed = sum(1 for _, p in tests if p)
    total = len(tests)

    print(f"\n  Total: {passed}/{total} tests passed")

    for name, pass_status in tests:
        status = "✅ PASS" if pass_status else "❌ FAIL"
        print(f"  {status}: {name}")

    # Exit code
    if passed == total:
        print("\n  🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
