# tests/conftest.py
import sys
import types
from types import SimpleNamespace


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


# Build the fake module
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

# Install into sys.modules before any tests import ui.chat
sys.modules["flet"] = fake_flet
