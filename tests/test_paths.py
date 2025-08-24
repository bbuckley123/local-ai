import importlib
import sys


def reload_paths(tmp_assets=None, frozen=False, meipass=None, exe=None):
    # Build a fresh module namespace so globals recompute on import
    if "paths" in sys.modules:
        del sys.modules["paths"]

    # Simulate environment
    if frozen:
        sys.frozen = True  # type: ignore[attr-defined]
    else:
        if hasattr(sys, "frozen"):
            delattr(sys, "frozen")  # type: ignore[attr-defined]
    if meipass is not None:
        sys._MEIPASS = str(meipass)  # type: ignore[attr-defined]
    elif hasattr(sys, "_MEIPASS"):
        delattr(sys, "_MEIPASS")  # type: ignore[attr-defined]
    if exe is not None:
        sys.executable = str(exe)

    # Create a fake module file layout: paths.py expects src/paths.py -> src/assets
    # We don’t actually need to move files; we’ll monkeypatch __file__ after import
    import paths

    if tmp_assets is not None:
        # monkeypatch module-level __file__ to point inside a temp src/
        # then recompute ASSETS_DIR/LLM_MODELS_DIR based on that
        paths.__file__ = str(tmp_assets.parent / "paths.py")  # type: ignore
        importlib.reload(paths)
    return paths


def test_dev_assets_dir(tmp_path, monkeypatch):
    # Create a fake src/assets/models/llm tree in tmp
    src_dir = tmp_path / "src"
    assets_root = src_dir / "assets"
    llm_dir = assets_root / "models" / "llm"
    llm_dir.mkdir(parents=True)

    # Tell paths.py to use our temp assets
    monkeypatch.setenv("LOCALAI_ASSETS_DIR", str(assets_root))

    # Reload module so it picks up the env override
    if "paths" in sys.modules:
        del sys.modules["paths"]
    import paths

    assert paths.LLM_MODELS_DIR.resolve() == llm_dir.resolve()


def test_frozen_meipass(tmp_path):
    meipass = tmp_path / "_MEIPASS"
    assets = meipass / "assets" / "models" / "llm"
    assets.mkdir(parents=True)
    exe = tmp_path / "dummy-exe"
    exe.write_bytes(b"x")
    paths = reload_paths(frozen=True, meipass=meipass, exe=exe)
    assert assets == paths.LLM_MODELS_DIR


def test_frozen_macos_onedir(tmp_path):
    # Simulate .../My.app/Contents/MacOS/Local AI (Chat)
    app = tmp_path / "Local AI (Chat).app"
    macos = app / "Contents" / "MacOS"
    macos.mkdir(parents=True)
    exe = macos / "Local AI (Chat)"
    exe.write_bytes(b"x")
    assets = macos / "assets" / "models" / "llm"
    assets.mkdir(parents=True)

    paths = reload_paths(frozen=True, exe=exe)
    assert assets == paths.LLM_MODELS_DIR
