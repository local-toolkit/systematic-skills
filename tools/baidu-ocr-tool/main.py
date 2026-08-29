#!/usr/bin/env python
"""One-shot local OCR for PDFs and images.

The default book workflow is intentionally end-to-end:

    ocr.py book.pdf

It renders PDF pages, runs layout-aware OCR when the PP-StructureV3 extras are
available, falls back to PP-OCRv6 text OCR when they are not, and writes a
portable visual HTML book, Markdown document, page images, extracted image
assets, and JSON metadata into one output directory.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import os
import re
import sys
import tempfile
from html import escape as html_escape
from pathlib import Path
from typing import Any, Callable, Iterable


# Keep model-source probing quiet and avoid the known Windows oneDNN issue. The
# pipeline is still allowed to download missing models on its first run.
os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")
os.environ.setdefault("PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT", "False")

# PP-StructureV3 lazily renders annotated images and otherwise downloads a
# large CJK font after inference. Prefer a local font when one is available,
# but do not assume the repository belongs to a particular user or OS.
if not os.environ.get("PADDLE_PDX_LOCAL_FONT_FILE_PATH"):
    _font_candidates = [
        Path.home() / ".paddlex" / "fonts" / "PingFang-SC-Regular.ttf",
        Path("C:/Windows/Fonts/simfang.ttf"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
    ]
    for _font_candidate in _font_candidates:
        if _font_candidate.is_file():
            os.environ["PADDLE_PDX_LOCAL_FONT_FILE_PATH"] = str(_font_candidate)
            break

IMAGE_EXTENSIONS = {".bmp", ".dib", ".jpeg", ".jpg", ".png", ".webp", ".pbm", ".pgm", ".ppm", ".pnm", ".tif", ".tiff"}
PDF_EXTENSIONS = {".pdf"}
DEFAULT_RENDER_SCALE = 2.0
MAX_RENDER_PIXELS = 178_956_970
SCHEMA_VERSION = "3.0"


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def _safe_name(value: str, fallback: str = "asset") -> str:
    """Make a filename safe on Windows, macOS, and Linux."""

    value = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", value)
    value = value.strip(" .")
    return value or fallback


def _json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    if hasattr(value, "tolist"):
        return value.tolist()
    return str(value)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=_json_default),
        encoding="utf-8",
    )


def _result_payload(result: Any) -> dict[str, Any]:
    """Read PaddleX/PaddleOCR result JSON without depending on one wrapper."""

    value = getattr(result, "json", None)
    if callable(value):
        value = value()
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, dict):
        return {}
    payload = value.get("res", value)
    return payload if isinstance(payload, dict) else {}


def _save_image_object(image: Any, path: Path) -> None:
    """Save a PIL/numpy/Paddle image object as a portable PNG."""

    from PIL import Image

    if image is None:
        raise ValueError("image object is empty")
    if hasattr(image, "to_pil"):
        image = image.to_pil()
    if not isinstance(image, Image.Image):
        image = Image.fromarray(image)
    if image.mode not in {"RGB", "RGBA"}:
        image = image.convert("RGB")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")


def _render_pdf_pages(input_path: Path, pages_dir: Path, requested_scale: float) -> list[Path]:
    """Render every PDF page once so OCR and Markdown use identical page images."""

    import pypdfium2 as pdfium

    if requested_scale <= 0:
        raise ValueError("--render-scale must be greater than 0")

    pages_dir.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(input_path))
    page_paths: list[Path] = []
    try:
        for index in range(len(document)):
            page = document[index]
            bitmap = None
            try:
                width_pt, height_pt = page.get_size()
                scale = requested_scale
                estimated_pixels = float(width_pt) * float(height_pt) * scale * scale
                if estimated_pixels > MAX_RENDER_PIXELS:
                    scale = math.sqrt(MAX_RENDER_PIXELS / (float(width_pt) * float(height_pt)))
                bitmap = page.render(scale=scale)
                output_path = pages_dir / f"page-{index + 1:04d}.png"
                _save_image_object(bitmap.to_pil(), output_path)
                page_paths.append(output_path)
            finally:
                close_bitmap = getattr(bitmap, "close", None)
                if close_bitmap:
                    close_bitmap()
                close_page = getattr(page, "close", None)
                if close_page:
                    close_page()
    finally:
        close_document = getattr(document, "close", None)
        if close_document:
            close_document()

    if not page_paths:
        raise ValueError(f"PDF has no readable pages: {input_path}")
    return page_paths


def _normalize_image_pages(input_path: Path, pages_dir: Path) -> list[Path]:
    """Normalize one image or a multi-frame TIFF into page PNGs."""

    from PIL import Image

    pages_dir.mkdir(parents=True, exist_ok=True)
    page_paths: list[Path] = []
    with Image.open(input_path) as source:
        frame_count = int(getattr(source, "n_frames", 1) or 1)
        for index in range(frame_count):
            if frame_count > 1:
                source.seek(index)
            frame = source.convert("RGB")
            output_path = pages_dir / f"page-{index + 1:04d}.png"
            frame.save(output_path, format="PNG")
            page_paths.append(output_path)
    return page_paths


def _prepare_pages(input_path: Path, pages_dir: Path, render_scale: float) -> list[Path]:
    if input_path.suffix.lower() in PDF_EXTENSIONS:
        return _render_pdf_pages(input_path, pages_dir, render_scale)
    return _normalize_image_pages(input_path, pages_dir)


def _quiet_call(function: Callable[[], Any], logs: list[str]) -> Any:
    """Capture noisy Paddle progress output so stdout stays machine-readable."""

    buffer = io.StringIO()
    native_capture = tempfile.TemporaryFile(mode="w+b")
    saved_stdout = os.dup(sys.stdout.fileno())
    saved_stderr = os.dup(sys.stderr.fileno())
    error: BaseException | None = None
    value: Any = None
    try:
        sys.stdout.flush()
        sys.stderr.flush()
        # Some Paddle/Windows dependency checks write from a child process and
        # bypass contextlib.redirect_stdout. Redirect the OS handles as well.
        os.dup2(native_capture.fileno(), sys.stdout.fileno())
        os.dup2(native_capture.fileno(), sys.stderr.fileno())
        try:
            with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                value = function()
        except BaseException as exc:
            error = exc
    finally:
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        finally:
            os.dup2(saved_stdout, sys.stdout.fileno())
            os.dup2(saved_stderr, sys.stderr.fileno())
            os.close(saved_stdout)
            os.close(saved_stderr)
    native_capture.seek(0)
    native_text = native_capture.read().decode("utf-8", errors="replace")
    native_capture.close()
    captured = buffer.getvalue() + native_text
    if captured.strip():
        logs.append(captured)
    if error is not None:
        raise error
    return value


def _missing_structure_dependencies() -> list[str]:
    try:
        from paddlex.utils.deps import EXTRAS, is_dep_available

        return [name for name in EXTRAS.get("ocr", {}) if not is_dep_available(name)]
    except Exception:
        # The actual constructor below remains the source of truth. This only
        # avoids a guaranteed failed attempt when the optional extra is absent.
        return ["paddlex[ocr]"]


def _run_structure_ocr(page_paths: list[Path], args: argparse.Namespace) -> list[Any]:
    """Run one layout-aware pipeline over all pages."""

    from paddleocr import PPStructureV3

    model = f"PP-OCRv6_{args.model}"
    pipeline = PPStructureV3(
        text_detection_model_name=f"{model}_det",
        text_recognition_model_name=f"{model}_rec",
        # Document input benefits from orientation/unwarping and line-angle
        # handling; tables and formulas become Markdown/LaTeX blocks.
        use_doc_orientation_classify=True,
        use_doc_unwarping=True,
        use_textline_orientation=True,
        use_table_recognition=True,
        use_formula_recognition=True,
        use_chart_recognition=False,
        use_region_detection=True,
        # Keep headers/footers instead of silently dropping source content.
        markdown_ignore_labels=[],
        device=args.device,
        enable_mkldnn=False,
    )
    return list(
        pipeline.predict(
            [str(path) for path in page_paths],
            text_rec_score_thresh=args.min_score,
        )
    )


def _run_basic_ocr(page_paths: list[Path], args: argparse.Namespace) -> list[Any]:
    """Run one fast PP-OCRv6 pipeline over all pages."""

    from paddleocr import PaddleOCR

    model = f"PP-OCRv6_{args.model}"
    pipeline = PaddleOCR(
        text_detection_model_name=f"{model}_det",
        text_recognition_model_name=f"{model}_rec",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        enable_mkldnn=False,
        device=args.device,
    )
    return list(
        pipeline.predict(
            [str(path) for path in page_paths],
            text_rec_score_thresh=args.min_score,
        )
    )


def _basic_page_data(result: Any, page_number: int, min_score: float) -> dict[str, Any]:
    raw = _result_payload(result)
    texts = list(raw.get("rec_texts") or [])
    scores = list(raw.get("rec_scores") or [])
    boxes = list(raw.get("rec_boxes") or [])
    lines: list[dict[str, Any]] = []
    for index, value in enumerate(texts):
        text = "" if value is None else str(value)
        if not text:
            continue
        score = None
        if index < len(scores):
            try:
                score = float(scores[index])
            except (TypeError, ValueError):
                score = None
        if score is not None and score < min_score:
            continue
        box = boxes[index] if index < len(boxes) else None
        lines.append({"text": text, "score": score, "box": box})

    raw["page_index"] = page_number - 1
    return {
        "page": page_number,
        "text": "\n".join(item["text"] for item in lines),
        "markdown": "\n".join(item["text"] for item in lines),
        "lines": lines,
        "raw": raw,
        "markdown_images": {},
    }


def _structure_markdown(result: Any) -> dict[str, Any]:
    try:
        return result._to_markdown(pretty=False)
    except AttributeError:
        value = getattr(result, "markdown", {})
        return value if isinstance(value, dict) else {}


def _ocr_lines_from_payload(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract OCR lines used by the HTML text layer.

    PP-StructureV3 nests its OCR result under ``overall_ocr_res`` while the
    basic PaddleOCR result exposes the same fields at the top level. Keeping
    this adapter here makes both pipelines produce the same portable schema.
    """

    source = raw.get("overall_ocr_res")
    if not isinstance(source, dict):
        source = raw
    texts = list(source.get("rec_texts") or [])
    scores = list(source.get("rec_scores") or [])
    boxes = list(source.get("rec_boxes") or [])
    lines: list[dict[str, Any]] = []
    for index, value in enumerate(texts):
        text = "" if value is None else str(value).strip()
        if not text:
            continue
        score = None
        if index < len(scores):
            try:
                score = float(scores[index])
            except (TypeError, ValueError):
                score = None
        box = boxes[index] if index < len(boxes) else None
        lines.append({"text": text, "score": score, "box": box})
    return lines


