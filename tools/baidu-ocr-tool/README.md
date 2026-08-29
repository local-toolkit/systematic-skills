# Baidu OCR Tool

将 PDF 或图片一次性转换成书籍式 OCR 文档包。默认使用 PP-StructureV3 做版面理解、使用 `gpu:0` 推理，并同时保留原页视觉底稿和可搜索的 OCR 坐标层。

## 安装

```bash
python -m pip install -r tools/baidu-ocr-tool/requirements-gpu-nvidia.txt
```

GPU 运行必须安装与操作系统、Python 和 CUDA/ROCm 匹配的 Paddle GPU 包；基础依赖文件不会偷偷安装 CPU 版 Paddle。确实需要 CPU 时使用 `requirements-cpu.txt`，并在命令中显式添加 `--device cpu`。

首次运行可能下载 PaddleOCR/PP-StructureV3 模型。

## GPU 运行

`main.py` 默认使用 `gpu:0`，启动前会检查 Paddle 是否真的加载了 CUDA/ROCm 后端；检查失败会直接退出，不会静默改用 CPU。只有明确需要 CPU 时，才使用 `--device cpu` 或 `--allow-cpu-fallback`。

`requirements-gpu-nvidia.txt` 面向 NVIDIA CUDA 环境。AMD GPU 需要与操作系统匹配的 ROCm/Paddle 构建；如果当前平台没有兼容的 Paddle GPU 包，程序会保留诊断错误，不会把 CPU 结果冒充成 GPU 结果。

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

如果 GPU 后端不可用，程序会直接返回诊断错误；只有明确允许时才使用 `--allow-cpu-fallback`。
