#!/usr/bin/env python3
"""
imgconv tool - Python wrapper for imgconv Go library
This tool provides a command-line interface for image processing operations
using the sunshineplan/imgconv Go library.
"""

import argparse
import sys
import subprocess
import os

def run_go_wrapper(args):
    """Run the Go wrapper program with the provided arguments."""
    # Build the go wrapper command
    # First, ensure the Go binary is built
    script_dir = os.path.dirname(os.path.abspath(__file__))
    go_binary = os.path.join(script_dir, "bin", "imgconv-wrapper")

    # Build if not exists
    if not os.path.exists(go_binary):
        print("Building Go wrapper...")
        build_cmd = ["go", "build", "-o", go_binary, "cmd/main.go"]
        build_process = subprocess.run(build_cmd, cwd=script_dir, capture_output=True, text=True)
        if build_process.returncode != 0:
            print(f"Build failed: {build_process.stderr}")
            sys.exit(1)
        print("Build successful!")

    # Run the Go binary
    cmd = [go_binary] + args

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e.stderr}")
        return e.returncode
    except FileNotFoundError:
        print("ERROR: imgconv-wrapper binary not found. Please build it first with 'go build -o bin/imgconv-wrapper cmd/main.go'")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Image conversion and processing tool using imgconv Go library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert format
  python main.py --action convert --input image.png --output image.jpg --format jpeg

  # Resize image
  python main.py --action resize --input photo.jpg --output small.jpg --width 800

  # Resize by percentage
  python main.py --action resize --input photo.jpg --output half.jpg --percent 50

  # Add watermark
  python main.py --action watermark --input image.jpg --output watermarked.jpg --watermark logo.png --opacity 128 --random

  # Split image
  python main.py --action split --input long.png --output split_%d.png --split-parts 3 --split-mode horizontal
        """
    )

    # Required arguments
    parser.add_argument('--action', required=True,
                       choices=['convert', 'resize', 'watermark', 'split'],
                       help='Action to perform')
    parser.add_argument('--input', required=True,
                       help='Input image path')

    # Optional arguments
    parser.add_argument('--output', help='Output image path')
    parser.add_argument('--format',
                       choices=['jpeg', 'png', 'gif', 'tiff', 'bmp', 'webp'],
                       help='Output format (for convert action)')

    # Resize options
    parser.add_argument('--width', type=int, help='Target width (for resize)')
    parser.add_argument('--height', type=int, help='Target height (for resize)')
    parser.add_argument('--percent', type=int, help='Resize percentage (for resize, e.g., 50 for 50%%)')

    # Watermark options
    parser.add_argument('--watermark', help='Watermark image path (for watermark action)')
    parser.add_argument('--opacity', type=int, default=128, help='Watermark opacity 0-255 (default: 128)')
    parser.add_argument('--random', action='store_true', help='Place watermark at random position')
    parser.add_argument('--offset-x', type=int, help='Watermark offset X')
    parser.add_argument('--offset-y', type=int, help='Watermark offset Y')

    # Split options
    parser.add_argument('--split-parts', type=int, help='Number of parts to split into (for split action)')
    parser.add_argument('--split-mode', choices=['horizontal', 'vertical'],
                       help='Split direction (for split action)')

    args = parser.parse_args()

    # Build argument list for Go wrapper
    go_args = []

    go_args.extend(['--action', args.action])
    go_args.extend(['--input', args.input])

    if args.output:
        go_args.extend(['--output', args.output])

    if args.format:
        go_args.extend(['--format', args.format])

    if args.width:
        go_args.extend(['--width', str(args.width)])

    if args.height:
        go_args.extend(['--height', str(args.height)])

    if args.percent:
        go_args.extend(['--percent', str(args.percent)])

    if args.watermark:
        go_args.extend(['--watermark', args.watermark])

    go_args.extend(['--opacity', str(args.opacity)])

    if args.random:
        go_args.append('--random')

    if args.offset_x is not None:
        go_args.extend(['--offset-x', str(args.offset_x)])

    if args.offset_y is not None:
        go_args.extend(['--offset-y', str(args.offset_y)])

    if args.split_parts:
        go_args.extend(['--split-parts', str(args.split_parts)])

    if args.split_mode:
        go_args.extend(['--split-mode', args.split_mode])

    return run_go_wrapper(go_args)

if __name__ == "__main__":
    sys.exit(main())