def _image_size(path: Path) -> tuple[int, int]:
    from PIL import Image

    with Image.open(path) as image:
        return int(image.width), int(image.height)


def _normalized_box(box: Any) -> list[float] | None:
    """Convert Paddle's xyxy or four-point box into [left, top, right, bottom]."""

    if hasattr(box, "tolist"):
        box = box.tolist()
    if not isinstance(box, (list, tuple)):
        return None

    # Most PP-OCR results use [x1, y1, x2, y2].
    if len(box) == 4 and all(not isinstance(value, (list, tuple)) for value in box):
        try:
            x1, y1, x2, y2 = (float(value) for value in box)
        except (TypeError, ValueError):
            return None
    else:
        points: list[tuple[float, float]] = []
        for point in box:
            if hasattr(point, "tolist"):
                point = point.tolist()
            if not isinstance(point, (list, tuple)) or len(point) < 2:
                continue
            try:
                points.append((float(point[0]), float(point[1])))
            except (TypeError, ValueError):
                continue
        if not points:
            return None
        x1 = min(point[0] for point in points)
        y1 = min(point[1] for point in points)
        x2 = max(point[0] for point in points)
        y2 = max(point[1] for point in points)

    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1
    if x2 <= x1 or y2 <= y1:
        return None
    return [x1, y1, x2, y2]


