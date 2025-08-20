import os
import threading
import queue
from pathlib import Path
from typing import Optional, Tuple

try:
    from llama_cpp import Llama
except Exception:
    Llama = None  # we'll handle missing dep in UI

class LlamaRunner:
    """
    Tiny wrapper around llama-cpp-python with Metal offload.
    - load(model_path)
    - stream_chat(system, user, temperature, max_tokens) -> (Queue, cancel_event, Thread)
    """
    def __init__(self) -> None:
        self._llm: Optional[Llama] = None
        self.model_path: Optional[str] = None

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
            raise FileNotFoundError(f"Model not found: {p}")

        # free old
        self.unload()

        # create new (Metal GPU offload)
        self._llm = Llama(
            model_path=str(p),
            n_ctx=int(n_ctx),
            n_gpu_layers=-1,                      # offload all layers to Metal
            n_threads=os.cpu_count() or 4,
            verbose=False,
        )
        self.model_path = str(p)

    def stream_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> Tuple["queue.Queue[Optional[str]]", threading.Event, threading.Thread]:
        if self._llm is None:
            raise RuntimeError("Model not loaded")

        q: "queue.Queue[Optional[str]]" = queue.Queue()
        cancel = threading.Event()

        def _worker():
            try:
                messages = []
                if system_prompt.strip():
                    messages.append({"role": "system", "content": system_prompt.strip()})
                messages.append({"role": "user", "content": user_prompt.strip()})

                for chunk in self._llm.create_chat_completion(
                    messages=messages,
                    stream=True,
                    temperature=float(temperature),
                    max_tokens=int(max_tokens),
                ):
                    if cancel.is_set():
                        break
                    try:
                        delta = chunk["choices"][0]["delta"].get("content", "")
                    except Exception:
                        delta = ""
                    if delta:
                        q.put(delta)
            except Exception as e:
                q.put(f"\n[Error: {e}]\n")
            finally:
                q.put(None)  # sentinel

        th = threading.Thread(target=_worker, daemon=True)
        th.start()
        return q, cancel, th
