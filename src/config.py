import os
from dotenv import load_dotenv

load_dotenv()

MOCK_MODE: bool = os.getenv("MOCK_MODE", "true").lower() == "true"
COMFYUI_URL: str = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-6")

SLIDE_WIDTH: int = 1080
SLIDE_HEIGHT: int = 1920

BRAND_COLOR: str = os.getenv("BRAND_COLOR", "#FF6B35")
BRAND_HANDLE: str = os.getenv("BRAND_HANDLE", "@calmcaloriesrecipes")

WORKFLOWS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workflows")
TEMPLATES_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
FONTS_DIR: str = os.path.join(TEMPLATES_DIR, "fonts")

IP_ADAPTER_WEIGHT: float = float(os.getenv("IP_ADAPTER_WEIGHT", "0.65"))
COMFYUI_TIMEOUT: int = int(os.getenv("COMFYUI_TIMEOUT", "120"))
