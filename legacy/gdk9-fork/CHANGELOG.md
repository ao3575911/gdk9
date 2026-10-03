# Changelog

All notable changes to this project are documented here.

## 0.2.0 — Repo hygiene and CI
- Remove committed build artifacts and caches (`dist/`, `gdk9_cli.egg-info/`, `.pytest_cache/`, `__pycache__/`, `.venv/`).
- Delete duplicated trees and nested repos (`Gdk9-Core/`, nested `gdk9/.git`). Canonical source is `gdk9/` at the repository root.
- Add a comprehensive `.gitignore` to prevent re-adding artifacts and secrets.
- Remove sensitive files from version control (`config/secret_key`, `codex.sqlite3`). Rotate any corresponding secrets.
- Add GitHub Actions CI (Python 3.9–3.12) running lint (ruff+pyflakes) and `make test`.
- Update Makefile: `make lint` prefers `ruff`, falls back to `pyflakes`; `make fmt` uses `black` if installed; `make setup` installs dev tools.
- Bump package version to `0.2.0` in `pyproject.toml`.

## 0.1.0 — Initial release
- Initial CLI, tokenization, rules, and tests.
