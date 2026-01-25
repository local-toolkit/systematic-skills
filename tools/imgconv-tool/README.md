# imgconv Tool

Image conversion and processing tool using the [sunshineplan/imgconv](https://github.com/sunshineplan/imgconv) Go library.

## Features

- **Format Conversion**: Convert between JPEG, PNG, GIF, TIFF, BMP, WEBP formats
- **Image Resizing**: Resize by fixed dimensions or percentage while maintaining aspect ratio
- **Watermark Addition**: Add watermarks with configurable opacity and positioning
- **Image Splitting**: Split images horizontally or vertically into multiple parts

## Installation

### Prerequisites

- Go 1.21 or higher
- Python 3.x (for wrapper script)

### Build the Go binary

```bash
cd imgconv-tool
go mod tidy
go build -o bin/imgconv-wrapper cmd/main.go
```

Or use the Python wrapper which will build automatically if needed.

## Usage

### Command Line Interface

```bash
python main.py [OPTIONS]
```

### Actions

#### 1. Convert Image Format

```bash
python main.py --action convert --input image.png --output image.jpg --format jpeg
```

#### 2. Resize Image

```bash
# Resize to specific width (maintain aspect ratio)
python main.py --action resize --input photo.jpg --output small.jpg --width 800

# Resize to specific dimensions
python main.py --action resize --input photo.jpg --output thumbnail.jpg --width 128 --height 128

# Resize by percentage
python main.py --action resize --input photo.jpg --output half.jpg --percent 50
```

#### 3. Add Watermark

```bash
# Add watermark at random position with 50% opacity
python main.py --action watermark --input image.jpg --output watermarked.jpg --watermark logo.png --opacity 128 --random

# Add watermark at fixed position with offset
python main.py --action watermark --input image.jpg --output watermarked.jpg --watermark logo.png --offset-x 10 --offset-y 10
```

#### 4. Split Image

```bash
# Split horizontally into 3 parts
python main.py --action split --input long.png --output part_%d.png --split-parts 3 --split-mode horizontal

# Split vertically into 2 parts
python main.py --action split --input tall.jpg --output part_%d.jpg --split-parts 2 --split-mode vertical
```

### AI-Powered Usage via agent_client.py

```bash
# Natural language processing for image operations
python agent_client.py "Convert image.png to JPEG format"
python agent_client.py "Resize this photo to 800px wide"
python agent_client.py "Add a watermark to image.jpg with 50% transparency"
python agent_client.py "Split this long screenshot into 3 horizontal parts"
```

## Options

| Option | Description |
|--------|-------------|
| `--action` | Action to perform: `convert`, `resize`, `watermark`, `split` (required) |
| `--input` | Input image path (required) |
| `--output` | Output image path (optional, auto-generated if not specified) |
| `--format` | Target format: `jpeg`, `png`, `gif`, `tiff`, `bmp`, `webp` (for convert) |
| `--width` | Target width in pixels (for resize) |
| `--height` | Target height in pixels (for resize) |
| `--percent` | Resize percentage (for resize, e.g., 50 for 50%) |
| `--watermark` | Watermark image path (for watermark) |
| `--opacity` | Watermark opacity 0-255, default 128 (for watermark) |
| `--random` | Place watermark at random position (for watermark) |
| `--offset-x` | Watermark offset X from position (for watermark) |
| `--offset-y` | Watermark offset Y from position (for watermark) |
| `--split-parts` | Number of parts to split into (for split) |
| `--split-mode` | Split direction: `horizontal` or `vertical` (for split) |

## Examples

### Batch Convert PNG to JPEG

```bash
for f in *.png; do
    python main.py --action convert --input "$f" --output "${f%.png}.jpg" --format jpeg
done
```

### Create Thumbnails

```bash
python main.py --action resize --input large.jpg --output thumb.jpg --width 200 --height 200
```

### Add Watermark to All Images

```bash
for f in *.jpg; do
    python main.py --action watermark --input "$f" --output "marked_$f" --watermark logo.png --opacity 100 --random
done
```

### Split Long Screenshot

```bash
python main.py --action split --input screenshot.png --output split_%d.png --split-parts 5 --split-mode horizontal
```

## Supported Input Formats

- JPEG/JPG
- PNG
- GIF
- TIFF/TIF
- BMP
- WEBP
- PDF (as input only)

## Architecture

```
imgconv-tool/
├── agent_client.py    # AI-powered CLI with natural language processing
├── main.py           # Python wrapper for Go binary
├── cmd/
│   └── main.go       # Go binary implementation using imgconv library
├── bin/              # Compiled Go binary (auto-generated)
└── go.mod            # Go module dependencies
```

## Dependencies

### Go Dependencies
- [github.com/sunshineplan/imgconv](https://github.com/sunshineplan/imgconv) v1.1.14
- [github.com/disintegration/imaging](https://github.com/disintegration/imaging) (transitive)
- [github.com/pdfcpu/pdfcpu](https://github.com/pdfcpu/pdfcpu) (transitive)
- [github.com/hhrutter/tiff](https://github.com/hhrutter/tiff) (transitive)
- [github.com/HugoSmits86/nativewebp](https://github.com/HugoSmits86/nativewebp) (transitive)

### Python Dependencies
- requests (for agent_client.py)
- No additional dependencies for main.py

## License

This tool uses the imgconv library which is licensed under MIT. See the [imgconv repository](https://github.com/sunshineplan/imgconv) for details.
