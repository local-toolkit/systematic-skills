package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/sunshineplan/imgconv"
	"image"
)

var (
	action     = flag.String("action", "", "Action to perform: convert, resize, watermark, split")
	inputFile  = flag.String("input", "", "Input image path")
	outputFile = flag.String("output", "", "Output image path")
	format     = flag.String("format", "", "Output format: jpeg, png, gif, tiff, bmp, webp")
	width      = flag.Int("width", 0, "Target width for resize")
	height     = flag.Int("height", 0, "Target height for resize")
	percent    = flag.Int("percent", 0, "Resize percentage (e.g., 50 for 50%)")
	watermark  = flag.String("watermark", "", "Watermark image path")
	opacity    = flag.Int("opacity", 128, "Watermark opacity 0-255")
	randomPos  = flag.Bool("random", false, "Place watermark at random position")
	offsetX    = flag.Int("offset-x", 0, "Watermark offset X")
	offsetY    = flag.Int("offset-y", 0, "Watermark offset Y")
	splitParts = flag.Int("split-parts", 0, "Number of parts to split into")
	splitMode  = flag.String("split-mode", "", "Split mode: horizontal, vertical")
)

func parseFormat(format string) imgconv.Format {
	switch strings.ToLower(format) {
	case "jpeg", "jpg":
		return imgconv.JPEG
	case "png":
		return imgconv.PNG
	case "gif":
		return imgconv.GIF
	case "tiff", "tif":
		return imgconv.TIFF
	case "bmp":
		return imgconv.BMP
	case "webp":
		return imgconv.WEBP
	default:
		return imgconv.JPEG
	}
}

func parseSplitMode(mode string) imgconv.SplitMode {
	switch strings.ToLower(mode) {
	case "horizontal":
		return imgconv.SplitHorizontalMode
	case "vertical":
		return imgconv.SplitVerticalMode
	default:
		return imgconv.SplitHorizontalMode
	}
}

func validateRequiredFields() error {
	if *action == "" {
		return fmt.Errorf("--action is required")
	}
	if *inputFile == "" {
		return fmt.Errorf("--input is required")
	}
	if _, err := os.Stat(*inputFile); os.IsNotExist(err) {
		return fmt.Errorf("input file does not exist: %s", *inputFile)
	}
	return nil
}

func convertImage() error {
	// Open input image
	src, err := imgconv.Open(*inputFile)
	if err != nil {
		return fmt.Errorf("failed to open input image: %w", err)
	}

	// Determine output format
	outputFormat := parseFormat(*format)

	// Determine output file path
	outPath := *outputFile
	if outPath == "" {
		ext := "." + *format
		outPath = strings.TrimSuffix(*inputFile, filepath.Ext(*inputFile)) + ext
	}

	// Create output file
	outFile, err := os.Create(outPath)
	if err != nil {
		return fmt.Errorf("failed to create output file: %w", err)
	}
	defer outFile.Close()

	// Write image
	if err := imgconv.Write(outFile, src, &imgconv.FormatOption{Format: outputFormat}); err != nil {
		return fmt.Errorf("failed to write image: %w", err)
	}

	fmt.Printf("Successfully converted %s to %s (format: %s)\n", *inputFile, outPath, *format)
	return nil
}

func resizeImage() error {
	// Open input image
	src, err := imgconv.Open(*inputFile)
	if err != nil {
		return fmt.Errorf("failed to open input image: %w", err)
	}

	// Build resize options
	opts := &imgconv.ResizeOption{}
	if *width > 0 {
		opts.Width = *width
	}
	if *height > 0 {
		opts.Height = *height
	}
	if *percent > 0 {
		opts.Percent = float64(*percent)
	}

	// Perform resize
	dst := imgconv.Resize(src, opts)

	// Determine output file path
	outPath := *outputFile
	if outPath == "" {
		ext := filepath.Ext(*inputFile)
		outPath = strings.TrimSuffix(*inputFile, ext) + "_resized" + ext
	}

	// Create output file
	outFile, err := os.Create(outPath)
	if err != nil {
		return fmt.Errorf("failed to create output file: %w", err)
	}
	defer outFile.Close()

	// Write resized image
	if err := imgconv.Write(outFile, dst, &imgconv.FormatOption{Format: imgconv.JPEG}); err != nil {
		return fmt.Errorf("failed to write image: %w", err)
	}

	fmt.Printf("Successfully resized %s to %s\n", *inputFile, outPath)
	return nil
}

