# GDk9 Architecture

## Overview

GDk9 is structured as a layered Python package. The CLI (`gdk9`) is the user-facing surface; below it sits a set of functional modules; at the core is the pure implication kernel with no I/O or filesystem dependencies.

---

## Layer Diagram

```
┌─────────────────────────────────────────────────────┐
│  CLI  (gdk9/cli.py)                                 │
│  argparse entry point — routes all subcommands      │
├──────────────┬────────────────────────────────────  │
│  TUI         │  REPL (sh)                           │
│  (tui.py)    │  (inline in cli.py)                  │
├──────────────┴────────────────────────────────────  │
│  High-Level Modules                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ energy   │ │ optimize │ │  dcg     │            │
│  │ analyze  │ │ attune   │ │  paths   │            │
│  └──────────┘ └──────────┘ └──────────┘            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ tokenize │ │  imply   │ │  crypto  │            │
│  └──────────┘ └──────────┘ └──────────┘            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ plugins  │ │  state   │ │   subs   │            │
│  │ loader   │ │  crdt    │ │          │            │
│  └──────────┘ └──────────┘ └──────────┘            │
├────────────────────────────────────────────────────  │
│  Foundation Modules                                  │
│  principles.py  ·  parser.py  ·  errors.py          │
│  io_utils.py  ·  fmt.py  ·  ansi.py  ·  log.py     │
├────────────────────────────────────────────────────  │
│  Kernel  (gdk9/kernel/)  — pure, no I/O             │
│  engine · expression · rule · symbol · proof        │
└─────────────────────────────────────────────────────┘
```

---

## Module Responsibilities

### CLI (`cli.py`)
Single entry point. Parses args, loads principle, auto-boots plugins, dispatches to `cmd_*` functions. Contains no business logic.

### Energy (`energy.py`)
- `char_energy(ch, principle)` — digital-root energy for a single character.
- `string_energy(text, principle)` → `(total, dr)` — aggregate.
- `analyze_text(text, principle)` → structured units (document/paragraphs/sentences/words).
- `vector_energy`, `harmonic_triads` — extended analysis mode.

### Principles (`principles.py`, `parser.py`)
- `Principle` dataclass: letter_mode, number_mode, weights, symbol_energy.
- `load_principle(path)` — from JSON/YAML file or bundled Ninefold Grid default.

### DCG (`dcg.py`)
- `DCG` class: 52-node graph (A–Z, a–z).
- Edge types: DC↔AC (cost 1/2), within-class all-pairs (cost 1), cross-class cycle (cost 2).
- `shortest_path` via Dijkstra; `word_path_info` for per-step edge validity.
- `symmetry_class`, `sym_energy`, `vectorize` — per-character functions.
- `homotopy_equivalent` — energy + vector-distance check within tolerance.

### Tokenize (`tokenize.py`)
- Splits text on characters with a target energy value or explicit delimiter set.
- Supports keep/drop delimiters, strip whitespace, annotate mode.
- `to_json_payload` — rich JSON with metrics, histograms, top tokens.

### Optimize (`optimize.py`)
- `optimize_attunement` — append/prepend/intersperse planning (minimal symbol steps).
- `optimize_substitution` / `apply_edit_plan` — character-level edit planning.
- `Plan` and `EditPlan` dataclasses carry before/after energy and step list.

### Imply (`imply.py`)
- `Rule` dataclass: name, type (fusion/split), arity, params.
- `make_fusion`, `make_split` — validated constructors.
- `apply_rule` — energy-conserving rule application over named symbols.

### State (`state.py`, `crdt.py`)
- JSON state file: `{"symbols": {...}, "rules": {...}}`.
- Each entry wrapped in an LWW-CRDT record with a timestamp.
- `merge_state(base, incoming)` — deterministic last-write-wins merge.

### Plugins (`plugins/loader.py`, `plugins/registry.py`)
- Discovers packs in `./plugins/` and `~/.gdk9/plugins/`.
- Parses JSON, YAML (PyYAML optional), or Python (AST literal_eval only — never exec).
- `auto_boot` — loads enabled plugins from `~/.gdk9/plugins.json` at CLI startup.
- `apply_plugin` — merges symbol_energy into active principle; seeds symbols/rules into state.

### Crypto (`crypto.py`)
- EDPC: playful non-crypto transform — rotates via `char_energy` keystream (not XOR, not DCG).
- Secure: Fernet (`cryptography`) with PBKDF2-HMAC-SHA256 key derivation; payload `G9F` + salt + Fernet token (urlsafe-b64).

### Kernel (`kernel/`)
Pure implication kernel — no CLI, no state files, no plugins, no TUI, no crypto.
- `engine.py` — evaluation, rule application, bounded search.
- `expression.py` — ordered symbolic expression.
- `rule.py` — pure rule metadata and transform.
- `symbol.py` — named unit with evaluated energy.
- `proof.py` — traceable judgment steps.
- `principle.py` — immutable valuation context wrapping existing principle data.

**Kernel boundary:** May import `gdk9.energy` and `gdk9.principles`. Must not import any other `gdk9.*` module.

---

## Data Flow: `gdk9 an "Hello"`

```
argv
  → cli.main()
      → load_principle(None)           # loads ninefold.json
      → plugins_auto_boot(principle, state)
      → cmd_analyze(args, principle, use_color)
          → read_input(args.text, None)   # returns "Hello"
          → analyze_text("Hello", principle)
              → tokenize_sentences / tokenize_words
              → char_energy per character
              → digital_root aggregation
              → returns {document, paragraphs, sentences, words}
          → Box / fmt_dr rendering
          → print to stdout
```

---

## Data Flow: Plugin Load

```
gdk9 pl load ./plugins/pack.yaml
  → plugins_find("./plugins/pack.yaml")
  → plugins_load(path)
      → parse YAML/JSON or AST literal_eval for .py
      → validate schema (name, version, rules, checks)
      → run conservation checks
      → returns PluginPack
  → plugins_apply(pack, principle, state)
      → merge pack.symbol_energy into principle.symbol_energy
      → seed pack.symbols into state
      → add pack.rules into state.rules
  → save_state(state, path)
  → plugins_enable(pack.name, path)   # writes ~/.gdk9/plugins.json
```

---

## Testing Layout

```
tests/
├── conftest.py              — shared fixtures (principle, state)
├── test_energy.py           — char_energy, string_energy, digital_root
├── test_tokenize.py         — tokenizer correctness
├── test_tokenize_metrics.py — JSON metrics payload
├── test_dcg.py              — DCG classify, path, shortest, homotopy
├── test_optimize.py         — attunement planning
├── test_rules.py            — fusion/split rule definitions
├── test_rules_commit.py     — rule apply + commit to state
├── test_rules_reversibility.py — round-trip energy conservation
├── test_state_crdt.py       — CRDT merge semantics
├── test_crypto.py           — EDPC encrypt/decrypt round-trips
├── test_plugins.py          — plugin load/validate/apply
└── kernel/                  — kernel unit tests
```

Run: `make test` or `python -m pytest -q`.

---

## Extension Points

| What to extend | Where |
|----------------|-------|
| New CLI command | Add subparser in `build_parser()` + `cmd_*` function in `cli.py` |
| New energy mode | `principles.py` + `energy.py` `char_energy()` dispatch |
| New DCG edge type | `dcg.py` `_build_graph()` |
| New rule type | `imply.py` `apply_rule()` dispatch |
| Plugin-distributed rules | Author a JSON/YAML pack, add `checks` |
| Kernel theorem | `kernel/engine.py` `search()` |