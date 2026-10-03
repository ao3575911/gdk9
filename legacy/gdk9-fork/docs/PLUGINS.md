# Gdk9 Plugins

Plugins extend GDk9 with rule packs and optional symbol energy/seed symbols.

- Locations: `./plugins/` (project-local) and `~/.gdk9/plugins/` (user).
- Formats: JSON/YAML, or Python with a top-level `PLUGIN = {...}` literal. Python packs are parsed via AST and not executed.
- Auto-boot: Enabled plugins listed in `~/.gdk9/plugins.json` are loaded on every CLI run.

## Schema (JSON/YAML)
```
{
  "name": "my_pack",
  "version": "0.1",
  "description": "Short summary",
  "symbol_energy": {"~": 9},              // optional: merges into current principle
  "symbols": {"X": 10.0},                  // optional: seeds named symbols in state
  "rules": [                                // optional: rule pack
    {"type": "split", "name": "HALVE", "out_a": "L", "out_b": "R", "ratio": 0.5},
    {"type": "fusion", "name": "JOIN", "out": "AUTO", "arity": 2}
  ],
  "checks": [                               // optional: conservation checks at load
    {"rule": "HALVE", "inputs": [{"name": "X", "energy": 10.0}]}
  ]
}
```

- Rules are validated on load; splits enforce 0..1 ratio, fusions enforce arity ≥ 2.
- Checks are executed in a fail-fast sandbox by applying rules to provided inputs and verifying energy conservation.

## CLI
- `gdk9 plugin list` — discover plugins
- `gdk9 plugin validate <NAME|PATH>` — validate pack without applying
- `gdk9 plugin info <NAME|PATH>` — show metadata
- `gdk9 plugin load <NAME|PATH>` — apply to state and enable for auto-boot
- `gdk9 plugin enable/disable` — toggle auto-boot

## Safety
- YAML is parsed with `json` first, then `PyYAML` when available. Prefer JSON-compatible YAML for portability.
- Python packs are parsed via AST `literal_eval` of the `PLUGIN` assignment; no code is executed.

## Notes
- Energy conservation is guaranteed at runtime by the core rule engine and additionally checked using plugin-provided inputs.
- To distribute a pack as a directory: `my_pack/plugin.json` (or `.yaml`/`.py`) and optional `checks.json`.

