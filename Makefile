.PHONY: setup build run test lint fmt help package

PY ?= python3

help:
	@echo "Targets: setup build run test lint fmt package"
	@echo "  build   — sdist + wheel via python -m build (installs build if needed)"

setup:
	@$(PY) -V
	@echo "Installing dev tools (ruff, pyflakes, black, build)..."
	@$(PY) -m pip install -q --upgrade pip || true
	@$(PY) -m pip install -q ruff pyflakes black build || true

build:
	@echo "Ensuring build backend is available..."
	@$(PY) -c "import build" 2>/dev/null || $(PY) -m pip install -q 'build>=1.0'
	$(PY) -m build
	@echo "Artifacts in dist/:"
	@ls -1 dist/*.tar.gz dist/*.whl 2>/dev/null || ls -1 dist/

run:
	$(PY) -m gdk9.cli --help

test:
	$(PY) -m pytest -q

lint:
	ruff check . || echo "Install ruff for linting (pip install ruff)"
	$(PY) -m pyflakes gdk9 || echo "Install pyflakes for linting (pip install pyflakes)"

fmt:
	black . || echo "Install black to format (pip install black)"

package:
	@mkdir -p dist
	python3 scripts/make_zip.py