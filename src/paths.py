# src/paths.py
from pathlib import Path
import sys

# --- find assets directory ---------------------------------------------------

def _dev_assets_dir() -> Path:
    # src/paths.py is in src/, so assets is src/assets
    return Path(__file__).resolve().parent / "assets"

def _frozen_assets_dir() -> Path:
    exe = Path(sys.executable).resolve()
    if getattr(sys, "frozen", False):
        # Case 1: PyInstaller onefile bundle -> assets unpacked to _MEIPASS
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass and (Path(meipass) / "assets").exists():
            return Path(meipass) / "assets"

        # Case 2: PyInstaller onedir macOS .app bundle
        # -> dist/AppName.app/Contents/MacOS/assets
        macos_assets = exe.parent / "assets"
        if macos_assets.exists():
            return macos_assets

        # Case 3 (rare): manually copied into Resources/assets
        resources_assets = exe.parent.parent / "Resources" / "assets"
        if resources_assets.exists():
            return resources_assets

    # Fallback for dev
    return _dev_assets_dir()

ASSETS_DIR = _frozen_assets_dir()

# --- model + output paths ----------------------------------------------------

LLM_MODELS_DIR = ASSETS_DIR / "models" / "llm"

APP_DIR = Path.home() / "LocalAI"
OUTPUTS_DIR = APP_DIR / "outputs"
for p in (APP_DIR, OUTPUTS_DIR):
    p.mkdir(parents=True, exist_ok=True)
