# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### License
- Align root `LICENSE` file to **AGPL-3.0-or-later** (was GPL-3 text; matches pyproject/CLI/docs).


### Package
- Add `[project.optional-dependencies].build` (`build`) and include `build` in the
  `dev` extra so `pip install '.[build]'` / `'.[dev]'` yields a reproducible sdist/wheel path.
- Harden `make build` to ensure the `build` package is present, then run
  `python -m build` and list `dist/` artifacts.
- Add `docs/RELEASE.md` with exact local build, `twine check`, and optional TestPyPI
  upload/install commands (no auto-publish workflow required).

---

## [0.3.0] — 2026-05-15

### License
- Relicensed from GPL-3.0 to **AGPL-3.0-or-later**. This ensures network use of GDk9
  services requires source disclosure — aligned with community and commercial-ecosystem goals.
  AGPL permits dual licensing for commercial deployments while keeping the commons open.

### Documentation
- Added `docs/index.md` — full documentation tree and navigation guide.
- Added `docs/CHEATSHEET.md` — comprehensive quick-reference: all commands, flags,
  formulas, symmetry tables, energy arithmetic, and example workflows.
- Added `docs/QUICKSTART.md` — five-minute guide from install to first analysis.
- Added `docs/ARCHITECTURE.md` — module dependency map, kernel boundary, data flow diagram.
- Added `docs/CONFIGURATION.md` — principle files, state files, plugin auto-boot, env vars.
- Added `docs/API.md` — public Python API surface for embedding GDk9 as a library.
- Added `docs/SECURITY.md` — threat model, crypto module guidance, secret handling.
- Removed `Proprietary` references from `docs/HANDBOOK.md` and `cli.py --version` string.

### Scripts
- Added `scripts/batch_analyze.py` — analyze every `.txt`/`.md` file in a directory,
  emit CSV or JSON report with per-file energy totals and digital roots.
- Added `scripts/export_json.py` — full JSON export of analysis, profile, and assign
  for a single input; suitable for piping into downstream tools.
- Added `scripts/watch_file.py` — inotify-style poll loop: re-analyze a file whenever
  it changes, printing live energy delta to stdout.
- Added `scripts/profile_compare.py` — side-by-side energy histogram comparison of two
  input files or strings; outputs unified diff of distribution bins.

### Plugins
- Added `plugins/harmonic_suite.json` — Root/Wave/Peak triad fusion rules plus
  symbol energy tuning for punctuation commonly used in verse or note-taking.
- Added `plugins/crypto_keys.json` — asymmetric-class split and Z-flip fusion rules
  designed for GDk9 key-derivation workflows; includes conservation checks.
- Added `plugins/language_metrics.json` — fusion rules for sentence-level energy
  aggregation; symbol energy overrides for common linguistic punctuation.
- Added `plugins/ninefold_extended.json` — extends the default Ninefold Grid with
  curated symbol energies for Unicode math, arrows, and box-drawing characters.

### Data
- Completed `pairs.csv` — expanded from 5 rows to 70+ rows covering:
  - Visual confusion (homoglyph) pairs
  - DC ↔ AC form pairs (all 26 uppercase/lowercase letter pairs)
  - Same-energy substitution pairs (A1Z26 digital-root groups)
  - Involutive symmetry triplets (N, S, Z and their lowercase counterparts)

### Package
- Updated `pyproject.toml`: version `0.3.0`, AGPL-3.0-or-later license,
  full author field, `dev` optional extras, ruff configuration.

---

## [0.2.0] — Repo hygiene and CI
- Remove committed build artifacts and caches (`dist/`, `gdk9_cli.egg-info/`, `.pytest_cache/`, `__pycache__/`, `.venv/`).
- Delete duplicated trees and nested repos (`Gdk9-Core/`, nested `gdk9/.git`). Canonical source is `gdk9/` at the repository root.
- Add a comprehensive `.gitignore` to prevent re-adding artifacts and secrets.
- Remove sensitive files from version control (`config/secret_key`, `codex.sqlite3`). Rotate any corresponding secrets.
- Add GitHub Actions CI (Python 3.9–3.12) running lint (ruff+pyflakes) and `make test`.
- Update Makefile: `make lint` prefers `ruff`, falls back to `pyflakes`; `make fmt` uses `black` if installed; `make setup` installs dev tools.
- Bump package version to `0.2.0` in `pyproject.toml`.

## [0.1.0] — Initial release
- Initial CLI, tokenization, rules, and tests.