def _structure_page_data(result: Any, page_number: int) -> dict[str, Any]:
    raw = _result_payload(result)
    markdown_data = _structure_markdown(result)
    markdown_text = str(markdown_data.get("markdown_texts") or "").strip()
    blocks = raw.get("parsing_res_list") or []
    text_parts: list[str] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        value = block.get("block_content")
        if value is not None and str(value).strip():
            text_parts.append(str(value).strip())
    raw["page_index"] = page_number - 1
    return {
        "page": page_number,
        "text": "\n".join(text_parts),
        "markdown": markdown_text,
        "lines": _ocr_lines_from_payload(raw),
        "blocks": blocks,
        "raw": raw,
        "markdown_images": markdown_data.get("markdown_images") or {},
    }


def _materialize_assets(
    markdown: str,
    image_map: dict[str, Any],
    assets_dir: Path,
    page_number: int,
) -> tuple[str, list[dict[str, str]]]:
    assets: list[dict[str, str]] = []
    for index, (source_name, image) in enumerate(image_map.items(), start=1):
        source_text = str(source_name)
        source_stem = Path(source_text.replace("\\", "/")).stem
        filename = f"page-{page_number:04d}-{index:03d}-{_safe_name(source_stem)}.png"
        target = assets_dir / filename
        try:
            _save_image_object(image, target)
        except Exception:
            continue
        relative_path = f"assets/{filename}"
        markdown = markdown.replace(source_text, relative_path)
        assets.append({"source": source_text, "path": relative_path})
    return markdown, assets


