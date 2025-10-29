# Image Processing MCP Server

MCP server enabling NANDA agents to process and manipulate images.

## Features

- ✅ Resize images (with aspect ratio)
- ✅ Compress images
- ✅ Convert formats (JPEG, PNG, WEBP, etc.)
- ✅ Add watermarks
- ✅ Apply filters
- ✅ Get image metadata

## Setup

```bash
pip install -r requirements.txt
```

## Usage Examples

### Resize Image
```python
resize_image(
    input_path="/path/to/image.jpg",
    output_path="/path/to/resized.jpg",
    width=800,
    height=600,
    maintain_aspect=True
)
```

### Compress Image
```python
compress_image(
    input_path="/path/to/large.jpg",
    output_path="/path/to/compressed.jpg",
    quality=85
)
```

### Convert Format
```python
convert_format(
    input_path="/path/to/image.png",
    output_path="/path/to/image.webp",
    format="WEBP"
)
```

### Add Watermark
```python
add_watermark(
    input_path="/path/to/image.jpg",
    output_path="/path/to/watermarked.jpg",
    watermark_text="© 2024 Company",
    position="bottom_right"
)
```

### Apply Filter
```python
apply_filter(
    input_path="/path/to/image.jpg",
    output_path="/path/to/filtered.jpg",
    filter_type="SHARPEN"
)
```

## Available Filters

- `BLUR` - Blur image
- `SHARPEN` - Sharpen image
- `EDGE_ENHANCE` - Enhance edges
- `CONTOUR` - Detect contours
- `DETAIL` - Enhance details
- `EMBOSS` - Emboss effect

## Tools

| Tool | Description |
|------|-------------|
| `resize_image` | Resize image |
| `compress_image` | Compress to reduce size |
| `convert_format` | Convert to different format |
| `add_watermark` | Add text watermark |
| `apply_filter` | Apply image filter |
| `get_image_info` | Get image metadata |

## License

MIT
