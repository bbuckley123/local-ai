# AGENTS

This repository uses the [AGENTS.md](https://github.com/openai/agents.md) specification to guide
LLM coding agents. The instructions in this file apply to the entire repository.

## General Guidelines

- Use [ripgrep](https://github.com/BurntSushi/ripgrep) (`rg`) for searching. Avoid
  `ls -R` or recursive `grep` as they are slow in large code bases.
- Keep line length at **100 characters** to match the `ruff` configuration.
- Prefer small, focused commits with descriptive commit messages.
- Do not amend or force-push existing commits.

## Development Workflow

1. **Format and lint** all touched files:
   ```bash
   ruff format .
   ruff check .
   ```
2. **Run tests** and ensure they pass:
   ```bash
   pytest
   ```
   The `Makefile` provides shortcuts:
   ```bash
   make fmt
   make lint
   make test
   ```
3. If dependencies are missing, install them inside the existing virtual
   environment or run `uv sync`.
4. Update or add tests when changing behavior.

## Project Notes

- The default chat model lives in `src/assets/models/llm/` and can be overridden by setting
  the `LOCALAI_ASSETS_DIR` environment variable to a directory containing `models/llm`.
- The main application entry point is `src/app.py`; running `make run` launches the UI.
- Packaging is handled through `make pyi`, which wraps PyInstaller.

## Pull Requests

- Ensure the working tree is clean (`git status` shows no changes) before finishing.
- Reference relevant files and test output in your pull request description.