def _save_annotation(result: Any, annotated_dir: Path, page_number: int, structure: bool) -> str | None:
    try:
        images = getattr(result, "img", {})
        if not isinstance(images, dict):
            return None
        preferred = ["layout_order_res", "overall_ocr_res"] if structure else ["ocr_res_img"]
        selected = next((images[key] for key in preferred if key in images), None)
        if selected is None:
            return None
        filename = f"page-{page_number:04d}-annotated.png"
        _save_image_object(selected, annotated_dir / filename)
        return f"annotated/{filename}"
    except Exception:
        return None


def _build_markdown(
    title: str,
    source_name: str,
    pipeline_name: str,
    model_name: str,
    pages: list[dict[str, Any]],
    fallback_reason: str | None,
    html_name: str | None,
) -> str:
    lines = [
        f"# {title}",
        "",
        f"> 来源文件：`{source_name}`",
        f"> OCR 管线：`{pipeline_name}`",
        f"> OCR 模型：`{model_name}`",
        f"> 页数：{len(pages)}",
    ]
    if html_name:
        lines.append(f"> 版面阅读：[`{html_name}`]({html_name})（原页图 + 可搜索 OCR 层）")
    if fallback_reason:
        lines.append("> 说明：结构化管线不可用，本次使用基础 OCR；页面图片与逐行识别结果仍已完整保存。")
    lines.extend(["", "## 页面索引", ""])
    for page in pages:
        number = page["page"]
        lines.append(f"- [第 {number} 页](#第-{number}-页)")

    for page in pages:
        number = page["page"]
        page_image = f"pages/page-{number:04d}.png"
        content = str(page.get("markdown") or "").strip()
        lines.extend(["", f"## 第 {number} 页", "", f"![第 {number} 页]({page_image})", ""])
        lines.append(content if content else "*本页未识别到文字。*")

    return "\n".join(lines).rstrip() + "\n"


