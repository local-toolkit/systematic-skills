---
name: yt-dlp
version: 2026.01.23
description: 工业级媒体提取协议。强制执行依赖校验与流选择逻辑，杜绝无效参数组合。
status: active
type: execution
---

# yt-dlp Expert Skill

Media extraction expert using `yt-dlp`.

## Agent Instructions

### Security & critical Constraints

- **Cookies**: NEVER pass cookies as strings. Use `--cookies-from-browser` (chrome/firefox) or `--cookies-file` (path to .txt).
- **Audio Extraction**: When requesting audio (`-x`), ALWAYS set `--audio-quality 0` and prefer `--audio-format opus`.
- **Embeds**: If using `--embed-subs` or `--embed-metadata`, MUST set `--merge-output-format` to `mkv` or `mp4`.

### Operation Sets

#### 1. Best Quality (8K/HDR)

`--format "bv*[vcodec^=av01]+ba/bv+ba/b"`

#### 2. Compatibility (MP4)

`--format "bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]" --merge-output-format mp4`

#### 3. Playlist Management

- Use `--download-archive` to prevent duplicates.
- Use `--playlist-items` to select specific videos (e.g. "1,2,5-10").

### Error Handling

- **403 Forbidden**: Signal need for cookies or cache clear (`--rm-cache-dir`).
- **Sign-in Required**: Use `--cookies-from-browser`.
