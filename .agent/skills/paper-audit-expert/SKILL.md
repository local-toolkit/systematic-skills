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
- Must follow the `research_audit_protocol_v2026` strictly.
- Must generate SVG/Mermaid for system architecture.
- Must not hallucinate data; use [INSUFFICIENT_DATA] if missing.

## 2. Operation Sets

### 2.1 Audit Workflow (The "The Audit")
This is the primary operation. It consists of 4 sequential steps.

#### Step 1: Ingestion
Read the target PDF.
- If `pdftotext` is available: `pdftotext -layout <pdf_path> -`
- Warning: If file is scanned image, OCR is required (ask user if not available).

#### Step 2: 鍒嗘瀽 (The Prompt)
浣跨敤 **Research Audit Protocol** (PromptA) 鍒嗘瀽鏂囨湰銆?
**瑙掕壊**: 棣栧腑瀛︽湳瀹¤鍛?(Chief Academic Auditor)
**鐩爣**: 涓ユ牸鎵ц鈥滀笁娆￠槄璇绘硶鈥濆苟鐢熸垚楂樿川閲忓璁℃姤鍛娿€?
**鎵ц璇︽儏 (PromptA鍐呭瑕佹眰)**:
1.  **绗竴閬嶉槄璇伙細蹇€熺粨鏋勭悊瑙?(First Reading)**
    - **璁烘枃绫诲瀷**: (鐞嗚/绯荤粺/瀹為獙/搴旂敤/娴嬮噺)銆?    - **鏍稿績璐＄尞**: 绠€杩拌鏂囩殑涓昏鍒涙柊鐐?(涓嶈秴杩?5 鏉?銆?    - **鏍稿績瑙ｅ喅鐨勯棶棰?*: 璁烘枃璇曞浘瑙ｅ喅鐨勬牴鏈棝鐐广€?    - **鍦ㄥ凡鏈夌爺绌朵腑鐨勪綅缃?*: 涓庡墠浜哄伐浣滅殑鍖哄埆 (鏀硅繘浜?鏇夸唬浜?琛ュ厖浜?銆?2.  **绗簩閬嶉槄璇伙細鏍稿績鍐呭鎻愮偧 (Second Reading)**
    - **鏁翠綋妗嗘灦**: 璁烘枃鐨勯€昏緫缁勭粐缁撴瀯銆?    - **鍏抽敭鏂规硶涓庢ā鍧?*: 鏍稿績绠楁硶銆佸疄楠岃璁℃垨绯荤粺妯″潡銆?    - **鏈€閲嶈鐨勫浘琛?瀹為獙缁撴灉**: 鍏抽敭鏁版嵁鏀寔鍙婂叾璇佹槑浜嗕粈涔堛€?    - **渚濊禆鐨勫墠鎻愬亣璁?*: 璁烘枃鎴愮珛鐨勮竟鐣屼笌闅愭€у亣璁俱€?3.  **绗笁閬嶉槄璇伙細浜茶嚜闃呰浠峰€煎垽鏂?(Third Reading Judgement)**
    - **蹇呴』浜茶嚜绮捐鐨勯儴鍒?*: 鐞嗙敱鍙婂叧閿皬鑺傘€?    - **鍙互鍙湅鎬荤粨鐨勯儴鍒?*: 鐞嗙敱鍙婇潪鏍稿績灏忚妭銆?    - **澶嶇幇/鏀硅繘/寮曠敤鏃朵笉鍙烦杩囩殑缁嗚妭**: 鍏抽敭鍏紡銆佸弬鏁般€佹鍒欐垨鐗规畩绛栫暐銆?4.  **鐮旂┒浠峰€艰瘎浼?(Research Value Assessment)**
    - **浼樺娍**: 璁烘枃鐨勬牳蹇冧寒鐐广€?    - **娼滃湪椋庨櫓鎴栧眬闄?*: 灞€闄愭€ф垨鏈В鍐崇殑闂銆?    - **鍚彂鏂瑰悜**: 瀵规湭鏉ョ爺绌舵垨宸ョ▼瀹炶返鐨勫惎鍙戙€?
#### Step 3: 鍙鍖栦笌褰掓。 (Visualization & Archival)
1.  **鐢熸垚 SVG**: 鍒涘缓涓€涓珮璐ㄩ噺銆佸彲闃呰鐨?*妯悜涓夊眰缁撴瀯绯荤粺鏋舵瀯鍥?*銆?    - 鍥捐〃蹇呴』鍖呭惈锛氬乏渚ц緭鍏ュ眰銆佷腑闂村鐞?閫昏緫灞傘€佸彸渚ц緭鍑?鎴愬搧灞傘€?    - 椋庢牸闇€涓撲笟銆佸鏈笖鏄撲簬闃呰銆?2.  **鍒涘缓绗旇**: 涓ユ牸鎸夌収涓婅堪鍥涗釜闃舵锛堜竴銆佷簩銆佷笁銆佸洓锛夌粍缁?Markdown銆?    - 鏂囦欢鍚嶆牸寮? `tools/paper_audit/notes/<Paper_Title>.md`銆?    - 蹇呴』鍖呭惈 YAML 鍏冩暟鎹€?    - 鍦ㄦ鏂囦腑宓屽叆璇ユ灦鏋勫浘銆?3.  **绉诲姩 PDF**: 灏嗗師濮?PDF 浠?`inbox` 绉诲姩鍒?`completed`銆?
#### Step 4: Execution via Tool
Trigger the archiving logic via:
`python3 paper-audit-tool/agent_client.py "Move processed paper.pdf to completed"`

## 3. Error Handling
- **PDF Read Error**: If text is garbage, abort and notify user "OCR Required".
- **Missing Metadata**: If YAML fields (authors, year) are not found, use "Unknown" but do not fail.

## 4. Usage Examples

"Please audit the paper 'attention_is_all_you_need.pdf' in the inbox."

-> Agent reads `tools/paper_audit/inbox/attention_is_all_you_need.pdf`.
-> Agent runs the protocol.
-> Agent saves `tools/paper_audit/notes/Attention Is All You Need.md`.
-> Agent moves PDF to `tools/paper_audit/completed/attention_is_all_you_need.pdf`.
