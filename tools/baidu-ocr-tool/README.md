# Baidu OCR Tool

将 PDF 或图片一次性转换成书籍式 OCR 文档包。默认使用 PP-StructureV3 做版面理解，并同时保留原页视觉底稿和可搜索的 OCR 坐标层。

## 安装

```bash
python -m pip install -r tools/baidu-ocr-tool/requirements.txt
```

首次运行可能下载 PaddleOCR/PP-StructureV3 模型。

## 使用

统一 agent 会通过 `agent_client.py` 调用：

```bash
python tools/baidu-ocr-tool/agent_client.py "OCR /absolute/path/to/book.pdf"
```

也可以直接调用核心脚本：

```bash
python tools/baidu-ocr-tool/main.py /absolute/path/to/book.pdf
```

默认输出到输入文件旁的 `<文件名>_ocr/`，包含：

- `book.html`：原页图片 + 可搜索/可调试 OCR 文字层
- `<文件名>.md`：结构化 Markdown 和逐页图片
- `<文件名>.json`：版面区块、坐标、置信度和原始元数据
- `pages/`、`assets/`、`manifest.json` 和诊断日志

如果 PaddleOCR 不在当前 Python 中，可设置 `BAIDU_OCR_PYTHON` 指向已安装 PaddleOCR 的 Python 可执行文件。
