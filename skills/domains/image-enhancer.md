---
name: image-enhancer
description: Batch image enhancement with ImageMagick — upscale, sharpen, format-convert, platform presets.

metadata:
  tags:
  - image
  - enhancement
  - imagemagick
  - sharpening
  - upscale
  - batch
  - webp
  - avif
  - compression
  tier: task-specific
  domain: creative
when_to_apply: When improving image quality, sharpening screenshots, upscaling for print or retina displays, batch converting image formats, or optimizing images for specific platforms
---
# Image Enhancer

Professional image enhancement using ImageMagick (`convert`, `magick`, `mogrify`, `identify`) and intelligent optimization techniques. Produces sharper, cleaner images optimized for any output target — web, social media, print, or documentation.

## Trigger

- **Command**: `/enhance-image` or `/image-enhancer`
- **Keywords**: enhance image, improve screenshot, upscale, sharpen, batch process images, convert format, optimize for Twitter/Instagram/LinkedIn/blog

## When to Use This Skill

- **Documentation**: Enhance screenshots for clarity in docs or wikis
- **Blog Posts**: Optimize images for fast web delivery
- **Social Media**: Resize and optimize for platform-specific dimensions
- **Presentations**: Upscale images for large-screen projection
- **Print Materials**: Increase resolution for physical media output
- **Batch Processing**: Enhance entire folders of images in one pass
- **Format Conversion**: Convert between PNG, JPG, WebP, and AVIF
- **Compression**: Reduce file size while maintaining perceptual quality

---

## Core Capabilities

### 1. Resolution Enhancement
- Upscale using high-quality filter algorithms (Lanczos, Mitchell, Catrom)
- Maintain aspect ratios automatically
- Target retina and 4K display resolutions
- Smart interpolation selection based on image content type

### 2. Sharpening and Denoising
- Unsharp mask for natural, artifact-free sharpening
- Adaptive sharpen for edge-aware enhancement
- Despeckle and noise reduction passes
- Contrast stretching for washed-out images

### 3. Batch Processing
- Process entire directories with a single command
- Parallel processing via `mogrify` or `xargs -P`
- Preserve directory structure during output
- Progress logging via `tee enhancement.log`

### 4. Format Conversion
- PNG ↔ JPG ↔ WebP ↔ AVIF
- Maintain perceptual quality across conversions
- Chroma subsampling control for JPEG
- Lossless and lossy WebP modes

### 5. Compression Optimization
- Lossless PNG optimization with metadata stripping
- Quality-controlled JPEG compression
- Modern format output (WebP, AVIF) with quality targets
- Before/after file size comparison

