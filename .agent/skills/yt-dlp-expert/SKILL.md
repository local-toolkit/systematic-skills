---
name: yt-dlp
version: 2026.01.23
description: 工业级媒体提取协议。强制执行依赖校验与流选择逻辑，杜绝无效参数组合。
status: active
type: execution
---

## 1. 环境先验条件 (Pre-conditions)
在执行任何下载指令前，必须确认以下环境状态：
* **核心依赖**：ffmpeg 版本需 ≥ 7.0 (用于多线程合并与 AV1 解码)。
* **网络路由**：若目标域名为 youtube.com 或 twitch.tv，默认启用流量分片 `--http-chunk-size 10M`。
* **版本状态**：强制调用 `yt-dlp -U` 确保 PoS (Proof of Service) 绕过逻辑为最新。

## 2. 逻辑约束与冲突预防 (Constraints)
Agent 必须遵守以下互斥与依赖规则：
* **嵌入行为依赖**：使用 `--embed-subs` 或 `--embed-metadata` 时，必须显式指定 `--merge-output-format` 为 mkv 或 mp4。
* **音频提取约束**：使用 `-x` (extract-audio) 时，必须配合 `--audio-quality 0`，且优先使用 `--audio-format opus` (流媒体原生最优)。
* **Cookie 安全协议**：严禁直接在 CLI 传递明文 Cookie 字符串。仅允许使用 `--cookies-from-browser` 或指向受保护的 `.txt` 文件路径。

## 3. 高颗粒度操作指令集 (Operation Sets)

### 3.1 极致画质优先策略 (8K/HDR/AV1)
* **逻辑描述**：优先匹配最高分辨率，同时强制过滤无效的原始数据流。
* **指令模板**：
  `yt-dlp -f "bv*[vcodec^=av01]+ba/bv+ba/b" --unbuffered --check-formats`

### 3.2 生产级视频转换协议 (MP4 兼容)
* **逻辑描述**：由于 YouTube 默认提供 WebM/VP9，需强制重封装并对齐元数据。
* **指令模板**：
  `yt-dlp -f "bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]" --merge-output-format mp4 --add-metadata --convert-subs srt`

### 3.3 自动化队列管理
* **逻辑描述**：针对播单下载，强制开启原子性记录，防止中断后重复下载。
* **核心参数**：
  * `--download-archive archive.txt` (状态持久化)
  * `--break-on-existing` (遇重即止)
  * `-o "%(uploader)s/%(upload_date)s - %(title)s.%(ext)s"` (结构化存储)

## 4. 故障自愈决策树 (Error Handling)
当 Agent 接收到 stderr 时，需按以下逻辑重试：
* **状态码 403**：立即尝试 `--rm-cache-dir` 之后切换 `--client-name web_creator`。
* **由于内容受限无法解析**：触发 `--cookies-from-browser` 引导流程。
* **FFmpeg 缺失**：停止执行并提示用户安装 `media-video/ffmpeg`。

## 5. Python 实例化规范
当以库形式调用时，ydl_opts 字典必须包含 `postprocessor_args` 以处理 2026 年新增的加密流。
```python
ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    'concurrent_fragment_downloads': 10, # 2026 标准：多线程下载
    'postprocessor_args': {
        'ffmpeg': ['-threads', '4', '-movflags', 'faststart']
    },
    'quiet': False,
    'no_warnings': False
}
```