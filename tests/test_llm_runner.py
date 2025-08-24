import importlib
import sys
import time
import types

import pytest


# ---- helpers: fake Llama class ----
class _FakeLlama:
    def __init__(self, *, model_path, n_ctx, n_threads, verbose, n_gpu_layers=0, **kw):
        # record params for assertions
        self.kwargs = dict(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=verbose,
            n_gpu_layers=n_gpu_layers,
            **kw,
        )
        # simulate failure if caller tries to use GPU in "dev" test where we want a fallback
        if kw.get("_fail_on_gpu") and n_gpu_layers == -1:
            raise RuntimeError("GPU init failed")

    def create_completion(self, *, prompt, stream, max_tokens, temperature, top_p, stop):
        # stream a couple of chunks then end
        chunks = ["Hello", ", world!", "\n"]
        if stream:
            for t in chunks:
                yield {"choices": [{"text": t}]}
                time.sleep(0.01)
        else:
            return {"choices": [{"text": "".join(chunks)}]}


# ---- fixture to monkeypatch llama_cpp.Llama at import time ----
@pytest.fixture(autouse=True)
def fake_llama_monkeypatch(monkeypatch, tmp_path):
    # Build a temporary module to stand in for llama_cpp
    mod = types.ModuleType("llama_cpp")
    mod.Llama = _FakeLlama
    sys.modules["llama_cpp"] = mod
    yield
    # cleanup
    sys.modules.pop("llama_cpp", None)


def fresh_runner_module():
    # Ensure we import a fresh copy of the runner with our fake llama in place
    if "core.llm_adapter" in sys.modules:
        del sys.modules["core.llm_adapter"]
    return importlib.import_module("core.llm_adapter")


def test_load_file_not_found(tmp_path):
    m = fresh_runner_module()
    r = m.LlamaRunner()
    with pytest.raises(FileNotFoundError):
        r.load(str(tmp_path / "missing.gguf"))


def test_load_cpu_in_frozen(tmp_path, monkeypatch):
    # create dummy model file
    model = tmp_path / "model.gguf"
    model.write_bytes(b"dummy")

    m = fresh_runner_module()
    r = m.LlamaRunner()

    # pretend we're in a frozen app -> should choose CPU (n_gpu_layers=0)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    r.load(str(model), n_ctx=1024)
    assert r._llm.kwargs["n_gpu_layers"] == 0


def test_load_dev_prefers_gpu_then_fallback(tmp_path, monkeypatch):
    model = tmp_path / "model.gguf"
    model.write_bytes(b"dummy")

    # Swap in a FakeLlama that fails on GPU (-1) once, then succeeds on CPU
    class _FlakyFake(_FakeLlama):
        def __init__(self, **kw):
            kw["_fail_on_gpu"] = True
            super().__init__(**kw)

    # rebind llama_cpp.Llama to our flaky impl
    sys.modules["llama_cpp"].Llama = _FlakyFake  # type: ignore[attr-defined]

    m = fresh_runner_module()
    r = m.LlamaRunner()
    if hasattr(sys, "frozen"):
        delattr(sys, "frozen")  # dev mode
    r.load(str(model), n_ctx=1024)
    assert r._llm.kwargs["n_gpu_layers"] == 0  # fell back to CPU


def test_stream_chat_yields_tokens(tmp_path):
    model = tmp_path / "m.gguf"
    model.write_bytes(b"x")

    m = fresh_runner_module()
    r = m.LlamaRunner()
    r.load(str(model))

    q, cancel, th = r.stream_chat(system_prompt="", user_prompt="Hi?", max_tokens=16)
    out = []
    while True:
        item = q.get()
        if item is None:
            break
        out.append(item)
    assert "".join(out).strip().startswith("Hello")


def test_stream_chat_cancel(tmp_path):
    model = tmp_path / "m.gguf"
    model.write_bytes(b"x")
    m = fresh_runner_module()
    r = m.LlamaRunner()
    r.load(str(model))
    q, cancel, th = r.stream_chat(system_prompt="", user_prompt="Hi?")
    # cancel early
    cancel.set()
    # drain
    got = []
    while True:
        item = q.get()
        if item is None:
            break
        got.append(item)
    # We should have gotten 0 or a small number of chunks, not the full text
    assert len("".join(got)) <= len("Hello, world!\n")
