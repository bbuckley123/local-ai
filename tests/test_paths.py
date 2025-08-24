import sys

from paths import _dev_assets_dir, _frozen_assets_dir


def test_frozen_assets_dir_defaults_to_dev(monkeypatch):
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    monkeypatch.setattr(sys, "executable", "/usr/bin/python")
    assert _frozen_assets_dir() == _dev_assets_dir()
