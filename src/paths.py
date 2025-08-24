import os
import sys
from pathlib import Path

ENV_ASSETS = "LOCALAI_ASSETS_DIR"

def _env_assets_dir() -> Path | None:
    p = os.environ.get(ENV_ASSETS)
    if not p:
        return None
    pp = Path(p).expanduser().resolve()
    return pp if pp.exists() else None


def _dev_assets_dir() -> Path:
    # src/paths.py -> src/assets
    return Path(__file__).resolve().parent / "assets"


def _frozen_assets_dir() -> Path | None:
    exe = Path(sys.executable).resolve()
    if getattr(sys, "frozen", False):
        # PyInstaller onefile: extracted to _MEIPASS
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            mp = Path(meipass) / "assets"
            if mp.exists():
                return mp
        # PyInstaller onedir macOS .app: Contents/MacOS/assets
        macos_assets = exe.parent / "assets"
        if macos_assets.exists():
            return macos_assets
        # (fallback) if assets were copied into Resources/assets
        res_assets = exe.parent.parent / "Resources" / "assets"
        if res_assets.exists():
            return res_assets
    return None


def _assets_dir() -> Path:
    return _env_assets_dir() or _frozen_assets_dir() or _dev_assets_dir()


ASSETS_DIR = _assets_dir()

LLM_MODELS_DIR = ASSETS_DIR / "models" / "llm"

APP_DIR = Path.home() / "LocalAI"
OUTPUTS_DIR = APP_DIR / "outputs"
for p in (APP_DIR, OUTPUTS_DIR):
    p.mkdir(parents=True, exist_ok=True)
