import flet as ft

from core.llm_adapter import LlamaRunner
from paths import ensure_app_dirs
from ui.chat import ChatView

APP_TITLE = "Local AI (Chat)"


def main(page: ft.Page) -> None:
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
    chat = ChatView(page, llm, notify)

    page.add(
        ft.Column(
            [
                chat.control(),
            ],
            expand=True,
        )
    )


if __name__ == "__main__":
    # assets_dir ensures your bundled model (src/assets/...) is available when packaged
    ft.app(target=main, assets_dir="src/assets")
