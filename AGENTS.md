# Repository Guidelines (GDk9)

## Project structure
- `gdk9/` — Python package (CLI entry `gdk9.cli:main`, kernel, DCG, crypto, plugins, state).
- `tests/` — pytest suite (mirrors package concerns; not a `src/` tree).
- `docs/` — handbook, cheatsheet, SECURITY, PROVE, architecture notes.
- `examples/` — runnable scripts `01_*.py` … `09_*.py`.
- `scripts/` — small utilities (`export_json.py`, `profile_compare.py`, …).
- `plugins/` — distributable JSON/YAML plugin packs.
- No `src/`, no npm app, no auth service fiction.

## Build, test, lint
```bash
pip install -e ".[dev,secure]"   # or: make setup then pip install -e ".[dev]"
make test                        # python -m pytest -q
make lint                        # ruff + pyflakes
make fmt                         # black
make build                       # sdist + wheel
```
Prove gate details: `docs/PROVE.md` (critical ruff select + pytest; green CI on `main`).

## Coding style
- Python 3.9+; package code under `gdk9/`.
- Prefer snake_case modules/functions; keep diffs minimal; do not mass-reformat.
- Ruff line length 100 (`pyproject.toml`).

## Commits & PRs
- Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`.
- Small atomic commits; PRs describe why, list touched paths, keep CI green.

## Security
- Never commit secrets. Secure crypto mode is Fernet + PBKDF2-HMAC-SHA256 (200k) — see `docs/SECURITY.md` / `gdk9/crypto.py`.
- Load plugins only from trusted paths (`docs/PLUGINS.md`).

## Agent notes
- Prefer `rg` and small diffs. Do not invent maths or touch kernel/DCG/energy core unless the task requires it.
- Prove locally before claiming done: `ruff check gdk9 --select E9,F63,F7,F82` and `python -m pytest -q`.
