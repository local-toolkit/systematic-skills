---
name: paper-audit
description: rigorous academic auditing workflow for research papers, implementing Stanford 3-Pass method and Obsidisan archival.
status: active
type: execution
---

# Paper Audit Expert

Executes a rigorous "Chief Academic Auditor" protocol to analyze, visualize, and archive research papers.

## 1. Core Protocols

### 1.1 Pre-conditions

- **Input**: PDF files in `inbox` directory (default: `tools/paper_audit/inbox`)
- **Tools**: `pdftotext` (preferred) or basic text extraction
- **Output**: Markdown notes in `notes` directory, processed PDFs moved to `completed`

### 1.2 Operation Constraints

- **Language**: All output (Markdown notes, analysis, summaries) MUST be in **Simplified Chinese (简体中文)**.
- **Protocol**: Must follow the `research_audit_protocol_v2026` strictly.
- **Visualization**: Must generate a **high-quality, academic-style SVG** for the system architecture using a Python script. Do NOT use Mermaid for the final architecture diagram; use Python's `xml.etree.ElementTree` or similar to draw a custom "Horizontal 3-Layer System Architecture" SVG.
- **Integrity**: Must not hallucinate data; use [INSUFFICIENT_DATA] if missing.

## 2. Operation Sets

### 2.1 Audit Workflow (The "The Audit")

This is the primary operation. It consists of 4 sequential steps.

#### Step 1: Ingestion

Read the target PDF.

- If `pdftotext` or `fitz` (PyMuPDF) is available, extract full text.
- Warning: If file is scanned image, notify user that OCR is required.

#### Step 2: 分析 (The Prompt)

使用 **Research Audit Protocol** (PromptA) 分析文本。
**角色**: 首席学术审计员 (Chief Academic Auditor)
**目标**: 严格执行“三次阅读法”并生成高质量审计报告。
**执行详情 (PromptA内容要求)**:

1.  **第一遍阅读：快速结构理解 (First Pass)**
    - **论文类型**: (理论/系统/实验/应用/测量)。
    - **核心贡献**: 简述论文的主要创新点 (不超过 5 条)。
    - **核心解决的问题**: 论文试图解决的根本痛点。
    - **在已有研究中的位置**: 与前人工作的区别 (改进了? 替代了? 补充了?)。

2.  **第二遍阅读：核心内容提炼 (Second Pass)**
    - **整体框架**: 论文的逻辑组织结构。
    - **关键方法与模型**: 核心算法、实验设计或系统模块。
    - **最重要的图表/实验结果**: 关键数据支及其证明了什么。
    - **依赖的前提假设**: 论文成立的边界与隐性假设。

3.  **第三遍阅读：亲自阅读价值判断 (Third Pass)**
    - **必须亲自精读的部分**: 理由及关键小节。
    - **可以只看总结的部分**: 理由及非核心小节。
    - **复现/改进/引用时不可跳过的细节**: 关键公式、参数、正则或特殊策略。

4.  **研究价值评价 (Research Value Assessment)**
    - **优势**: 论文的核心亮点。
    - **潜在风险或局限**: 局限性或未解决的问题。
    - **启发方向**: 对未来研究或工程实践的启发。

#### Step 3: 可视化与归档 (Visualization & Archival)

1.  **生成 SVG (Python)**: 编写并运行 Python 脚本生成一个高质量、可阅读的 **横向三层结构系统架构图 (Horizontal 3-Layer System Architecture)**。
    - **必须包含**: 左侧输入层 (Input Layer)、中间处理/逻辑层 (Processing/Logic Layer)、右侧输出/成品层 (Output Layer)。
    - **样式**: 学术风格，配色专业 (e.g., light blue/gray backgrounds, clear strokes)，文字清晰 (Arial/Helvetica)。
    - **输出**: 保存为 `.svg` 文件在 `tools/paper_audit/notes/` 目录下。
2.  **创建笔记**: 严格按照上述四个阶段（一、二、三、四）组织 Markdown。
    - 文件名格式: `tools/paper_audit/notes/<Paper_Title>.md`。
    - 必须包含 YAML 元数据。
    - **必须** 在正文中嵌入生成的 SVG 架构图 (e.g., `![System Architecture](Paper_Title_architecture.svg)`).
3.  **移动 PDF**: 将原始 PDF 从 `inbox` 移动到 `completed`。

#### Step 4: Finalize

Ensure all files are in place and notify the user.
