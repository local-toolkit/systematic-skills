---
name: paper-audit
description: Rigorous academic auditing workflow (Stanford 3-Pass + Obsidian Archival).
status: active
type: execution
---

# Paper Audit Expert

Executes "Chief Academic Auditor" protocol.

## 1. Protocols & Constraints

- **Language**: Simplified Chinese (简体中文).
- **Visualization**: Must generate **Python-based SVG** (No Mermaid) for "Horizontal 3-Layer System Architecture".
- **Integrity**: No hallucination.

## 2. Audit Workflow

### Step 1: Ingestion

- Extract full text (pdftotext/fitz). Alert if OCR needed.

### Step 2: The Audit (Analysis)

**Role**: Chief Academic Auditor.

1.  **First Pass (Structure)**: Type, Contribution, Problem, Novelty.
2.  **Second Pass (Content)**: Framework, Methods, Key Results, Assumptions.
3.  **Third Pass (Value)**: Precision reading of key sections.
4.  **Assessment**: Strengths, Limitations, Future heuristics.

### Step 3: Visualization & Archival

1.  **SVG Gen**: Use `tools/paper-audit-tool/academic_svg.py` -> `AcademicSVG` class.
    - Output: `.svg` in `notes/`.
2.  **Markdown**: Save to `notes/<Title>.md`. Must embed the SVG.
3.  **Move**: PDF `inbox` -> `completed`.
