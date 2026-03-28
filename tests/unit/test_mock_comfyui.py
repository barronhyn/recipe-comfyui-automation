"""Unit tests for mock ComfyUI."""
import os
os.environ.setdefault("MOCK_MODE", "true")

from src.mock_comfyui import mock_generate
from src import config


def test_returns_bytes():
    result = mock_generate("test prompt", seed=42, slide_index=0)
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_valid_png():
    result = mock_generate("delicious pasta", seed=1, slide_index=1)
    # PNG magic bytes
    assert result[:8] == b"\x89PNG\r\n\x1a\n"


def test_correct_dimensions():
    from PIL import Image
    import io
    result = mock_generate("food photo", slide_index=0)
    img = Image.open(io.BytesIO(result))
    assert img.size == (config.SLIDE_WIDTH, config.SLIDE_HEIGHT)
