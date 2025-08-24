import pytest

import core.llm_adapter as llm_adapter
from core.llm_adapter import LlamaRunner


def test_chatml_prompt_includes_system_and_user():
    result = LlamaRunner._chatml_prompt("sys", "user")
    assert result == (
        "<|im_start|>system\nsys\n<|im_end|>\n"
        "<|im_start|>user\nuser\n<|im_end|>\n"
        "<|im_start|>assistant\n"
    )


def test_chatml_prompt_without_system_prompt():
    result = LlamaRunner._chatml_prompt("", "user")
    assert result == (
        "<|im_start|>user\nuser\n<|im_end|>\n"
        "<|im_start|>assistant\n"
    )


def test_load_requires_llama(monkeypatch, tmp_path):
    monkeypatch.setattr(llm_adapter, "Llama", None)
    runner = llm_adapter.LlamaRunner()
    with pytest.raises(RuntimeError):
        runner.load(str(tmp_path / "model.gguf"))


def test_load_missing_model_raises(monkeypatch, tmp_path):
    class DummyLlama:
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr(llm_adapter, "Llama", DummyLlama)
    runner = llm_adapter.LlamaRunner()
    with pytest.raises(FileNotFoundError):
        runner.load(str(tmp_path / "missing.gguf"))
