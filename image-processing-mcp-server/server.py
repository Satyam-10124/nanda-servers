#!/usr/bin/env python3
"""
Image Processing MCP Server for NANDA

Enables NANDA agents to process and manipulate images.
"""

from mcp.server.fastmcp import FastMCP
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import os
from typing import Optional

mcp = FastMCP("image-processing")


@mcp.tool()
def resize_image(
    input_path: str,
    output_path: str,
    width: int,
    height: int,
    maintain_aspect: bool = True
) -> dict:
    """
    Resize an image
    
    Args:
        input_path: Path to input image
        output_path: Path to save resized image
        width: Target width in pixels
        height: Target height in pixels
        maintain_aspect: Maintain aspect ratio (default: True)
    
    Returns:
        Output image details
    """
    try:
        img = Image.open(input_path)
        
        if maintain_aspect:
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
        else:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        img.save(output_path)
        
        return {
            "success": True,
            "input": input_path,
            "output": output_path,
            "size": img.size
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def compress_image(
    input_path: str,
    output_path: str,
    quality: int = 85
) -> dict:
    """
    Compress image to reduce file size
    
    Args:
        input_path: Path to input image
        output_path: Path to save compressed image
        quality: JPEG quality (1-100, default: 85)
    
    Returns:
        Compression details with file sizes
    """
    try:
        img = Image.open(input_path)
        
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        input_size = os.path.getsize(input_path)
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        output_size = os.path.getsize(output_path)
        
        reduction = ((input_size - output_size) / input_size) * 100
        
        return {
            "success": True,
            "input_size": input_size,
            "output_size": output_size,
            "reduction_percent": round(reduction, 2)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def convert_format(input_path: str, output_path: str, format: str) -> dict:
    """
    Convert image to different format
    
    Args:
        input_path: Path to input image
        output_path: Path to save converted image
        format: Target format (JPEG, PNG, WEBP, etc.)
    
    Returns:
        Conversion details
    """
    try:
        img = Image.open(input_path)
        
        if format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        img.save(output_path, format=format.upper())
        
        return {
            "success": True,
            "input_format": img.format,
            "output_format": format.upper(),
            "output_path": output_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_watermark(
    input_path: str,
    output_path: str,
    watermark_text: str,
    position: str = "bottom_right"
) -> dict:
    """
    Add text watermark to image
    
    Args:
        input_path: Path to input image
        output_path: Path to save watermarked image
        watermark_text: Watermark text
        position: Position (top_left, top_right, bottom_left, bottom_right)
    
    Returns:
        Watermark details
    """
    try:
        img = Image.open(input_path).convert('RGBA')
        watermark = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        positions = {
            'top_left': (10, 10),
            'top_right': (img.width - text_width - 10, 10),
            'bottom_left': (10, img.height - text_height - 10),
            'bottom_right': (img.width - text_width - 10, img.height - text_height - 10)
        }
        
        pos = positions.get(position, positions['bottom_right'])
        draw.text(pos, watermark_text, fill=(255, 255, 255, 128), font=font)
        
        result = Image.alpha_composite(img, watermark)
        result.convert('RGB').save(output_path)
        
        return {
            "success": True,
            "watermark": watermark_text,
            "output": output_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def apply_filter(input_path: str, output_path: str, filter_type: str) -> dict:
    """
    Apply filter to image
    
    Args:
        input_path: Path to input image
        output_path: Path to save filtered image
        filter_type: BLUR, SHARPEN, EDGE_ENHANCE, CONTOUR, DETAIL, EMBOSS
    
    Returns:
        Filter details
    """
    try:
        img = Image.open(input_path)
        
        filters = {
            'BLUR': ImageFilter.BLUR,
            'SHARPEN': ImageFilter.SHARPEN,
            'EDGE_ENHANCE': ImageFilter.EDGE_ENHANCE,
            'CONTOUR': ImageFilter.CONTOUR,
            'DETAIL': ImageFilter.DETAIL,
            'EMBOSS': ImageFilter.EMBOSS
        }
        
        if filter_type.upper() not in filters:
            return {"success": False, "error": f"Unknown filter: {filter_type}"}
        
        filtered = img.filter(filters[filter_type.upper()])
        filtered.save(output_path)
        
        return {
            "success": True,
            "filter": filter_type,
            "output": output_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_image_info(image_path: str) -> dict:
    """
    Get image information
    
    Args:
        image_path: Path to image
    
    Returns:
        Image metadata
    """
    try:
        img = Image.open(image_path)
        
        return {
            "success": True,
            "format": img.format,
            "mode": img.mode,
            "size": img.size,
            "width": img.width,
            "height": img.height,
            "file_size": os.path.getsize(image_path)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    print("🚀 Starting Image Processing MCP Server")
    print("🖼️  Resize, compress, filter images")
    print()
    mcp.run()
