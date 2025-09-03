# Contributing to Local AI

Thanks for taking the time to contribute! The following guidelines help you set up your
environment and ensure your contributions meet project standards.

## Setup

1. **Install Python**: Local AI requires Python 3.9 or newer.
2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```
3. **Install dependencies** using either `pip` or [`uv`](https://github.com/astral-sh/uv):
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

## Coding Standards

- Keep line length under **100 characters**.
- Format code with `ruff format .` and lint with `ruff check .`.
- Ensure all tests pass by running `pytest`.
- When modifying behavior, add or update tests as needed.

These commands are also available through the `Makefile`:
```bash
make fmt     # format
make lint    # lint only
make test    # run tests
```

## Secret Scanning

Run a history scan before pushing to ensure no credentials are committed:

```bash
gitleaks detect --source . --report-format json --report-path gitleaks-report.json
```

If `gitleaks` is unavailable, try `git-secrets`:

```bash
git-secrets --scan-history
```

Rotate any exposed credentials and scrub them from the repository history before opening a
pull request.

## Pull Request Process

1. Fork the repository and create your feature or bug fix.
2. Run formatting, linting, and tests before committing.
3. Push your changes and open a pull request against `main`.
4. Reference relevant files and test output in the pull request description.
5. By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

We appreciate your contributions and efforts to improve Local AI!
