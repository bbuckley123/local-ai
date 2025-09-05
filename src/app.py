import argparse
import os
from pathlib import Path

import flet as ft

from config import APP_TITLE, ENV_MODEL
from core.llm_adapter import LlamaRunner
from paths import ensure_app_dirs
from ui.chat import ChatView


def main(page: ft.Page, model_path: Path | None) -> None:
    ensure_app_dirs()
    page.title = APP_TITLE
    page.window_width = 900
    page.window_height = 700
    page.padding = 16
    page.theme_mode = "light"

    def notify(msg: str) -> None:
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    llm = LlamaRunner()
    chat = ChatView(page, llm, notify, model_path)

    page.add(
        ft.Column(
            [
                chat.control(),
            ],
            expand=True,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        help="Path to GGUF model file",
        default=os.environ.get(ENV_MODEL),
    )
    args = parser.parse_args()
    model = Path(args.model).expanduser() if args.model else None

    def _main(page: ft.Page) -> None:
        main(page, model)

    # assets_dir ensures your bundled model (src/assets/...) is available when packaged
    ft.app(target=_main, assets_dir="src/assets")
