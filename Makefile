# ===== Makefile (PyInstaller-only) =====

VENV := .venv

ifeq ($(OS),Windows_NT)
  PY    := $(VENV)/Scripts/python.exe
  PYI   := $(VENV)/Scripts/pyinstaller.exe
  # Put src/assets inside the app as "assets"
  ADDD  := --add-data src/assets;assets
else
  PY    := $(VENV)/bin/python
  PYI   := $(VENV)/bin/pyinstaller
  # Put src/assets inside the app as "assets"
  ADDD  := --add-data src/assets:assets
endif

NAME := Local AI (Chat)
ENTRY := src/app.py
PYI_OPTS := --collect-binaries llama_cpp --collect-data llama_cpp

.PHONY: help venv deps run pyi clean
help:
	@echo "make fmt       # format"
	@echo "make lint      # check style only"
	@echo "make venv      # create venv"
	@echo "make deps      # install runtime + packager into venv"
	@echo "make run       # run dev (python src/app.py)"
	@echo "make pyi       # build app with PyInstaller"
	@echo "make clean     # remove build artifacts"
	@echo "make lint-fix  # fix lint issues"
	@echo "make test      # run unit tests"

venv:
	@python -c "import sys,venv,os; p='$(VENV)'; os.path.exists(p) or venv.EnvBuilder(with_pip=True).create(p)" && \
	$(PY) -V

deps: venv
	# flet is needed as a library at runtime; pyinstaller for packing
	$(PY) -m pip install -U pip
	$(PY) -m pip install -U flet pyinstaller ruff black

run: deps
	$(PY) $(ENTRY)

pyi: deps
	$(PYI) --noconfirm --windowed --name "$(NAME)" \
	  $(PYI_OPTS) \
	  $(ADDD) \
	  $(ENTRY)

	mkdir -p "dist/$(NAME).app/Contents/MacOS/assets"
	rsync -a src/assets/ "dist/$(NAME).app/Contents/MacOS/assets/"

clean:
	rm -rf build dist *.spec

test: deps
	@PYTHONPATH=src $(PY) -m pytest -q

.PHONY: fmt lint lint-fix fix
# Use the venv python from your existing vars
RUFF := $(PY) -m ruff

fmt:
	$(RUFF) format .

lint:
	$(RUFF) check .
	$(RUFF) format --check .

# Auto-fix lint issues + format files
lint-fix:
	$(RUFF) check --fix .
	$(RUFF) format .

# nice alias
fix: lint-fix
