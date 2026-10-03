.PHONY: setup build run test lint fmt help package

PY ?= python3

help:
	@echo "Targets: setup build run test lint fmt"

setup:
	@$(PY) -V
	@echo "Installing dev tools (ruff, pyflakes, black)..."
	@$(PY) -m pip install -q --upgrade pip || true
	@$(PY) -m pip install -q ruff pyflakes black || true

build:
	$(PY) -m build || echo "Install 'build' to package (pip install build)"

run:
	$(PY) -m gdk9.cli --help

test:
	$(PY) -m unittest discover -s tests -p 'test_*.py'

lint:
	ruff check . || echo "Install ruff for linting (pip install ruff)"
	$(PY) -m pyflakes gdk9 || echo "Install pyflakes for linting (pip install pyflakes)"

fmt:
	black . || echo "Install black to format (pip install black)"

package:
	@mkdir -p dist
	python3 scripts/make_zip.py
