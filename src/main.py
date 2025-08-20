# src/main.py
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional
import flet as ft

APP_NAME = "Local AI"
APP_DIR = Path.home() / "LocalAI"
OUTPUTS_DIR = APP_DIR / "outputs" / "txt2img"
APP_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

async def fake_llm_stream(prompt: str, cancel: asyncio.Event):
    """Stub stream; replace with llama.cpp later."""
    text = f"Echoing: {prompt.strip()}\n\n"
    for ch in text:
        if cancel.is_set():
            return
        yield ch
        await asyncio.sleep(0.01)

def main(page: ft.Page) -> None:
    page.title = APP_NAME
    page.window_width = 900
    page.window_height = 700
    page.padding = 16
    page.theme_mode = "light"

    # ===== Mode switch (replaces Tabs) =====
    mode_picker = ft.Dropdown(
        label="Mode",
        options=[ft.dropdown.Option("Chat"), ft.dropdown.Option("Text → Image")],
        value="Chat",
        width=220,
    )

    # ======== Chat view ========
    chat_cancel = None  # type: Optional[asyncio.Event]
    chat_task = None    # type: Optional[asyncio.Task]

    chat_system = ft.TextField(label="System prompt (optional)", multiline=True, min_lines=2)
    chat_prompt = ft.TextField(label="Prompt", multiline=True, min_lines=4, expand=True)
    chat_temp = ft.Slider(label="Temperature", min=0.0, max=1.5, divisions=15, value=0.7, width=300)
    chat_out = ft.TextField(label="Output", multiline=True, min_lines=12, read_only=True, expand=True)
    chat_status = ft.Text(value="Ready.")
    btn_chat_go = ft.ElevatedButton("Generate ▶︎")
    btn_chat_cancel = ft.OutlinedButton("Cancel ⏹", disabled=True)

    def set_chat_busy(busy: bool) -> None:
        btn_chat_go.disabled = busy
        btn_chat_cancel.disabled = not busy
        chat_status.value = "Running…" if busy else "Ready."
        page.update()

    async def run_chat() -> None:
        # stream tokens into chat_out
        set_chat_busy(True)
        chat_out.value = ""
        page.update()
        async for tok in fake_llm_stream(prompt=chat_prompt.value, cancel=chat_cancel):
            chat_out.value += tok
            chat_out.update()
        set_chat_busy(False)

    def on_chat_go(_: ft.ControlEvent) -> None:
        nonlocal chat_cancel, chat_task
        if not chat_prompt.value.strip():
            page.snack_bar = ft.SnackBar(ft.Text("Enter a prompt first."))
            page.snack_bar.open = True
            page.update()
            return
        chat_cancel = asyncio.Event()
        chat_task = page.run_task(run_chat())

    def on_chat_cancel(_: ft.ControlEvent) -> None:
        nonlocal chat_cancel
        if chat_cancel and not chat_cancel.is_set():
            chat_cancel.set()

    btn_chat_go.on_click = on_chat_go
    btn_chat_cancel.on_click = on_chat_cancel

    chat_view = ft.Column(
        [
            chat_system,
            chat_prompt,
            ft.Row([chat_temp]),
            ft.Row([btn_chat_go, btn_chat_cancel, chat_status], spacing=12),
            chat_out,
        ],
        expand=True,
        visible=True,
    )

    # ======== Text → Image view (stub) ========
    t2i_prompt = ft.TextField(label="Prompt", multiline=True, min_lines=4, expand=True)
    t2i_steps = ft.Slider(label="Steps", min=5, max=50, divisions=45, value=20, width=250)
    t2i_guidance = ft.Slider(label="Guidance (CFG)", min=1.0, max=15.0, divisions=28, value=7.5, width=250)
    t2i_status = ft.Text(value="Not wired yet.")
    t2i_placeholder = ft.Container(content=ft.Text("Image will appear here"), height=360, border_radius=8)
    btn_t2i_go = ft.ElevatedButton("Generate")
    btn_t2i_cancel = ft.OutlinedButton("Cancel", disabled=True)

    def on_t2i_go(_: ft.ControlEvent) -> None:
        page.snack_bar = ft.SnackBar(ft.Text("Text→Image not wired yet."))
        page.snack_bar.open = True
        page.update()

    btn_t2i_go.on_click = on_t2i_go

    t2i_view = ft.Column(
        [
            t2i_prompt,
            ft.Row([t2i_steps, t2i_guidance], spacing=24),
            ft.Row([btn_t2i_go, btn_t2i_cancel, t2i_status], spacing=12),
            t2i_placeholder,
        ],
        expand=True,
        visible=False,
    )

    # ======== Switch logic ========
    def switch_mode(e: ft.ControlEvent) -> None:
        mode = mode_picker.value
        chat_view.visible = mode == "Chat"
        t2i_view.visible = mode == "Text → Image"
        page.update()

    mode_picker.on_change = switch_mode

    # ======== Layout ========
    page.add(
        ft.Column(
            [
                ft.Row([mode_picker]),
                chat_view,
                t2i_view,
            ],
            expand=True,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
