---
name: imgconv-expert
version: 1.0.0
description: Professional image processing expert based on sunshineplan/imgconv Go library.
status: active
type: execution
---

# Image Conversion Expert

## Overview

专业图像处理专家，基于 sunshineplan/imgconv Go 库，提供工业级图像格式转换、缩放、水印添加和图像分割功能。

## 核心功能

### 1. 图像格式转换

- **支持格式**: JPG/JPEG, PNG, GIF, TIFF/TIF, BMP, WEBP, PDF
- **输入类型**: 任何实现 `image.Image` 接口的图像
- **输出格式**: 可指定任意支持的格式

### 2. 图像缩放

- **固定尺寸**: 指定宽度和高度（如 128x128px）
- **保持比例**: 仅指定宽度或高度，自动保持宽高比
- **百分比缩放**: 按百分比缩放（如 50%）

### 3. 图像分割

- **水平分割**: 将图像水平分割为 N 部分
- **垂直分割**: 将图像垂直分割为 N 部分

### 4. 水印添加

- **随机位置**: 在图像随机位置添加水印
- **固定位置**: 在指定位置（带偏移量）添加水印
- **透明度控制**: 可设置水印透明度（0-255）

## 使用场景

### 场景 1: 批量格式转换

```
用户请求: "将 images/ 目录下的所有 PNG 图片转换为 JPEG 格式"
处理流程:
1. 扫描目标目录
2. 批量读取 PNG 文件
3. 转换为 JPEG 格式
4. 保存到指定输出目录
```

### 场景 2: 图像缩放

```
用户请求: "将这张图片缩放到宽度 800px，保持比例"
处理流程:
1. 读取原图
2. 使用 ResizeOption{Width: 800} 进行缩放
3. 保存输出
```

### 场景 3: 添加水印

```
用户请求: "为图片添加水印，透明度 50%，随机位置"
处理流程:
1. 读取原图和水印图
2. 使用 WatermarkOption{Opacity: 128, Random: true}
3. 保存输出
```

### 场景 4: 图像分割

```
用户请求: "将这张长图分成 3 张横向拼接的图片"
处理流程:
1. 读取原图
2. 使用 Split(srcImage, 3, SplitHorizontalMode)
3. 保存分割后的多张图片
```

## Go 库 API 参考

### 核心函数

#### 图像打开

```go
import "github.com/sunshineplan/imgconv"

// 从文件打开图像
src, err := imgconv.Open("path/to/image.jpg")
if err != nil {
    log.Fatal(err)
}
```

#### 图像缩放

```go
// 固定尺寸
dst := imgconv.Resize(src, &imgconv.ResizeOption{Width: 128, Height: 128})

// 保持比例缩放（仅宽度）
dst := imgconv.Resize(src, &imgconv.ResizeOption{Width: 800})

// 百分比缩放
dst := imgconv.Resize(src, &imgconv.ResizeOption{Percent: 50})
```

#### 图像分割

```go
// 水平分割为 3 部分
imgs, err := imgconv.Split(src, 3, imgconv.SplitHorizontalMode)

// 垂直分割为 3 部分
imgs, err := imgconv.Split(src, 3, imgconv.SplitVerticalMode)
```

#### 添加水印

```go
// 随机位置，透明度 128
dst := imgconv.Watermark(src, &imgconv.WatermarkOption{
    Mark: watermarkImg,
    Opacity: 128,
    Random: true,
})

// 固定位置，带偏移量
dst := imgconv.Watermark(src, &imgconv.WatermarkOption{
    Mark: watermarkImg,
    Opacity: 128,
    Offset: image.Pt(5, 5),
})
```

#### 格式转换

```go
import "io"

// 转换为 JPEG
imgconv.Write(dstWriter, src, &imgconv.FormatOption{Format: imgconv.JPEG})

// 转换为 PNG
imgconv.Write(dstWriter, src, &imgconv.FormatOption{Format: imgconv.PNG})
```

### 格式常量

```go
imgconv.JPEG  // JPEG 格式
imgconv.PNG   // PNG 格式
imgconv.GIF   // GIF 格式
imgconv.TIFF  // TIFF 格式
imgconv.BMP   // BMP 格式
imgconv.WEBP  // WEBP 格式
imgconv.PDF   // PDF 格式
```

### 分割模式常量

```go
imgconv.SplitHorizontalMode  // 水平分割
imgconv.SplitVerticalMode    // 垂直分割
```

## 依赖项

imgconv 依赖以下第三方项目：

- [disintegration/imaging](https://github.com/disintegration/imaging) - 图像处理核心库
- [pdfcpu/pdfcpu](https://github.com/pdfcpu/pdfcpu) - PDF 处理
- [hhrutter/tiff](https://github.com/hhrutter/tiff) - TIFF 格式支持
- [HugoSmits86/nativewebp](https://github.com/HugoSmits86/nativewebp) - WEBP 格式支持

## 安装

```bash
go get -u github.com/sunshineplan/imgconv
```

## 最佳实践

### 1. 错误处理

```go
src, err := imgconv.Open("image.jpg")
if err != nil {
    return fmt.Errorf("failed to open image: %w", err)
}
```

### 2. 内存管理

- 处理大图像时注意内存使用
- 使用完毕后及时释放资源

### 3. 批量处理

- 使用 goroutine 并行处理多张图片
- 控制并发数以避免内存溢出

### 4. 格式选择建议

- **JPEG**: 适合照片（有损压缩）
- **PNG**: 适合图标、透明图片（无损压缩）
- **WEBP**: 现代格式，压缩率高
- **TIFF**: 适合打印、存档

## 常见问题

### Q: 如何处理 PDF 文件？

A: imgconv 可以直接读取 PDF 文件作为输入，将其转换为其他图像格式。

### Q: 如何保持图像质量？

A: 对于高质量输出，推荐使用 PNG 或 WEBP 格式，避免使用 JPEG 的低质量压缩。

### Q: 如何批量处理多个文件？

A: 扫描目录，使用循环或 goroutine 并行处理每个文件。

### Q: 支持哪些输入格式？

A: 支持 JPG/JPEG, PNG, GIF, TIFF/TIF, BMP, WEBP 和 PDF 格式。

## 示例代码

### 完整示例：缩放 + 水印 + 格式转换

```go
package main

import (
    "io"
    "log"
    "os"

    "github.com/sunshineplan/imgconv"
)

func main() {
    // 打开原图
    src, err := imgconv.Open("input.jpg")
    if err != nil {
        log.Fatal(err)
    }

    // 打开水印图
    mark, err := imgconv.Open("watermark.png")
    if err != nil {
        log.Fatal(err)
    }

    // 缩放水印到合适大小
    resizedMark := imgconv.Resize(mark, &imgconv.ResizeOption{Width: 200})

    // 添加水印（随机位置，透明度 50%）
    watermarked := imgconv.Watermark(src, &imgconv.WatermarkOption{
        Mark: resizedMark,
        Opacity: 128,
        Random: true,
    })

    // 输出为 PNG 格式
    outFile, err := os.Create("output.png")
    if err != nil {
        log.Fatal(err)
    }
    defer outFile.Close()

    if err := imgconv.Write(outFile, watermarked, &imgconv.FormatOption{Format: imgconv.PNG}); err != nil {
        log.Fatal(err)
    }
}
```

## 相关资源

- [GitHub 仓库](https://github.com/sunshineplan/imgconv)
- [GoDoc 文档](https://pkg.go.dev/github.com/sunshineplan/imgconv)
- [源代码](https://github.com/sunshineplan/imgconv/tree/main)
