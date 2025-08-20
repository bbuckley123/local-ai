import asyncio
from pathlib import Path
from typing import Optional, Callable
import flet as ft

from core.llm_adapter import LlamaRunner
from paths import LLM_MODELS_DIR

NotifyFn = Callable[[str], None]


class ChatView:
    """
    Minimal chat UI:
      - Transcript (scrolling) on top
      - One input field + Send on bottom
    Lazy-loads a default model on first send if not already loaded.
    """

    DEFAULT_MODEL = LLM_MODELS_DIR / "Llama-3.1-8B-Instruct-Q4_K_M.gguf"

    def __init__(self, page: ft.Page, llm: LlamaRunner, notify: NotifyFn) -> None:
        self.page = page
        self.llm = llm
        self.notify = notify

        # state
        self._chat_task: Optional[asyncio.Task] = None

        # transcript
        self.transcript = ft.ListView(
            expand=True, spacing=8, auto_scroll=True, padding=10
        )

        # compose area
        self.input = ft.TextField(
            hint_text="Type your message…",
            autofocus=True,
            expand=True,
            min_lines=1,
            max_lines=4,
        )
        self.btn_send = ft.ElevatedButton("Send", on_click=self._on_send)
        self.status = ft.Text("Ready.")

        # layout
        self.container = ft.Column(
            [
                self.transcript,
                ft.Row([self.input, self.btn_send], vertical_alignment=ft.CrossAxisAlignment.END),
                self.status,
            ],
            expand=True,
        )

    # ---- public API ----
    def control(self) -> ft.Control:
        return self.container

    def set_visible(self, visible: bool) -> None:
        self.container.visible = visible
        self.page.update()

    # ---- helpers ----
    def _set_busy(self, running: bool) -> None:
        self.btn_send.disabled = running
        self.status.value = "Thinking…" if running else "Ready."
        self.page.update()

    def _append_user(self, text: str) -> None:
        self.transcript.controls.append(
            ft.Text(f"You: {text}", selectable=True)
        )
        self.page.update()

    def _append_assistant_stub(self) -> ft.Text:
        assistant_text = ft.Text("Assistant: ", selectable=True)
        self.transcript.controls.append(assistant_text)
        self.page.update()
        return assistant_text

    async def _ensure_model_loaded(self) -> bool:
        if self.llm.is_loaded():
            return True
        if not self.llm.is_available():
            self.notify("llama-cpp-python not installed. `pip install llama-cpp-python`")
            return False
        try:
            self.status.value = f"Loading model: {self.DEFAULT_MODEL.name}"
            self.page.update()
            self.llm.load(str(self.DEFAULT_MODEL), n_ctx=4096)
            self.notify(f"Loaded: {self.DEFAULT_MODEL.name}")
            self.status.value = "Model loaded."
            self.page.update()
            return True
        except Exception as e:
            self.notify(f"Failed to load model: {e}")
            self.status.value = "Load failed."
            self.page.update()
            return False

    async def _run_chat(self, prompt: str) -> None:
        if not await self._ensure_model_loaded():
            return

        self._set_busy(True)

        # create assistant message placeholder to stream into
        assistant_node = self._append_assistant_stub()

        # start streaming
        q, cancel_flag, th = self.llm.stream_chat(
            system_prompt="",             # keep it simple
            user_prompt=prompt,
            temperature=0.7,              # sensible default; hidden from UI
            max_tokens=512,               # sensible default; hidden from UI
        )

        # read stream
        try:
            while True:
                try:
                    item = q.get_nowait()
                except Exception:
                    item = ...

                if item is None:
                    break
                elif item is ...:
                    if not th.is_alive():
                        break
                    await asyncio.sleep(0.01)
                else:
                    assistant_node.value += item
                    assistant_node.update()
        finally:
            self._set_busy(False)

    # ---- events ----
    def _on_send(self, _: ft.ControlEvent) -> None:
        text = self.input.value.strip()
        if not text:
            self.notify("Type something first.")
            return

        # move input to transcript and clear box
        self._append_user(text)
        self.input.value = ""
        self.input.update()

        # kick off async chat
        if self._chat_task and not self._chat_task.done():
            self.notify("Still answering the previous message.")
            return
        self._chat_task = self.page.run_task(self._run_chat, text)
