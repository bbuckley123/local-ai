# Local AI

Local AI is a minimal desktop chat application that lets you run small language models completely offline. It uses [Flet](https://flet.dev/) for the user interface and [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) for model inference. The goal of the project is to provide a simple starting point for experimenting with local models without relying on any external APIs.

## Features

- Cross‑platform graphical interface built with Flet.
- Loads [GGUF](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md) models through `llama-cpp-python`.
- Streams model output token by token for a responsive chat experience.
- Configurable asset directory and model location.
- Tested using `pytest` with a lightweight fake model for fast feedback.

## Project Layout

```text
src/
  app.py             # Flet application entry point
  core/llm_adapter.py# Wrapper around llama-cpp-python
  ui/chat.py         # Chat view and interaction logic
  paths.py           # Resolves asset and output directories
  assets/            # (not tracked) place models and other resources here
```

## Getting Started

### 1. Install Python

Ensure you have **Python 3.9 or newer** available on your system.

### 2. Create a virtual environment

You can use any tool you like. Using `python -m venv`:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

### 3. Install dependencies

Install runtime and development dependencies. The project uses [`uv`](https://github.com/astral-sh/uv) but regular `pip` works as well.

Using `pip`:

```bash
pip install -r <(python - <<'PY'
import toml
print('\n'.join(toml.load('pyproject.toml')['project']['dependencies']))
PY
)
pip install flet[all]==0.28.3 ruff black pytest
```

Or with `uv`:

```bash
uv sync
```

### 4. Download a model

Place a GGUF model file in `src/assets/models/llm/`. The application defaults to
`qwen2.5-7b-instruct-q4_k_m.gguf`, so the final path should look like:

```
src/assets/models/llm/qwen2.5-7b-instruct-q4_k_m.gguf
```

If you want to store assets elsewhere, set `LOCALAI_ASSETS_DIR` to the directory
that contains `models/llm`. The `paths.py` module will pick it up automatically.

### 5. Run the app

```bash
flet run src/app.py
```

The window will open with a transcript view and a single input box. On first
send the model loads from disk and the response streams back into the chat.

## Development

Run formatting, linting and tests before committing:

```bash
ruff format .
ruff check .
pytest
```

These commands are also wrapped in the `Makefile`:

```bash
make fmt     # format
make lint    # lint only
make test    # run tests
```

## Packaging

The repository contains a small `Makefile` that bundles the application with
[PyInstaller](https://pyinstaller.org). From an activated virtual environment
run:

```bash
make pyi
```

The resulting application bundle will appear under `dist/`.

## Troubleshooting

- **Missing model:** The chat view looks for the default model path. If it is
  missing you will see a notification. Download the model or update the code to
  point to your own file.
- **GPU issues:** When packaging with PyInstaller the runner forces CPU mode by
  default to avoid Metal/OpenCL initialization failures.

## Contributing

Pull requests and issues are welcome. Please format code with `ruff format`, run
`ruff check` and ensure `pytest` passes before submitting.

## License

This project has not been assigned a license yet.

