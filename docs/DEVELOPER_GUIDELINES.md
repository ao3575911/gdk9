# Developer Guidelines

These guidelines capture principles for extending Gdk9 while preserving core guarantees.

## 7. Transformation Rules
- Conservation: All transformations must obey symbolic-energy conservation. Inputs and outputs must match within tolerance; enforce in rule applicators and tests.
- Energy registry: Avoid ad hoc symbol energy assignments. Use the energy registry derived from the active principle (see `gdk9/parser.py` and `gdk9/principles.py`).
- Extension surface: Extend via modules and registries, not direct kernel edits. Plugins are first-class — use `gdk9/plugins/` and `gdk9 plugin` / `gdk9 pl …`.
- New implication rules must include:
  - Definition: Name, type, arity, parameters.
  - Energy mapping: How input energies map to outputs (with tolerance).
  - Reversibility test: Demonstrate a reverse mapping or round-trip where applicable (e.g., fuse→split with computed ratio).
  - Tests: Place unit tests under `tests/` to verify behavior and conservation.

## 8. Feature status

| Feature | Status |
| --- | --- |
| Plugin Registry | **Implemented** — `gdk9/plugins/loader.py`, `gdk9/plugins/registry.py`, CLI: `gdk9 plugin` / `gdk9 pl …` |

Not scheduled: distributed sync, graph renderer, Telegram/WordFarm/BattleBot layers, REST API wrapper. Do not treat those as roadmap commitments.

Notes:
- Keep changes minimal and focused; match existing patterns and coding style.

## Prove gate

Green CI on `main` is required before treating a research change as done.
See `docs/PROVE.md`. Prefer critical ruff + pytest locally before opening a PR.
