---
name: baidu-ocr
description: 将用户指定的 PDF 或图片一次性转换为书籍式 OCR 文档包，包含视觉 HTML、结构化 Markdown、逐页图片、抽取资源和 JSON 版面数据。
---

# Baidu OCR Expert

## 目标

把 PDF 或图片当作整本文档处理，而不是返回一段散乱文字。默认使用 PP-StructureV3 做版面理解，并在同一次运行中生成可移动、可归档的完整输出目录。

## 使用规则

- 用户指定 PDF 或图片后，只执行一次 `tools/baidu-ocr-tool/agent_client.py`，等待它完成。
- 不要先统计页数、逐页转图、逐页 OCR 或手工拼接 Markdown；执行器会在同一个进程中完成。
- 默认使用 `book` 模式和 `gpu:0`，生成 `book.html`、Markdown、JSON、逐页 PNG 和抽取资源。
- 只有用户明确要求“只要文字/快速识别”时才传递 `--mode text`；只有用户明确不需要视觉 HTML 时才使用 `--mode document`。
- 当输入路径含空格时保留引号；优先传递用户给出的绝对路径。
- GPU 后端不可用时必须让执行器明确失败，不要默默改用 CPU；只有用户明确允许时才传递 `--allow-cpu-fallback`。

## 输出

```text
<文件名>_ocr/
├─ <文件名>.md          # 可编辑的结构化文本
├─ <文件名>.json        # 区块、文字、坐标、置信度和原始元数据
├─ book.html            # 原页视觉底稿 + 可搜索 OCR 文字层
├─ manifest.json
├─ pages/               # 每页完整 PNG
├─ assets/              # 图片、表格、公式等资源
└─ ocr.log              # 诊断日志（如有）
```

`book.html` 以原页图片作为视觉底稿，默认保持书本版面；页面中的 OCR 文字层透明但可搜索、复制，也可打开显示以检查定位框。Markdown 用于语义阅读和编辑，JSON 用于坐标和版面数据。

GPU 运行需要与当前机器和驱动匹配的 Paddle GPU/ROCm 运行时；执行器默认请求 `gpu:0`，并会把实际设备写入摘要、清单和 JSON。

## 完成回复

执行器成功时，直接返回摘要中的 `markdown` 和 `html` 路径，并报告页数、资源数和是否降级。不要把整本 OCR 文本复制到聊天中。失败时说明错误，不要自行拆分成多次逐页调用。
