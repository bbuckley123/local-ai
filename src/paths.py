from pathlib import Path

APP_NAME = "Local AI"

APP_DIR = Path.home() / "LocalAI"
MODELS_DIR = APP_DIR / "models"
LLM_MODELS_DIR = MODELS_DIR / "llm"
OUTPUTS_DIR = APP_DIR / "outputs"
T2I_OUTPUTS_DIR = OUTPUTS_DIR / "txt2img"

for p in [APP_DIR, LLM_MODELS_DIR, T2I_OUTPUTS_DIR]:
    p.mkdir(parents=True, exist_ok=True)
