README - Build & Test

Overview
- This repository is a Python CLI package (`gdk9-cli`) using `setuptools`.
- Requires Python >= 3.9.

Quick start (recommended)
1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Upgrade pip and install dev tools (Makefile helper):

```bash
pip install --upgrade pip
make setup
```

Build
- Build wheel and sdist (requires `build` package):

```bash
make build
# or explicitly
python3 -m pip install --upgrade build
python3 -m build
```

Install locally

```bash
pip install -e .
# or install a distribution from dist/
pip install dist/*.whl
```

Run the CLI

```bash
make run
# or, after installing the package
gdk9 --help
```

Tests

```bash
make test
# or direct
python3 -m unittest discover -s tests -p 'test_*.py'
```

Lint & Format

```bash
make lint
make fmt
```

Packaging

```bash
make package
# calls: python3 scripts/make_zip.py -> creates artifacts under dist/
```

Notes
- `pyproject.toml` uses `setuptools.build_meta`. The `build` package is required to run `python -m build`.
- `Makefile` uses `PY ?= python3`; you can override e.g. `make PY=python`.
