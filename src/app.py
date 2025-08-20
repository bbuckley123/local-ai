import flet as ft
from ui.chat import ChatView
from ui.t2i import T2IView
from core.llm_adapter import LlamaRunner

APP_TITLE = "Local AI (Chat + SD)"

def main(page: ft.Page) -> None:
    page.title = APP_TITLE
    page.window_width = 900
    page.window_height = 700
    page.padding = 16
    page.theme_mode = "light"

    def notify(msg: str) -> None:
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    # mode switch (avoids Tabs bug on Py3.9/Flet 0.28.x)
    mode_picker = ft.Dropdown(
        label="Mode",
        options=[ft.dropdown.Option("Chat"), ft.dropdown.Option("Text → Image")],
        value="Chat",
        width=220,
    )

    llm = LlamaRunner()

    chat = ChatView(page, llm, notify)
    t2i = T2IView(page, notify)

    def switch_mode(e: ft.ControlEvent) -> None:
        mode = mode_picker.value
        chat.set_visible(mode == "Chat")
        t2i.set_visible(mode == "Text → Image")

    mode_picker.on_change = switch_mode

    page.add(
        ft.Column(
            [
                ft.Row([mode_picker]),
                chat.control(),
                t2i.control(),
            ],
            expand=True,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
