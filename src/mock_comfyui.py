"""Mock ComfyUI: returns solid-colored PNG bytes, no GPU required."""
import io
import random

from PIL import Image, ImageDraw

from . import config

# Distinct pastel colors per slide index
_SLIDE_COLORS = [
    (255, 200, 170),  # 1 - warm peach (cover)
    (200, 230, 200),  # 2 - soft green (ingredients)
    (200, 210, 240),  # 3 - light blue (steps 1-2)
    (240, 220, 190),  # 4 - warm wheat (steps 3-4)
]


def mock_generate(prompt: str, seed: int | None = None, slide_index: int = 0) -> bytes:
    """Return a 1080×1920 PNG with a colored background and prompt text."""
    color = _SLIDE_COLORS[slide_index % len(_SLIDE_COLORS)]
    img = Image.new("RGB", (config.SLIDE_WIDTH, config.SLIDE_HEIGHT), color)
    draw = ImageDraw.Draw(img)

    # Draw a simple label so we can distinguish mock images
    label = f"[MOCK] Slide {slide_index + 1}"
    draw.text((40, 40), label, fill=(80, 80, 80))

    # Wrap prompt text across image
    max_chars = 60
    words = prompt.split()
    lines, current = [], ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = (current + " " + word).strip()
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)

    y = 120
    for line in lines[:20]:
        draw.text((40, y), line, fill=(60, 60, 60))
        y += 32

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