func addWatermark() error {
	// Open input image
	src, err := imgconv.Open(*inputFile)
	if err != nil {
		return fmt.Errorf("failed to open input image: %w", err)
	}

	// Open watermark image
	mark, err := imgconv.Open(*watermark)
	if err != nil {
		return fmt.Errorf("failed to open watermark image: %w", err)
	}

	// Build watermark options
	opts := &imgconv.WatermarkOption{
		Mark:    mark,
		Opacity: uint8(*opacity),
		Random:  *randomPos,
	}

	if !*randomPos && (*offsetX != 0 || *offsetY != 0) {
		opts.Offset = image.Pt(*offsetX, *offsetY)
	}

	// Add watermark
	dst := imgconv.Watermark(src, opts)

	// Determine output file path
	outPath := *outputFile
	if outPath == "" {
		ext := filepath.Ext(*inputFile)
		outPath = strings.TrimSuffix(*inputFile, ext) + "_watermarked" + ext
	}

	// Create output file
	outFile, err := os.Create(outPath)
	if err != nil {
		return fmt.Errorf("failed to create output file: %w", err)
	}
	defer outFile.Close()

	// Write watermarked image
	if err := imgconv.Write(outFile, dst, &imgconv.FormatOption{Format: imgconv.JPEG}); err != nil {
		return fmt.Errorf("failed to write image: %w", err)
	}

	fmt.Printf("Successfully added watermark to %s -> %s\n", *inputFile, outPath)
	return nil
}

func splitImage() error {
	// Open input image
	src, err := imgconv.Open(*inputFile)
	if err != nil {
		return fmt.Errorf("failed to open input image: %w", err)
	}

	// Parse split mode
	mode := parseSplitMode(*splitMode)

	// Split image
	imgs, err := imgconv.Split(src, *splitParts, mode)
	if err != nil {
		return fmt.Errorf("failed to split image: %w", err)
	}

	// Determine output file path pattern
	outPattern := *outputFile
	if outPattern == "" {
		ext := filepath.Ext(*inputFile)
		base := strings.TrimSuffix(*inputFile, ext)
		outPattern = base + "_%d" + ext
	}

	// Save split images
	for i, img := range imgs {
		// Format output filename
		outPath := fmt.Sprintf(outPattern, i+1)

		// Create output file
		outFile, err := os.Create(outPath)
		if err != nil {
			return fmt.Errorf("failed to create output file %s: %w", outPath, err)
		}

		// Write image
		if err := imgconv.Write(outFile, img, &imgconv.FormatOption{Format: imgconv.JPEG}); err != nil {
			outFile.Close()
			return fmt.Errorf("failed to write image %s: %w", outPath, err)
		}
		outFile.Close()

		fmt.Printf("Created split part %d: %s\n", i+1, outPath)
	}

	fmt.Printf("Successfully split %s into %d parts\n", *inputFile, len(imgs))
	return nil
}

func main() {
	flag.Parse()

	// Validate required fields
	if err := validateRequiredFields(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	// Execute action
	var err error
	switch strings.ToLower(*action) {
	case "convert":
		if *format == "" {
			fmt.Fprintf(os.Stderr, "Error: --format is required for convert action\n")
			os.Exit(1)
		}
		err = convertImage()
	case "resize":
		err = resizeImage()
	case "watermark":
		if *watermark == "" {
			fmt.Fprintf(os.Stderr, "Error: --watermark is required for watermark action\n")
			os.Exit(1)
		}
		err = addWatermark()
	case "split":
		if *splitParts == 0 {
			fmt.Fprintf(os.Stderr, "Error: --split-parts is required for split action\n")
			os.Exit(1)
		}
		if *splitMode == "" {
			fmt.Fprintf(os.Stderr, "Error: --split-mode is required for split action\n")
			os.Exit(1)
		}
		err = splitImage()
	default:
		fmt.Fprintf(os.Stderr, "Error: unknown action '%s'\n", *action)
		fmt.Fprintf(os.Stderr, "Valid actions: convert, resize, watermark, split\n")
		os.Exit(1)
	}

	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
