# GDk9 Documentation Index

> **GDk9 v0.3.0** — Symbolic Energy Platform | License: AGPL-3.0-or-later

---

## Documentation Tree

```
docs/
├── index.md               ← You are here — navigation hub
├── QUICKSTART.md          ← Install and first analysis in 5 minutes
├── CHEATSHEET.md          ← All commands, flags, formulas, and tables
├── HANDBOOK.md            ← Full bilingual reference (EN + RU)
├── CLI.md                 ← Detailed CLI command reference
├── GDK9_CORE.md           ← Core concepts: digital root, harmonic triads, sigils
├── KERNEL.md              ← Symbolic implication kernel architecture
├── PLUGINS.md             ← Plugin system: schema, loading, authoring
├── ARCHITECTURE.md        ← Module map, data flow, kernel boundary
├── CONFIGURATION.md       ← Principle files, state, env vars, auto-boot
├── API.md                 ← Public Python API for library embedding
├── SECURITY.md            ← Threat model, crypto guidance, secret handling
├── RELEASE.md             ← sdist/wheel build path and TestPyPI steps
├── PROVE.md               ← CI-on-main prove gate for research changes
├── DEVELOPER_GUIDELINES.md← Contribution standards and extension rules
├── DCG_CONTRACT.md        ← DCG/SymPhi letter-class / energy / 4D vector golden contract
└── KEYSUITE_BRIDGE.md     ← KeySuite conformance ↔ gdk9.kernel inventory
```

---

## Quick Navigation

| I want to…                              | Go to                          |
| --------------------------------------- | ------------------------------ |
| Install and run my first command        | [QUICKSTART.md](QUICKSTART.md) |
| Look up a flag or command quickly       | [CHEATSHEET.md](CHEATSHEET.md) |
| Understand digital root and energy      | [GDK9_CORE.md](GDK9_CORE.md)  |
| Configure a custom principle            | [CONFIGURATION.md](CONFIGURATION.md) |
| Write or load a plugin                  | [PLUGINS.md](PLUGINS.md)       |
| Use GDk9 as a Python library            | [API.md](API.md)               |
| Understand the implication kernel       | [KERNEL.md](KERNEL.md)         |
| Contribute or extend the codebase       | [DEVELOPER_GUIDELINES.md](DEVELOPER_GUIDELINES.md) |
| Pin DCG letter-class / energy / vector  | [DCG_CONTRACT.md](DCG_CONTRACT.md) |
| Review security considerations          | [SECURITY.md](SECURITY.md)     |
| Build sdist/wheel or upload to TestPyPI  | [RELEASE.md](RELEASE.md)       |
| Prove a change (CI on main)               | [PROVE.md](PROVE.md)           |
| Kernel search walkthrough                 | [HANDBOOK.md](HANDBOOK.md) §8  |

---

## Project Layout

```
gdk9/                      ← Python package root
├── __init__.py            ← version string
├── cli.py                 ← argparse entry point (gdk9 command)
├── energy.py              ← char_energy, string_energy, digital_root
├── principles.py          ← Principle dataclass and loader
├── dcg.py                 ← Directed Cognition Graph (classify, path, vector…)
├── tokenize.py            ← Tokenizer with energy-delimiter support
├── optimize.py            ← Attunement planning (append/edit/substitute)
├── imply.py               ← Rule definitions: fusion, split, apply
├── state.py               ← CRDT-aware state (symbols + rules)
├── crdt.py                ← Last-write-wins CRDT primitives
├── crypto.py              ← EDPC cipher and optional secure mode
├── tui.py                 ← Curses-based live analysis UI
├── subs.py                ← Substitution profile generator
├── ansi.py                ← Terminal color helpers
├── fmt.py                 ← Table/box rendering
├── log.py                 ← Debug logger
├── errors.py              ← Gdk9Error hierarchy
├── io_utils.py            ← stdin/file input unifier
├── utilization.py         ← attune(), sigil()
├── parser.py              ← Principle file parser
├── kernel/                ← Pure implication kernel (no I/O side effects)
│   ├── engine.py
│   ├── expression.py
│   ├── principle.py
│   ├── proof.py
│   ├── rule.py
│   └── symbol.py
├── plugins/               ← Plugin loader and registry
│   ├── loader.py
│   └── registry.py
└── data/                  ← Bundled data files
    ├── ninefold.json      ← Default principle
    ├── official.json      ← Active official principle (can be installed)
    └── subs.json          ← Default substitution profiles

scripts/                   ← Utility scripts
├── make_zip.py            ← Package project into dist/gdk9-project.zip
├── batch_analyze.py       ← Bulk analyze a directory of text files
├── export_json.py         ← Full JSON export for a single input
├── watch_file.py          ← Live re-analyze on file change
└── profile_compare.py     ← Side-by-side energy histogram diff

plugins/                   ← Distributable plugin packs (YAML/JSON)
├── example.yaml           ← Minimal example pack (HALVE split + JOIN fusion)
├── balanced_splits.json   ← Common balanced split rules
├── triad_fusions.json     ← Triad composition fusions
├── harmonic_suite.json    ← Root/Wave/Peak triad rules + verse punctuation
├── crypto_keys.json       ← Z-flip and asymmetric-class key-derivation rules
├── language_metrics.json  ← Sentence aggregation rules for NLP workflows
└── ninefold_extended.json ← Extended Ninefold Grid with Unicode symbols

tests/                     ← pytest suite
examples/                  ← Runnable example scripts (01_analyze.py … 07_api.py)
pairs.csv                  ← Character pair table (visual, DC/AC, energy, symbol)
```

---

## Core Concepts at a Glance

| Concept         | One-liner |
| --------------- | --------- |
| Digital Root    | Sum of digits reduced to 1–9; `0` normalises to `9`. |
| Energy          | `char_energy(ch)` via A1Z26 + digital root (default). |
| Principle       | JSON/YAML config: letter mode, weights, symbol_energy. |
| Conservation    | Rule inputs and outputs must have equal total energy (±tolerance). |
| Symmetry Class  | Idempotent / Biphasic / Involutive / Asymmetric — determines DCG edges. |
| DCG             | Directed Cognition Graph: 52-node graph over A–Z, a–z. |
| Attunement      | Modifying text to reach a target digital-root energy. |
| Plugin          | JSON/YAML/Python pack of rules, symbol overrides, and checks. |
| CRDT State      | Last-write-wins mergeable state file for symbols and rules. |