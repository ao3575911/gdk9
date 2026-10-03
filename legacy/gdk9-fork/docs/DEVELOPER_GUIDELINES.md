# Developer Guidelines

These guidelines capture principles for extending Gdk9 while preserving core guarantees.

## 7. Transformation Rules
- Conservation: All transformations must obey symbolic-energy conservation. Inputs and outputs must match within tolerance; enforce in rule applicators and tests.
- Energy registry: Avoid ad hoc symbol energy assignments. Use the energy registry derived from the active principle (see `gdk9/parser.py` and `gdk9/principles.py`).
- Extension surface: Extend via modules and registries, not direct kernel edits. A plugin system is planned; see `gdk9/plugins/` stubs for the interface.
- New implication rules must include:
  - Definition: Name, type, arity, parameters.
  - Energy mapping: How input energies map to outputs (with tolerance).
  - Reversibility test: Demonstrate a reverse mapping or round-trip where applicable (e.g., fuse→split with computed ratio).
  - Tests: Place unit tests under `tests/` to verify behavior and conservation.

## 8. Planned Features

| Feature | Description |
| --- | --- |
| Plugin Registry | Load user-defined symbolic grammars dynamically (implemented: see `gdk9/plugins/loader.py`, `gdk9 plugin ...`) |
| Distributed Sync | Peer-to-peer ledger consistency layer |
| Graph Renderer | Visualize implication networks |
| Telegram Layer | Connect GDk9 logic to gamified systems (WordFarm, BattleBot) |
| API Wrapper | REST interface for GDk9 kernel functions |

Notes:
- Plugin registry is scaffolded in `gdk9/plugins/registry.py` for experimentation. Backward-compatible integration into CLI will come later.
- Keep changes minimal and focused; match existing patterns and coding style.
