# DCG / alphabet golden contract

Pin the documented numeric contract for letter class, SymPhi rest-energy, and
4D vector from live `gdk9/dcg.py`. Sibling repos are literature only — this
fixture lives in gdk9 so they cannot drift the agenda.

Machine-readable values: [`tests/fixtures/dcg_golden.json`](../tests/fixtures/dcg_golden.json).
Checked by [`tests/test_dcg_golden.py`](../tests/test_dcg_golden.py) against the live public API.

## Source of truth

| Layer | Location |
|-------|----------|
| Implementation | `gdk9/dcg.py` (module docstring + public functions) |
| Public API | `docs/API.md` § DCG API |
| Class / energy table | `docs/CHEATSHEET.md` § DCG Symmetry Classes |
| Module map | `docs/ARCHITECTURE.md` § DCG |

No new energy laws. Classification, rest-energy, and the 4D vector are exactly
the existing functions: `symmetry_class`, `sym_energy`, `vectorize`,
`word_sym_energy`, `word_vector`.

## Energy model (from `gdk9/dcg.py`)

SymPhi rest-energy uses positional algebra (`pos` = A=1 … Z=26), not digital root.
Classification is determined by the uppercase form (`f` and `F` share a class).
Non-alphabetic characters: `sym_energy` → `0.0`, `vectorize` → `(0, 0, 0, 0)`,
and they are skipped by `word_sym_energy` / `word_vector`.

| Class | Letters (upper) | Base equation | SymPhi energy |
|-------|-----------------|---------------|---------------|
| Idempotent | A H I M O T U V W X Y | x² = x | E = pos |
| Biphasic | B C D E K | x² = f(x) | E = sin(pos) |
| Involutive | N S Z | x² = 1 | E = 1 / pos |
| Asymmetric | F G J L P Q R | x² ≠ x, 1 | E = pos + 1 |

`type_id` (vector component 1): idempotent=1, biphasic=2, involutive=3, asymmetric=4.

## 4D vector (from `gdk9/dcg.py` / cheatsheet)

```
v = [pos, type_id, √|E|, sin(pos · π / 26)]
```

`word_vector` is the component-wise sum of per-letter `vectorize` over alphabetic characters.

## Pinned words

Values below are the live API at the time the fixture was generated. The JSON
is the contract; this table is the human-readable summary.

| Word | Letters (alpha) | `word_sym_energy` | `word_vector` |
|------|-----------------|-------------------|---------------|
| `FWEM` | 4 | 42.04107572533686 | `[47.0, 8.0, 12.026380899298962, 2.585792292014487]` |
| `Hello` | 5 | 48.04107572533686 | `[52.0, 12.0, 14.891759811339249, 4.3474081782469725]` |
| `The quick brown fox jumps over the lazy dog` | 35 | 383.57937359787496 | `[473.0, 72.0, 102.5585905362783, 23.458080847556985]` |

`FWEM` matches the existing whitepaper / `tests/test_dcg.py` check
`E(FWEM) ≈ 42.04` (`places=1`).

Per-letter example (`FWEM`):

| Char | `symmetry_class` | `sym_energy` | `vectorize` |
|------|------------------|--------------|-------------|
| F | asymmetric | 7.0 | `[6.0, 4.0, 2.6457513110645907, 0.6631226582407952]` |
| W | idempotent | 23.0 | `[23.0, 1.0, 4.795831523312719, 0.35460488704253584]` |
| E | biphasic | −0.9589242746631385 | `[5.0, 2.0, 0.979246789457662, 0.5680647467311558]` |
| M | idempotent | 13.0 | `[13.0, 1.0, 3.605551275463989, 1.0]` |

## How to check

```bash
python -m pytest -q tests/test_dcg_golden.py
```

If `gdk9/dcg.py` changes class, energy, or vector formulae, this test fails
until the fixture (and this note) are updated on purpose.
