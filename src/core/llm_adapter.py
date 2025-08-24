import os
import queue
import sys
import threading
from pathlib import Path

try:
    from llama_cpp import Llama
except Exception:
    Llama = None  # handled by UI


class LlamaRunner:
    def __init__(self) -> None:
        self._llm: Llama | None = None
        self.model_path: str | None = None

    def is_available(self) -> bool:
        return Llama is not None

    def is_loaded(self) -> bool:
        return self._llm is not None

    def unload(self) -> None:
        self._llm = None
        self.model_path = None

    def load(self, model_path: str, n_ctx: int = 4096) -> None:
        if not self.is_available():
            raise RuntimeError("llama-cpp-python not installed")

        p = Path(model_path)
        if not p.exists():
            raise FileNotFoundError(f"Model not found: {p.resolve()}")

        # free old
        self.unload()

        base_kwargs = dict(
            model_path=str(p),
            n_ctx=int(n_ctx),
            n_threads=os.cpu_count() or 4,
            verbose=False,
        )

        # In frozen apps (PyInstaller), Metal can fail due to shader/resource lookup.
        # To get you a working build now, force CPU in frozen mode.
        prefer_cpu = bool(getattr(sys, "frozen", False))

        attempts = []
        if prefer_cpu:
            attempts = [dict(n_gpu_layers=0)]
        else:
            attempts = [dict(n_gpu_layers=-1), dict(n_gpu_layers=0)]

        last_err: Exception | None = None
        for a in attempts:
            try:
                self._llm = Llama(**base_kwargs, **a)
                last_err = None
                break
            except Exception as e:
                last_err = e
                self._llm = None

        if self._llm is None:
            # Surface full detail; UI will show class + message
            raise RuntimeError(f"Llama init failed ({type(last_err).__name__}): {last_err}")

        self.model_path = str(p)

    # ---- ChatML via create_completion (works across llama-cpp versions) ----
    @staticmethod
    def _chatml_prompt(system_prompt: str, user_prompt: str) -> str:
        parts = []
        sys_p = system_prompt.strip()
        if sys_p:
            parts.append(f"<|im_start|>system\n{sys_p}\n<|im_end|>\n")
        parts.append(f"<|im_start|>user\n{user_prompt.strip()}\n<|im_end|>\n")
        parts.append("<|im_start|>assistant\n")
        return "".join(parts)

    def stream_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> tuple["queue.Queue[str | None]", threading.Event, threading.Thread]:
        if self._llm is None:
            raise RuntimeError("Model not loaded")

        q: queue.Queue[str | None] = queue.Queue()
        cancel = threading.Event()

        def _worker():
            try:
                prompt = self._chatml_prompt(system_prompt, user_prompt)
                stops = ["<|im_end|>", "<|endoftext|>"]

                for chunk in self._llm.create_completion(
                    prompt=prompt,
                    stream=True,
                    max_tokens=int(max_tokens),
                    temperature=float(temperature),
                    top_p=0.9,
                    stop=stops,
                ):
                    if cancel.is_set():
                        break
                    try:
                        delta = chunk["choices"][0].get("text", "")
                    except Exception:
                        delta = ""
                    if delta:
                        q.put(delta)
            except Exception as e:
                q.put(f"\n[Error: {e}]\n")
            finally:
                q.put(None)

        th = threading.Thread(target=_worker, daemon=True)
        th.start()
        return q, cancel, th
