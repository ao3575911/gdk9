# GDk9 Python API

GDk9 can be used as an embedded Python library without the CLI. The public API surface is stable within a minor version.

---

## Installation

```bash
pip install -e .
```

or as a dependency:
```toml
# pyproject.toml
[project]
dependencies = ["gdk9-cli>=0.3.0"]
```

---

## Core Energy API

```python
from gdk9.principles import load_principle
from gdk9.energy import (
    char_energy,
    string_energy,
    digital_root,
    analyze_text,
    energy_profile,
    vector_energy,
    harmonic_triads,
)

principle = load_principle()          # Ninefold Grid default
# principle = load_principle("my.json")  # custom file

# Single character
e = char_energy("A", principle)       # → 1 (A=1, DR=1)
e = char_energy("!", principle)       # → 3 (symbol_energy["!"])

# String aggregate
total, dr = string_energy("Hello", principle)   # → (20, 2)

# Digital root directly
dr = digital_root(38)    # → 2   (3+8=11→2)
dr = digital_root(0)     # → 9   (normalised)

# Structured analysis
result = analyze_text("Hello world.", principle)
# result: dict with keys "document", "paragraphs", "sentences", "words"
# each value: list of UnitEnergy(unit, value, energy, total)

for word in result["words"]:
    print(word.value, word.energy, word.total)

# Energy profile histogram
prof = energy_profile("Hello world", principle)
# → {"1": 0, "2": 1, "3": 0, ..., "9": 0}

# Extended: 4D vector and harmonic triads
vec  = vector_energy("Hello", principle)
# → {"sum": {"letters": 20, "digits": 0, "symbols": 0},
#    "dr":  {"letters": 2, ...}}

harm = harmonic_triads("Hello world", principle)
# → {"root": 3, "wave": 4, "peak": 2}
```

---

## Principle API

```python
from gdk9.principles import Principle, load_principle

p = load_principle()                  # default Ninefold Grid
p = load_principle("custom.json")    # from file

# Principle fields (read-only dataclass)
p.name             # str
p.description      # str | None
p.letter_mode      # "a1z26" | "unicode"
p.number_mode      # "digital_root" | "raw"
p.normalize_zero_to_nine  # bool
p.weights          # {"letter": int, "digit": int, "symbol": int}
p.symbol_energy    # dict[str, int]
```

---

## DCG API

```python
from gdk9.dcg import (
    get_dcg,
    symmetry_class,
    sym_energy,
    vectorize,
    word_sym_energy,
    word_vector,
    homotopy_equivalent,
)

g = get_dcg()    # singleton DCG instance (52 nodes)

# Per-character
sc  = symmetry_class("F")      # → "asymmetric"
e   = sym_energy("F")          # → 7.0  (pos+1)
vec = vectorize("F")           # → [6.0, 4, 2.6457..., 0.6...]

# Per-word
we  = word_sym_energy("FWEM")  # → sum of sym_energy per letter
wv  = word_vector("FWEM")      # → 4D vector sum

# Path info
info = g.word_path_info("FWEM")
# → {"steps": [...], "is_valid_path": bool, "total_energy": float, "vector_sum": [...]}

# Shortest path
path = g.shortest_path("F", "M")  # → ["F", "f", "b", "m", "M"] or None
cost = g.shortest_path_cost("F", "M")  # → float

# Homotopy
equiv, detail = homotopy_equivalent("FWEM", "FeWM", tol=1.0)
# equiv: bool
# detail: {"word_a": {...}, "word_b": {...}, "energy_diff": float, "vector_distance": float, "equivalent": bool}
```

---

## Tokenizer API

```python
from gdk9.tokenize import (
    tokenize_by_energy,
    tokens_with_energy,
    to_json_payload,
    annotate_text,
    delimiter_set,
)

# Get delimiter characters for a given energy level
delims = delimiter_set(principle, energy=1)  # → {".","<",">","|"}

# Tokenize
from gdk9.tokenize import tokenize_by_energy
tokens = tokenize_by_energy(
    "Hello. World!",
    principle,
    energy=1,
    keep_delims=True,
    strip_tokens=True,
)
# → list of str

# Full JSON payload (matches `gdk9 tok -F json`)
payload_str = to_json_payload("Hello. World", principle, energy=1)
import json
data = json.loads(payload_str)

# Annotate inline
annotated = annotate_text("Hi", principle)
# → "H[8]i[9]"
```

---

## Optimization / Attunement API

