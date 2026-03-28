"""Pillow text drawing utilities."""
from __future__ import annotations

import os
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from . import config
from .template_engine import TextBlock


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Try to load a TTF font; fall back to Pillow default."""
    fonts_dir = config.FONTS_DIR
    candidates = []
    if bold:
        candidates = ["Roboto-Bold.ttf", "DejaVuSans-Bold.ttf", "Arial Bold.ttf"]
    else:
        candidates = ["Roboto-Regular.ttf", "DejaVuSans.ttf", "Arial.ttf"]

    for name in candidates:
        path = os.path.join(fonts_dir, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    # System font fallback
    system_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    for path in system_fonts:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont, max_width: int) -> list[str]:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        try:
            w = font.getlength(test)
        except AttributeError:
            w = len(test) * (font.size if hasattr(font, "size") else 10)
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def draw_text_block(
    draw: ImageDraw.ImageDraw,
    block: TextBlock,
    lines: list[str],
) -> int:
    """Draw lines of text; returns y position after last line."""
    font = _load_font(block.font_size, block.bold)
    y = block.y
    for line in lines:
        wrapped = _wrap_text(line, font, block.max_width)
        for wline in wrapped:
            if block.align == "center":
                try:
                    w = font.getlength(wline)
                except AttributeError:
                    w = len(wline) * block.font_size * 0.6
                x = block.x + (block.max_width - w) // 2
            else:
                x = block.x
            draw.text((x, y), wline, font=font, fill=block.color)
            y += block.font_size + block.line_spacing
        y += 4  # extra gap between logical lines
    return y


def draw_handle_badge(
    img: Image.Image,
    handle: str,
    brand_color: str = "#FF6B35",
) -> None:
    """Draw brand handle in bottom-right corner."""
    draw = ImageDraw.Draw(img)
    font = _load_font(36)
    padding = 20
    try:
        w = font.getlength(handle)
    except AttributeError:
        w = len(handle) * 22

    x = config.SLIDE_WIDTH - int(w) - padding * 2
    y = config.SLIDE_HEIGHT - 80

    # Background pill
    r, g, b = _hex_to_rgb(brand_color)
    draw.rectangle([x - padding, y - 8, x + int(w) + padding, y + 48], fill=(r, g, b, 200))
    draw.text((x, y), handle, font=font, fill=(255, 255, 255))


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
