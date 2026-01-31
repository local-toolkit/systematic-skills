---
name: vtt-recitation-expert
version: 1.0.0
description: Converts VTT subtitle files into Obsidian-friendly Markdown for recitation (with timestamps and segmentation).
status: active
type: execution
---

# VTT Recitation Converter

This skill converts video subtitle files (`.vtt`) into a clean, formatted Markdown document designed for recitation and language learning.

## Features

- **Timestamped**: Every sentence has a clickable timestamp (e.g., `**[00:12]**`).
- **Segmented**: Automatically groups text into manageable chunks.
- **Deduplicated**: Cleans up scrolling repeats common in YouTube auto-captions.

## Usage

To convert a file, execute the python script with the absolute path to the `.vtt` file.

```bash
python3 /Users/xujintao/Documents/workspace/systematic-skills/.agent/skills/vtt-recitation-expert/scripts/vtt_to_md.py "<ABSOLUTE_PATH_TO_VTT_FILE>"
```

### Examples

**Convert a single file:**

```bash
python3 /Users/xujintao/Documents/workspace/systematic-skills/.agent/skills/vtt-recitation-expert/scripts/vtt_to_md.py "/Users/xujintao/Downloads/video.en.vtt"
```

The tool will generate a new file in the same directory ending with `_obsidian.md`.