def _build_book_html(
    title: str,
    source_name: str,
    pipeline_name: str,
    model_name: str,
    pages: list[dict[str, Any]],
    markdown_name: str,
    json_name: str,
) -> str:
    """Build a portable visual book with a selectable OCR text layer.

    The page PNG is the visual source of truth, so typography, columns,
    illustrations, stamps, and page furniture remain faithful to the scan.
    OCR lines are positioned over that image and transparent by default; a
    checkbox can reveal them for visual debugging while browser search/copy
    still sees the text.
    """

    nav_items: list[str] = []
    page_sections: list[str] = []
    for page in pages:
        number = int(page.get("page") or 0)
        page_id = f"page-{number:04d}"
        nav_items.append(
            f'<a class="page-link" href="#{page_id}">第 {number} 页</a>'
        )

        width = max(1, int(page.get("width") or 1))
        height = max(1, int(page.get("height") or 1))
        text_spans: list[str] = []
        for line in page.get("lines") or []:
            if not isinstance(line, dict):
                continue
            text = str(line.get("text") or "").strip()
            rect = _normalized_box(line.get("box"))
            if not text or rect is None:
                continue
            x1, y1, x2, y2 = rect
            x1 = max(0.0, min(float(width), x1))
            y1 = max(0.0, min(float(height), y1))
            x2 = max(0.0, min(float(width), x2))
            y2 = max(0.0, min(float(height), y2))
            if x2 <= x1 or y2 <= y1:
                continue
            left = x1 / width * 100.0
            top = y1 / height * 100.0
            box_width = (x2 - x1) / width * 100.0
            box_height = (y2 - y1) / height * 100.0
            # cqw scales with the page container, keeping the overlay aligned
            # when the browser resizes the page.
            font_size = max(0.25, min(8.0, (y2 - y1) / width * 75.0))
            score = line.get("score")
            score_text = ""
            if score is not None:
                try:
                    score_text = f" title=\"置信度 {float(score):.3f}\""
                except (TypeError, ValueError):
                    pass
            style = (
                f"left:{left:.5f}%;top:{top:.5f}%;"
                f"width:{box_width:.5f}%;height:{box_height:.5f}%;"
                f"font-size:{font_size:.5f}cqw;"
            )
            escaped_text = html_escape(text, quote=True)
            text_spans.append(
                f'<span class="ocr-line" style="{style}"{score_text} '
                f'aria-label="{escaped_text}">{escaped_text}</span>'
            )

        page_image = html_escape(str(page.get("page_image") or ""), quote=True)
        page_alt = html_escape(f"第 {number} 页原始版面", quote=True)
        structured = str(page.get("markdown") or "").strip()
        details = ""
        if structured:
            details = (
                '<details class="structured-text">'
                "<summary>查看本页结构化 Markdown</summary>"
                f"<pre>{html_escape(structured, quote=False)}</pre>"
                "</details>"
            )
        annotation = page.get("annotated_image")
        annotation_link = ""
        if annotation:
            safe_annotation = html_escape(str(annotation), quote=True)
            annotation_link = (
                f' <a href="{safe_annotation}">查看版面标注图</a>'
            )
        page_sections.append(
            f'<section class="page-card" id="{page_id}">'
            f'<div class="page-heading"><span>第 {number} 页</span>'
            f'<span class="page-tools"><a href="{page_image}">打开原页图</a>'
            f"{annotation_link}</span></div>"
            f'<div class="book-page" style="--page-ratio:{width / height:.8f};">'
            f'<img class="page-image" src="{page_image}" alt="{page_alt}" '
            'loading="lazy">'
            f'<div class="ocr-layer" aria-label="第 {number} 页 OCR 文字层">'
            f"{''.join(text_spans)}"
            "</div></div>"
            f"{details}</section>"
        )

    escaped_title = html_escape(title, quote=True)
    escaped_source = html_escape(source_name, quote=True)
    escaped_pipeline = html_escape(pipeline_name, quote=True)
    escaped_model = html_escape(model_name, quote=True)
    escaped_markdown = html_escape(markdown_name, quote=True)
    escaped_json = html_escape(json_name, quote=True)
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title} · OCR 书籍版</title>
  <style>
    :root {{ color-scheme: light; --ink:#242424; --muted:#6b7280; --paper:#fff;
      --canvas:#ece9e4; --line:#d8d2c8; --accent:#315c8c; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; color:var(--ink); background:var(--canvas);
      font-family:system-ui,-apple-system,"Segoe UI","Noto Sans CJK SC",sans-serif; }}
    .visually-hidden {{ position:absolute; width:1px; height:1px; padding:0; margin:-1px;
      overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }}
    .toolbar {{ position:sticky; top:0; z-index:10; padding:12px 20px;
      background:rgba(255,255,255,.94); border-bottom:1px solid var(--line);
      backdrop-filter:blur(8px); }}
    .toolbar-inner {{ max-width:1160px; margin:0 auto; display:flex; gap:16px;
      align-items:center; flex-wrap:wrap; }}
    .toolbar a, .toolbar label {{ color:var(--accent); cursor:pointer; text-decoration:none; }}
    .toolbar a:hover, .toolbar label:hover {{ text-decoration:underline; }}
    .toolbar .meta {{ color:var(--muted); font-size:.9rem; margin-right:auto; }}
    .intro {{ max-width:1160px; margin:28px auto 20px; padding:0 20px; }}
    h1 {{ margin:0 0 8px; font-family:Georgia,"Noto Serif CJK SC",serif; font-weight:600; }}
    .intro p {{ margin:5px 0; color:var(--muted); font-size:.92rem; }}
    .toc {{ display:flex; gap:8px; flex-wrap:wrap; max-width:1160px; margin:0 auto 24px;
      padding:0 20px; }}
    .page-link {{ padding:5px 9px; border:1px solid var(--line); border-radius:999px;
      background:rgba(255,255,255,.7); color:var(--accent); text-decoration:none;
      font-size:.84rem; }}
    .page-link:hover {{ background:var(--paper); }}
    .book {{ max-width:1160px; margin:0 auto; padding:0 20px 60px; }}
    .page-card {{ margin:0 auto 34px; scroll-margin-top:75px; }}
    .page-heading {{ display:flex; justify-content:space-between; gap:16px; align-items:center;
      color:var(--muted); font-size:.88rem; margin:0 0 8px; }}
    .page-tools {{ display:flex; gap:12px; }}
    .page-tools a {{ color:var(--accent); text-decoration:none; }}
    .page-tools a:hover {{ text-decoration:underline; }}
    .book-page {{ position:relative; width:100%; container-type:inline-size;
      background:var(--paper); box-shadow:0 5px 24px rgba(47,38,26,.17);
      line-height:0; overflow:hidden; }}
    .page-image {{ display:block; width:100%; height:auto; margin:0; }}
    .ocr-layer {{ position:absolute; inset:0; pointer-events:none; }}
    .ocr-line {{ position:absolute; display:block; overflow:hidden; white-space:nowrap;
      line-height:1; color:transparent; user-select:text; pointer-events:auto;
      font-family:Arial,"Noto Sans CJK SC",sans-serif; }}
    #show-ocr:checked ~ .book .ocr-line {{ color:rgba(12,40,75,.86);
      background:rgba(220,238,255,.48); outline:1px solid rgba(49,92,140,.3); }}
    .structured-text {{ margin-top:10px; background:rgba(255,255,255,.72);
      border:1px solid var(--line); border-radius:6px; }}
    .structured-text summary {{ padding:8px 11px; color:var(--accent); cursor:pointer; }}
    .structured-text pre {{ overflow:auto; margin:0; padding:12px; white-space:pre-wrap;
      font:12px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace; }}
    @media (max-width:640px) {{ .toolbar {{ padding:10px 12px; }} .intro,.toc,.book {{ padding-left:12px; padding-right:12px; }}
      .page-heading {{ align-items:flex-start; }} .page-tools {{ flex-direction:column; gap:3px; }} }}
    @media print {{ .toolbar,.intro,.toc,.page-heading,.structured-text {{ display:none; }}
      body {{ background:#fff; }} .book {{ max-width:none; padding:0; }}
      .page-card {{ break-after:page; margin:0; }} .book-page {{ box-shadow:none; }} }}
  </style>
</head>
<body>
  <input class="visually-hidden" type="checkbox" id="show-ocr">
  <div class="toolbar"><div class="toolbar-inner">
    <span class="meta">书籍版 · {len(pages)} 页 · {escaped_pipeline} · {escaped_model}</span>
    <label for="show-ocr">显示 OCR 文字层</label>
    <a href="{escaped_markdown}">打开 Markdown</a>
    <a href="{escaped_json}">打开结构 JSON</a>
  </div></div>
  <header class="intro">
    <h1>{escaped_title}</h1>
    <p>来源：{escaped_source}</p>
    <p>页面原图是视觉底稿；默认隐藏文字层以保持原书观感，勾选“显示 OCR 文字层”可检查识别框并进行搜索/复制。</p>
  </header>
  <nav class="toc" aria-label="页面索引">{''.join(nav_items)}</nav>
  <main class="book">{''.join(page_sections)}</main>
</body>
</html>
'''


def _write_log(output_dir: Path, logs: Iterable[str]) -> Path | None:
    content = "\n".join(item.rstrip() for item in logs if item.strip())
    if not content.strip():
        return None
    path = output_dir / "ocr.log"
    path.write_text(content + "\n", encoding="utf-8", errors="replace")
    return path


def _absolute(path: Path) -> str:
    return str(path.resolve())


def _process(args: argparse.Namespace) -> tuple[dict[str, Any], str]:
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"input not found: {input_path}")
    if input_path.suffix.lower() not in IMAGE_EXTENSIONS | PDF_EXTENSIONS:
        raise ValueError("supported input types: PDF, PNG, JPG, BMP, WEBP, TIFF")

    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else input_path.parent / f"{_safe_name(input_path.stem)}_ocr"
    )
    pages_dir = output_dir / "pages"
    assets_dir = output_dir / "assets"
    annotated_dir = output_dir / "annotated"
    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)
    if args.annotated:
        annotated_dir.mkdir(parents=True, exist_ok=True)

    logs: list[str] = []
    page_paths = _prepare_pages(input_path, pages_dir, args.render_scale)

    requested_document = args.mode in {"book", "auto", "document"}
    book_mode = args.mode in {"book", "auto"}
    structure = False
    fallback_reason: str | None = None
    results: list[Any]

    if requested_document:
        missing = _quiet_call(_missing_structure_dependencies, logs)
        if missing:
            fallback_reason = "missing optional dependencies: " + ", ".join(missing)
        else:
            try:
                results = _quiet_call(lambda: _run_structure_ocr(page_paths, args), logs)
                structure = True
            except Exception as exc:
                fallback_reason = f"structured OCR failed: {type(exc).__name__}: {exc}"

    if not structure:
        results = _quiet_call(lambda: _run_basic_ocr(page_paths, args), logs)

    if len(results) != len(page_paths):
        raise RuntimeError(
            f"OCR returned {len(results)} page results for {len(page_paths)} input pages"
        )

    page_data: list[dict[str, Any]] = []
    asset_count = 0
    for page_number, result in enumerate(results, start=1):
        if structure:
            data = _quiet_call(
                lambda: _structure_page_data(result, page_number), logs
            )
        else:
            data = _basic_page_data(result, page_number, args.min_score)
        width, height = _image_size(page_paths[page_number - 1])
        data["page_image"] = f"pages/page-{page_number:04d}.png"
        data["width"] = width
        data["height"] = height
        data["markdown"], assets = _materialize_assets(
            data["markdown"], data.pop("markdown_images"), assets_dir, page_number
        )
        data["assets"] = assets
        asset_count += len(assets)
        if args.annotated:
            annotation = _quiet_call(
                lambda: _save_annotation(result, annotated_dir, page_number, structure),
                logs,
            )
            if annotation:
                data["annotated_image"] = annotation
        page_data.append(data)

    pipeline_name = "PP-StructureV3" if structure else "PaddleOCR"
    model_name = f"PP-OCRv6_{args.model}"
    markdown_name = f"{_safe_name(input_path.stem)}.md"
    json_name = f"{_safe_name(input_path.stem)}.json"
    html_name = "book.html" if book_mode else None
    markdown_path = output_dir / markdown_name
    json_path = output_dir / json_name
    markdown_text = _build_markdown(
        input_path.stem,
        input_path.name,
        pipeline_name,
        model_name,
        page_data,
        fallback_reason,
        html_name,
    )
    markdown_path.write_text(markdown_text, encoding="utf-8")

    html_path = None
    if html_name:
        html_path = output_dir / html_name
        html_path.write_text(
            _build_book_html(
                input_path.stem,
                input_path.name,
                pipeline_name,
                model_name,
                page_data,
                markdown_name,
                json_name,
            ),
            encoding="utf-8",
        )

    result_pages: list[dict[str, Any]] = []
    for data in page_data:
        result_pages.append(
            {key: value for key, value in data.items() if key != "markdown_images"}
        )
    result_document = {
        "schema_version": SCHEMA_VERSION,
        "source_file": input_path.name,
        "pipeline": pipeline_name,
        "model": model_name,
        "book_html": html_name,
        "pages": result_pages,
    }
    _write_json(json_path, result_document)

    log_path = _write_log(output_dir, logs)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "ok": True,
        "source_file": input_path.name,
        "requested_mode": args.mode,
        "effective_mode": "document" if structure else "text-fallback",
        "pipeline": pipeline_name,
        "model": model_name,
        "page_count": len(page_paths),
        "asset_count": asset_count,
        "fallback": bool(fallback_reason),
        "fallback_reason": fallback_reason,
        "files": {
            "markdown": markdown_name,
            "json": json_name,
            "html": html_name,
            "pages": "pages/",
            "assets": "assets/",
            "annotated": "annotated/" if args.annotated else None,
            "log": log_path.name if log_path else None,
        },
    }
    _write_json(output_dir / "manifest.json", manifest)

    summary = {
        "ok": True,
        "source": _absolute(input_path),
        "output_dir": _absolute(output_dir),
        "markdown": _absolute(markdown_path),
        "json": _absolute(json_path),
        "html": _absolute(html_path) if html_path else None,
        "pages_dir": _absolute(pages_dir),
        "assets_dir": _absolute(assets_dir),
        "pages": len(page_paths),
        "assets": asset_count,
        "pipeline": pipeline_name,
        "model": model_name,
        "fallback": bool(fallback_reason),
    }
    if args.format in {"text", "both"}:
        document_output = "\n".join(
            f"--- page {page['page']} ---\n{page['text']}" for page in page_data
        )
    else:
        document_output = json.dumps(
            result_document, ensure_ascii=False, indent=2, default=_json_default
        )
    return summary, document_output


def _emit_success(args: argparse.Namespace, summary: dict[str, Any], document_output: str) -> None:
    if args.format == "summary":
        print(json.dumps(summary, ensure_ascii=False))
    elif args.format in {"text", "json"}:
        print(document_output)
    else:
        print(document_output)
        print(json.dumps(summary, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    parser = argparse.ArgumentParser(
        description="One-shot local OCR: PDF/image -> book HTML + Markdown + page images + JSON"
    )
    parser.add_argument("input", help="PDF or image path")
    parser.add_argument(
        "--mode",
        choices=["book", "auto", "document", "text"],
        default="book",
        help="book=layout OCR + visual HTML; auto is a compatibility alias; text=fast OCR only",
    )
    parser.add_argument(
        "--model",
        choices=["tiny", "small", "medium"],
        default="medium",
        help="PP-OCRv6 tier: tiny, small, or medium (default: medium)",
    )
    parser.add_argument(
        "--format",
        choices=["summary", "text", "json", "both"],
        default="summary",
        help="stdout format; summary is a single machine-readable completion object",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="output folder; default is <input-folder>/<input-stem>_ocr",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="drop OCR lines below this confidence (default: keep all)",
    )
    parser.add_argument(
        "--render-scale",
        type=float,
        default=DEFAULT_RENDER_SCALE,
        help="PDF render scale relative to 72 DPI (default: 2.0)",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Paddle device, e.g. cpu or gpu:0 (default: cpu)",
    )
    parser.add_argument(
        "--annotated",
        action="store_true",
        help="also save one annotated OCR/layout image per page",
    )
    args = parser.parse_args(argv)

    try:
        summary, document_output = _process(args)
        _emit_success(args, summary, document_output)
        return 0
    except Exception as exc:
        error = {
            "ok": False,
            "error": type(exc).__name__,
            "message": str(exc),
        }
        print(json.dumps(error, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
