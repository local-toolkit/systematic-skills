#!/usr/bin/env python3
"""Route a natural-language OCR request to the one-shot book converter."""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys


TOOL_DIR = Path(__file__).resolve().parent
TOOL_SCRIPT = TOOL_DIR / "main.py"
SUPPORTED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff",
}


def _python_executable() -> str:
    """Prefer a PaddleOCR environment while remaining portable."""

    configured = os.environ.get("BAIDU_OCR_PYTHON")
    candidates = [Path(configured)] if configured else []
    candidates.extend(
        [
            TOOL_DIR / "venv" / "Scripts" / "python.exe",
            TOOL_DIR / "venv" / "bin" / "python",
            Path.home() / "paddleocr_env" / "Scripts" / "python.exe",
            Path.home() / "paddleocr_env" / "bin" / "python",
        ]
    )
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def _query_tokens(query: str) -> list[str]:
    # Keep quoted paths with spaces intact, while still accepting a plain path.
    matches = re.findall(r'"([^"]+)"|\'([^\']+)\'|(\S+)', query)
    tokens: list[str] = []
    for quoted_double, quoted_single, bare in matches:
        token = quoted_double or quoted_single or bare
        tokens.append(token.strip().strip("\"'，。；,.;:"))
    return tokens


def _find_input(query: str) -> Path | None:
    candidates = [Path(query.strip().strip("\"'"))]
    candidates.extend(Path(token) for token in _query_tokens(query))
    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
        except OSError:
            continue
        if resolved.is_file() and resolved.suffix.lower() in SUPPORTED_EXTENSIONS:
            return resolved
    return None


def run_ocr(query: str) -> int:
    input_path = _find_input(query)
    if input_path is None:
        print(
            "ERROR: 请在请求中提供存在的 PDF/PNG/JPG/TIFF 文件路径。"
            "默认会生成 book.html、Markdown、JSON 和逐页图片。",
            file=sys.stderr,
        )
        return 2

    command = [_python_executable(), str(TOOL_SCRIPT), str(input_path)]
    result = subprocess.run(command, check=False)
    return int(result.returncode)


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python agent_client.py "OCR <absolute PDF path>"', file=sys.stderr)
        return 2
    return run_ocr(" ".join(sys.argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
