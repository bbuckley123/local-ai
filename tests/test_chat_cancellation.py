import asyncio
import queue
import sys
import threading
import time
import types
from types import SimpleNamespace

import ui.chat as chat


# Minimal flet stub so ui.chat can be imported without the real dependency.
class _Text:
    def __init__(self, value: str = "", selectable: bool = False, **kw):
        self.value = value

    def update(self) -> None:
        pass


class _ListView:
    def __init__(self, **kw):
        self.controls: list[object] = []


class _TextField:
    def __init__(self, **kw):
        self.value = ""

    def update(self) -> None:
        pass


class _Button:
    def __init__(self, *a, **kw):
        self.disabled = False


class _Row:
    def __init__(self, controls, vertical_alignment=None):
        pass


class _Column:
    def __init__(self, controls, expand=False):
        pass


class _SnackBar:
    def __init__(self, text):
        self.open = False


fake_flet = types.ModuleType("flet")
fake_flet.Text = _Text
fake_flet.ListView = _ListView
fake_flet.TextField = _TextField
fake_flet.ElevatedButton = _Button
fake_flet.Row = _Row
fake_flet.Column = _Column
fake_flet.CrossAxisAlignment = SimpleNamespace(END=None)
fake_flet.SnackBar = _SnackBar
fake_flet.Control = object
fake_flet.ControlEvent = object
fake_flet.Page = object
sys.modules["flet"] = fake_flet


class DummyRunner:
    def is_loaded(self) -> bool:
        return True

    def is_available(self) -> bool:
        return True

    def stream_chat(self, *, system_prompt, user_prompt, temperature, max_tokens):
        q: queue.Queue[str | None] = queue.Queue()
        cancel = threading.Event()

        def worker() -> None:
            for ch in "hi":
                if cancel.is_set():
                    break
                q.put(ch)
                time.sleep(0.05)
            q.put(None)

        th = threading.Thread(target=worker)
        th.start()
        return q, cancel, th


class DummyPage:
    def run_task(self, coro, *args):
        return asyncio.create_task(coro(*args))

    def update(self) -> None:
        pass


def test_on_send_cancels_previous() -> None:
    async def run_test() -> None:
        page = DummyPage()
        notes: list[str] = []
        view = chat.ChatView(page, DummyRunner(), notes.append)

        view.input.value = "first"
        view._on_send(None)
        await asyncio.sleep(0.06)
        first_flag = view._cancel_flag
        first_thread = view._worker_thread
        first_task = view._chat_task
        assert first_flag and not first_flag.is_set()
        assert first_thread and first_thread.is_alive()

        view.input.value = "second"
        view._on_send(None)
        assert first_flag.is_set()
        assert first_thread and not first_thread.is_alive()
        assert view._chat_task and view._chat_task is not first_task

        view._cancel_chat()
        await asyncio.sleep(0.01)

    asyncio.run(run_test())
