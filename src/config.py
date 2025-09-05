import os
from dataclasses import dataclass
from pathlib import Path

APP_TITLE = "Local AI (Chat)"
ENV_MODEL = "LOCALAI_MODEL"
ENV_ASSETS = "LOCALAI_ASSETS_DIR"
DEFAULT_APP_DIR = Path.home() / "LocalAI"

DEFAULT_TEMPERATURE = float(os.getenv("LOCALAI_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.getenv("LOCALAI_MAX_TOKENS", "512"))
DEFAULT_CTX_SIZE = int(os.getenv("LOCALAI_CTX_SIZE", "4096"))


@dataclass(frozen=True)
class LLMDefaults:
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS
    ctx_size: int = DEFAULT_CTX_SIZE
