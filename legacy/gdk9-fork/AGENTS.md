# Repository Guidelines

## Project Structure & Module Organization
- `src/` application code organized by feature; keep files focused and cohesive.
- `tests/` mirrors `src/` paths for unit/integration tests (e.g., `tests/auth/test_login.*`).
- `scripts/` utility and CI helpers; keep scripts idempotent and documented.
- `docs/` project docs; `assets/` static files; `config/` environment templates (see `.env.example`).
- Prefer feature-first modules (e.g., `src/auth/`, `src/payments/`) over giant utility buckets.

## Build, Test, and Development Commands
- `make setup` install dependencies for local dev (delegates to package manager).
- `make build` produce release artifacts/bundles.
- `make run` start the local app/entrypoint.
- `make test` run the full test suite with coverage.
- `make lint` static analysis; `make fmt` auto-format code.
If no Makefile, use the nearest equivalents (Node: `npm ci && npm run build|test|lint`; Python: `pip install -r requirements.txt && pytest -q`).

## Coding Style & Naming Conventions
- Indentation: 2 spaces; max line length: 100; no trailing whitespace.
- Naming: classes `PascalCase`; functions/vars `camelCase` (or `snake_case` in Python); files by language norms (e.g., Python `snake_case.py`, JS/TS `kebab-case.ts`).
- Keep modules single-responsibility; avoid cross-feature imports except via public interfaces.
- Use the provided formatters/linters via `make fmt` and `make lint`; do not commit unrelated reformatting.

## Testing Guidelines
- Place tests under `tests/`, mirroring `src/` structure.
- Naming: Python `test_*.py`; JS/TS `*.spec.(js|ts)`.
- Aim for ≥85% coverage; new/changed code must include tests.
- Run locally with `make test` (or `pytest -q` / `npm test`).

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, optional scopes (e.g., `feat(auth): ...`).
- Commits are small and atomic; body explains the why, not just the what.
- PRs include: clear description, linked issues, tests, and screenshots for UI changes. Ensure CI green and `make lint`/`make fmt` are clean.

## Security & Configuration
- Never commit secrets; keep `.env` local and provide `.env.example` for defaults.
- Sanitize logs and test data; avoid PII in fixtures.

## Agent-Specific Instructions
- This file’s scope is the repository root and all subdirectories.
- Prefer minimal diffs; match existing patterns; do not reformat unrelated files.
- Use fast search (`rg`) and read files in ≤250-line chunks when inspecting.