```python
from gdk9.optimize import optimize_attunement, apply_plan, optimize_substitution, apply_edit_plan

# Plan: compute minimum symbol insertions
plan = optimize_attunement(
    "Hello",
    target=7,
    principle=principle,
    allowed_symbols=".!?",
    method="append",
    max_steps=64,
)
# plan.steps   → [(".", 2)]
# plan.method  → "append"
# plan.target  → 7
# plan.total_before, plan.dr_before
# plan.total_after,  plan.dr_after

result_text = apply_plan("Hello", plan, spread=None)

# Edit plan (substitute / character-level edits)
eplan = optimize_substitution(
    "Hello",
    target=5,
    principle=principle,
    subs={"l": ["1"], "o": ["0"]},
    allow_delete=False,
    max_edits=64,
)
result_text = apply_edit_plan("Hello", eplan)
```

---

## Implication Rules API

```python
from gdk9.imply import make_fusion, make_split, apply_rule, Rule

# Define rules
fusion = make_fusion("JOIN", out_name="AUTO", arity=2)
split  = make_split("HALVE", out_a="L", out_b="R", ratio=0.5)

# Apply rules to a symbols dict
symbols = {"X": 10.0, "Y": 6.0}
result = apply_rule(fusion, symbols, inputs=["X", "Y"], tol=1e-9)
# → {"ok": True, "outputs": [{"name": "XY", "energy": 16.0}], ...}

result = apply_rule(split, {"X": 10.0}, inputs=["X"], tol=1e-9)
# → {"ok": True, "outputs": [{"name": "L", "energy": 5.0}, {"name": "R", "energy": 5.0}], ...}
```

---

## State / CRDT API

```python
from gdk9.state import load_state, save_state, set_symbol, set_rule, list_symbols, merge_state

state = load_state()                  # default ~/.gdk9/state.json
state = load_state("my_state.json")

set_symbol(state, "ALPHA", 5.0)
save_state(state, "my_state.json")

syms = list_symbols(state)  # → {"ALPHA": 5.0, ...}

# CRDT merge
merged, stats = merge_state(base_state, incoming_state)
# stats: {"symbols_merged": int, "rules_merged": int, "conflicts_resolved": int}
```

---

## Utilization API

```python
from gdk9.utilization import attune, sigil

# Legacy single-symbol attune
new_text, total, dr, count = attune("Hello", target=7, principle=principle, symbol=".")

# Sigil visual (grid or bar)
vis = sigil("Hello", principle, style="grid")
print(vis)
```

---

## Kernel API (pure, no I/O)

The kernel is in-memory only. Adapters (`gdk9.kernel_cli`, `gdk9 kernel …`) may
wrap it; `gdk9.kernel.*` itself must not import CLI, state, plugins, crypto, TUI,
or terminal formatting helpers.

```python
from gdk9.kernel import (
  Expression,
  ImplicationEngine,
  ImplicationRule,
  Judgment,
  KernelPrinciple,
  ProofStep,
  RuleKind,
  Symbol,
)
from gdk9.kernel.engine import fusion_rule, split_rule

kp = KernelPrinciple.default()          # or adapt a Principle via kernel_cli
expr = Expression.from_text("AB", kp)   # or Expression.from_names(["A", "B"], kp)
engine = ImplicationEngine(kp, (fusion_rule(),))

total, root = engine.evaluate(expr)     # → (3.0, 3)
judgment = engine.apply("fuse", expr)   # Judgment with conservation check
path = engine.infer(expr, Expression((Symbol("AB", total),)), max_depth=2)
```

### CLI smoke path (adapter)

```bash
gdk9 kernel eval ABC
gdk9 kernel apply fuse A B
gdk9 kernel apply split AB --parts A,B --energies 1,2
gdk9 kernel search A B --target AB --max-depth 2 --rules fuse
```

JSON output is emitted by `gdk9.kernel_cli` (outside `gdk9.kernel`). See
`docs/KERNEL.md` and `examples/08_kernel.py`.

---

## Error Types

```python
from gdk9.errors import Gdk9Error, InputError, ConfigError, OptimizationError

try:
    plan = optimize_attunement(...)
except OptimizationError as e:
    print(e)  # user-readable message
```

| Exception | Raised when |
|-----------|-------------|
| `InputError` | Bad user input (empty text, invalid flag value) |
| `ConfigError` | Malformed principle or state file |
| `OptimizationError` | Attunement target unreachable within max_steps |
| `Gdk9Error` | Base class for all GDk9 exceptions |
