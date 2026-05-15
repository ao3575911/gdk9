# SymPhi-Engine

Physics-aware symbolic implication kernel. Applies conserved-energy grammar to the GDk9 alphabet — classifying letters by symmetry type, computing energy invariants, and transforming words through morphisms that preserve the fundamental conservation law: **ΣE(before) = ΣE(after)**.

```bash
python main.py FWEM
# Energy: 42.04
# Classes: ['asymmetric', 'idempotent', 'biphasic', 'idempotent']
# Vector: [63. 60. 41. -0.95]
# Conserved: True
```

## Concepts

**Symmetry types** — every letter is one of four classes:

| Type | Letters | Equation | Role |
|------|---------|----------|------|
| Idempotent | A H I M O T U V W X Y / a m o t u v w x y | x² = x | Stabiliser — preserves identity |
| Biphasic | B C D E K / b c d e k | x² = f(x) | Oscillator — dual-phase modulation |
| Involutive | N S Z / n s z | x² = 1 | Flipper — reversible inversion |
| Asymmetric | F G J L P Q R / f g j l p q r | x² ≠ x, 1 | Driver — directional flow |

**Energy** — each letter contributes `pos × type_factor` where `type_factor` varies by symmetry class. Words are stable when total energy is positive, finite, and conserved across transforms.

**Vectorization** — each letter maps to a 4-D vector `[pos, type_id, √E, sin(θ)]`. Word vectors are the component-wise sum, enabling ML integration and homotopy analysis.

## Install

```bash
git clone https://github.com/ao3575911/SymPhi-Engine.git
cd SymPhi-Engine
pip install -e .
```

**Runtime requirements:** `numpy`. Optional heavy analysis (regression, pipeline): `sympy networkx matplotlib scikit-learn pandas`.

```bash
pip install numpy                          # core engine only
pip install -r requirements.txt            # full stack
```

Requires Python ≥ 3.10.

## Usage

### CLI
```bash
python main.py FWEM        # read a word through the implication engine
python main.py hello       # mixed-case works too
```

### Library
```python
from gdk9_core_engine import ImplicationEngine
from gdk9_framework import word_energy, get_symmetry_type, vectorize

engine = ImplicationEngine()

# Decode a word
result = engine.read("AVWM")
print(result["energy"])          # float
print(result["classes"])         # ['idempotent', 'involutive', 'idempotent', 'idempotent']
print(result["vector_sum"])      # numpy array

# Validate conservation
engine.validate_conservation("FWEM")   # True

# Transform
engine.transform("FWEM", morphism="flip")   # "MEWF"

# Lower-level
word_energy("GDK9")           # total energy float
get_symmetry_type("F")        # 'asymmetric'
vectorize("A")                # np.array([1, 0, 1.0, 0.841])
```

### Symbolic cipher
```python
from symbolic_cipher import encrypt, decrypt

ct = encrypt("hello", key="GDK9")
pt = decrypt(ct, key="GDK9")
```

## Module overview

| File | Purpose |
|------|---------|
| `gdk9_core_engine.py` | `ImplicationEngine` — read, validate, transform |
| `gdk9_framework.py` | Symmetry classification, energy, vectorisation |
| `gdk9_framework_extended.py` | Extended morphisms and homotopy utilities |
| `symbolic_cipher.py` | Energy-keyed symbolic cipher |
| `gdk9_pipeline.py` | Full analysis pipeline with metrics |
| `gdk9_pipeline_simple.py` | Lightweight pipeline variant |
| `gdk9_regression_engine.py` | Energy regression and prediction |
| `gdk9_regression_engine_v31.py` | v3.1 regression with expanded ruleset |
| `main.py` | CLI entry point |

## Development

```bash
pip install -e ".[dev]"
python -m py_compile gdk9_core_engine.py gdk9_framework.py symbolic_cipher.py
```

CI runs on Python 3.10, 3.11, 3.12 via GitHub Actions.

## License

MIT — © 2025 Adam Grange
