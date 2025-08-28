import asyncio
import sys
import types
from types import SimpleNamespace


# Minimal flet stub so ui.chat can be imported without the real dependency.
class _Text:
    def __init__(self, value: str = "", selectable: bool = False, **kw):
        self.value = value

    def update(self):
        pass


class _ListView:
    def __init__(self, **kw):
        self.controls: list[object] = []


class _TextField:
    def __init__(self, **kw):
        self.value = ""

    def update(self):
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
sys.modules.setdefault("flet", fake_flet)

import ui.chat as chat


def test_find_gguf_model_none(tmp_path, monkeypatch):
    monkeypatch.setattr(chat, "LLM_MODELS_DIR", tmp_path)
    assert chat.find_gguf_model() is None


def test_ensure_model_loaded_no_models(tmp_path, monkeypatch):
    monkeypatch.setattr(chat, "LLM_MODELS_DIR", tmp_path)
    notes: list[str] = []
    page = SimpleNamespace(update=lambda: None)
    llm = SimpleNamespace(
        is_loaded=lambda: False,
        is_available=lambda: True,
        load=lambda *a, **kw: None,
    )
    view = chat.ChatView(page, llm, notes.append)
    ok = asyncio.run(view._ensure_model_loaded())
    assert not ok
    assert notes and "No GGUF models found" in notes[-1]