### 6. Platform Presets
- Twitter/X, Instagram, LinkedIn, Blog — see [Platform Preset Reference](#platform-preset-reference) below

---

## ImageMagick Quick Reference

### Resize and Upscale

```bash
# Upscale to specific width (maintain aspect ratio)
convert input.png -filter Lanczos -resize 2560x output.png

# Upscale to percentage
convert input.png -filter Mitchell -resize 200% output.png

# Exact dimensions with crop (center gravity)
convert input.png -resize 1200x675^ -gravity center -extent 1200x675 output.jpg
```

### Sharpening

```bash
# Unsharp mask — natural sharpening for photos
convert input.png -unsharp 0x1 output.png

# Adaptive sharpen — edge-aware, good for screenshots
convert input.png -adaptive-sharpen 0x1 output.png

# Combined: upscale + sharpen
convert input.png -filter Lanczos -resize 2560x -unsharp 0x1 output.png
```

### Denoising

```bash
# Despeckle (gentle noise reduction)
convert input.png -despeckle output.png

# Median filter (stronger noise reduction)
convert input.png -median 1 output.png

# Noise reduction before upscaling
convert input.png -despeckle -filter Lanczos -resize 200% output.png
```

### Format Conversion

```bash
# PNG to JPEG with quality
convert input.png -quality 90 output.jpg

# PNG to WebP
convert input.png -quality 85 output.webp

# PNG to AVIF (requires ImageMagick with AVIF delegate)
magick input.png -quality 80 output.avif

# Batch convert all PNGs to WebP
mogrify -format webp -quality 85 *.png
```

### Compression and Metadata

```bash
# Strip EXIF/metadata (privacy + file size)
convert input.png -strip output.png

# JPEG with chroma subsampling (smaller files)
convert input.jpg -quality 85 -sampling-factor 4:2:0 -strip output.jpg

# PNG lossless optimization
convert input.png -strip -define png:compression-level=9 output.png
```

### Batch Processing

```bash
# Resize all JPEGs in place
mogrify -resize 1920x *.jpg

# Convert directory to WebP (preserves originals)
mogrify -format webp -quality 85 -path ./webp/ *.png

# Parallel batch with backup
mkdir -p originals enhanced
cp *.png originals/
mogrify -format jpg -quality 90 -path ./enhanced/ *.png
```

---

## Advanced Enhancement Pipelines

### Full Enhancement: Upscale + Sharpen + Optimize

```bash
convert input.png \
  -filter Lanczos -resize 2560x \
  -unsharp 0x1 \
  -strip \
  -quality 95 \
  output-enhanced.png
```

### Screenshot Enhancement (Text Clarity)

Best for UI screenshots, terminal captures, documentation images:

```bash
convert screenshot.png \
  -filter Mitchell -resize 200% \
  -adaptive-sharpen 0x1 \
  -contrast-stretch 0.1x0.1% \
  -strip \
  screenshot-enhanced.png
```

### Photo Enhancement (Natural Imagery)

Best for photographs with smooth gradients and organic detail:

```bash
convert photo.jpg \
  -filter Lanczos -resize 3840x \
  -unsharp 0x0.5+0.5+0.05 \
  -quality 92 \
  -strip \
  photo-enhanced.jpg
```

### Web-Optimized Output (Minimal File Size)

```bash
convert input.png \
  -resize 1920x \
  -strip \
  -quality 85 \
  output.webp
```

---

## Platform Preset Reference

### Twitter / X

| Property | Value |
|----------|-------|
| Landscape | 1200 x 675 px |
| Square | 1200 x 1200 px |
| Format | JPG or PNG |
| Max file size | 5 MB |
| Recommended quality | 85–90 |

```bash
convert input.png \
  -resize 1200x675^ -gravity center -extent 1200x675 \
  -quality 87 -strip \
  twitter.jpg
```

### Instagram

| Property | Value |
|----------|-------|
| Feed (square) | 1080 x 1080 px |
| Feed (portrait) | 1080 x 1350 px |
| Stories / Reels | 1080 x 1920 px |
| Format | JPG |
| Max file size | 30 MB |
| Recommended quality | 90 |

```bash
# Square feed post
convert input.png \
  -resize 1080x1080^ -gravity center -extent 1080x1080 \
  -quality 90 -strip \
  instagram-square.jpg

# Portrait feed post
convert input.png \
  -resize 1080x1350^ -gravity center -extent 1080x1350 \
  -quality 90 -strip \
  instagram-portrait.jpg
```

### LinkedIn

| Property | Value |
|----------|-------|
| Link preview / article | 1200 x 627 px |
| Profile banner | 1584 x 396 px |
| Format | JPG or PNG |
| Max file size | 5 MB |
| Recommended quality | 85–90 |

```bash
convert input.png \
  -resize 1200x627^ -gravity center -extent 1200x627 \
  -quality 88 -strip \
  linkedin.jpg
```

### Blog / Web Headers

| Property | Value |
|----------|-------|
| Standard max width | 1920 px |
| Retina max width | 2560 px |
| Format | WebP (JPG fallback) |
| Recommended quality | 85 (WebP), 90 (JPG) |

```bash
# WebP (primary)
convert input.png \
  -resize 1920x -strip \
  -quality 85 \
  header.webp

# JPEG fallback
convert input.png \
  -resize 1920x -strip \
  -quality 90 \
  header.jpg
```

---

## Quality Guidelines

### PNG (Lossless)

- Compression level: 9 (maximum, lossless)
- Always strip metadata: `-strip`
- No quality loss — use for graphics, logos, screenshots

### JPEG (Lossy)

| Use Case | Quality |
|----------|---------|
| Web / social | 85–90 |
| Print | 90–95 |
| Thumbnails | 75–80 |

Add `-sampling-factor 4:2:0` for smaller files at equivalent visual quality.

### WebP (Modern Lossy / Lossless)

| Use Case | Quality |
|----------|---------|
| Web photos | 80–85 |
| Graphics / screenshots | 90–95 |
| Lossless mode | `-define webp:lossless=true` |

WebP typically achieves 25–35% smaller files than JPEG at equivalent quality.

### AVIF (Newest)

| Use Case | Quality |
|----------|---------|
| Highest compression | 75–80 |
| Balanced | 80–85 |

AVIF requires ImageMagick compiled with `libavif`. Check support: `magick -list format | grep AVIF`.

---

## Filter Algorithm Reference

| Filter | Best For | Tradeoff |
|--------|----------|----------|
| **Lanczos** | Photos, natural images | Slowest, sharpest |
| **Mitchell** | Screenshots, text, UI | Medium speed, clean edges |
| **Catrom** | General purpose | Medium speed, balanced |
| **Point** | Pixel art, no interpolation | Fastest, nearest-neighbor |
| **Box** | Simple averaging | Fast, blurrier |

---

## Before/After Quality Comparison

### File Size Comparison

```bash
# Single image
echo "Before: $(du -sh input.png | cut -f1)"
echo "After:  $(du -sh output.png | cut -f1)"

# Directory comparison
echo "Before: $(du -sh originals/ | cut -f1)"
echo "After:  $(du -sh enhanced/ | cut -f1)"
```

### Dimension Check

```bash
# Check dimensions and format before/after
identify -format "%f: %wx%h %m %b bytes
" input.png output.png
```

### Verbose Image Info

```bash
identify -verbose input.png | grep -E "(Geometry|Quality|Format|Filesize)"
```

### Side-by-Side Comparison Montage

```bash
# Create a comparison image (requires input and output)
convert +append input.png output.png comparison.png

# With label overlay
convert \
  \( input.png -set label "Before" \) \
  \( output.png -set label "After" \) \
  +append -border 2 comparison-labeled.png
```

---

## Instructions for Claude

When a user requests image enhancement, follow this workflow:

### Step 1 — Analyze the Source Image

```bash
identify -format "Dimensions: %wx%h
Format: %m
Size: %b bytes
Colorspace: %[colorspace]
" input.png
```

Determine content type:
- **Screenshot / UI / text**: Use Mitchell filter, adaptive-sharpen
- **Photo / natural image**: Use Lanczos filter, unsharp mask
- **Logo / vector-rendered graphic**: Use Point or Box filter, avoid lossy

### Step 2 — Back Up Originals (Always)

```bash
mkdir -p originals
cp input.png originals/input.png
```

Never mutate the source file in place without a backup.

### Step 3 — Apply Transformations in Optimal Order

1. Denoise (if needed): `-despeckle` or `-median 1`
2. Resize / upscale: `-filter <X> -resize <target>`
3. Sharpen: `-unsharp` or `-adaptive-sharpen`
4. Contrast / color correction: `-contrast-stretch 0.1x0.1%`
5. Strip metadata: `-strip`
6. Compress: `-quality <N>`

### Step 4 — Platform Presets

If the user specifies a target platform, apply the preset from the [Platform Preset Reference](#platform-preset-reference) section exactly. Prefer the exact crop dimensions with `-gravity center -extent` to guarantee correct aspect ratio.

### Step 5 — Batch Processing

For directories:
```bash
# Non-destructive: output to subdirectory
mogrify -format webp -quality 85 -path ./webp/ *.png

# With parallel processing (if `parallel` is available)
ls *.png | parallel -j 4 'convert {} -filter Lanczos -resize 2560x enhanced/{}'
```

### Step 6 — Validate and Report

After processing, always output:
- Before/after dimensions
- Before/after file sizes
- Format used
- Any warnings (e.g., AVIF not available, delegate missing)

---

## Troubleshooting

### Image Too Blurry After Upscaling

- Switch to a higher-quality filter: `-filter Lanczos`
- Add sharpening after resize: `-unsharp 0x1`
- Reduce upscale ratio (200% instead of 400%)

### File Size Larger Than Expected After Conversion

- Strip metadata: `-strip`
- Lower quality target: `-quality 85` instead of 95
- Use a modern format: WebP or AVIF
- For JPEG, add chroma subsampling: `-sampling-factor 4:2:0`

### Text Not Sharp in Screenshots

- Use Mitchell filter: `-filter Mitchell`
- Use adaptive sharpen: `-adaptive-sharpen 0x1`
- Boost contrast gently: `-contrast-stretch 0.1x0.1%`

### Batch Processing Is Slow

- Use `mogrify` instead of a `for` loop calling `convert`
- Parallelize with GNU parallel or `xargs -P 4`
- Process in chunks for very large directories

### AVIF Not Supported

Check delegate support:
```bash
magick -list format | grep AVIF
```

If absent, fall back to WebP:
```bash
convert input.png -quality 85 output.webp
```

### `convert` Command Conflicts with Windows `convert.exe`

Use `magick convert` explicitly on systems where the path may be ambiguous:
```bash
magick convert input.png -quality 90 output.jpg
```

---

## File Organization Convention

```
project-images/
├── originals/           # Untouched source images (always back up here first)
├── enhanced/            # Enhanced versions
├── web/                 # Web-optimized (WebP, AVIF)
├── social/              # Platform-specific exports
│   ├── twitter/
│   ├── instagram/
│   └── linkedin/
├── print/               # High-resolution for print output
└── enhancement.log      # Processing log (tee output here)
```

---

## Dependencies

- **ImageMagick** — `convert`, `magick`, `mogrify`, `identify`
  - macOS: `brew install imagemagick`
  - Ubuntu/Debian: `apt install imagemagick`
  - Windows: Download from https://imagemagick.org/script/download.php
- **GNU Parallel** (optional, for parallel batch) — `brew install parallel` / `apt install parallel`
- **AVIF support** — requires ImageMagick built with `libavif` delegate
