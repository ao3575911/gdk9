# GDk9 ↔ egglog bridge spike

**Verdict: YES** — GDk9 digital-root (DR) rewrite rules can ride egglog via `egglog-python` (`pip`/`uv` package name: **`egglog`**).

## Goal

Prove yes/no: can GDk9 rules ride egglog via egglog-python?

## Layout (in-repo)

| Path | Role |
|------|------|
| `gdk9/egglog_bridge/dr_egglog.py` | ONE DR rewrite suite encoded in egglog |
| `gdk9/egglog_bridge/fallback.py` | **Old rewriter kept** — wraps `gdk9.energy.digital_root` |
| `gdk9/saturate.py` | CLI entry (`python -m gdk9.saturate` / `gdk9-saturate`) |

## Dependency

```bash
pip install 'gdk9-cli[egglog]'
# or: uv pip install egglog   # egglog>=13.0.0
```

Requires Python ≥ 3.11 for the egglog path (fallback works on older Pythons).

## DR rewrite suite (egglog)

Two-phase saturation (required — folding DR-equivalent integers while still adding diverges):

1. **Sum fold:** `Energy(a) + Energy(b) → Energy(a + b)`
2. **DR collapse (subsume):**
   - `Energy(a) | a>0 ∧ a%9==0 → Energy.root(9)`
   - `Energy(a) | a>0 ∧ a%9≠0 → Energy.root(a%9)`
   - `Energy(0) → Energy.root(9)`  (`zero_to_nine`, matches gdk9)

## How to run

```bash
# with egglog installed
python -m gdk9.saturate
# or
gdk9-saturate

# custom fixture
python -m gdk9.saturate --values 26,10,9

# old rewriter only
python -m gdk9.saturate --fallback-only
```

## What passed

Default fixture `[26, 10, 9]`:

- egglog before: `Energy(26) + Energy(10) + Energy(9)`
- egglog after sum: `Energy(45)`
- egglog collapsed/best: **`Energy.root(9)`**
- fallback: total=45, folded_terms=`[8,1,9]`, best_dr=`9`, congruence_dr=`9`
- egglog best_dr == fallback best_dr == **9**

Example stdout:

```
=== GDk9 egglog bridge spike: saturate ===
fixture: [26, 10, 9]
[egglog] before:    Energy(26) + Energy(10) + Energy(9)
[egglog] after_sum: Energy(45)
[egglog] after_dr:  Energy.root(9)
[egglog] best_dr:   9
[fallback] total=45 folded=[8, 1, 9] best_dr=9 congruence_dr=9
VERDICT: YES
collapsed/best form: Energy.root(9)
```

## Verdict

**YES**

GDk9 DR rules can be encoded and saturated via egglog-python; result matches the legacy `gdk9.energy.digital_root` rewriter.

## Blockers / notes

- Do **not** combine unbounded `+` congruence over raw integers with DR-equivalence in one open-ended ruleset — that explodes the e-graph. Two-phase (sum then subsuming DR fold) is the workable pattern.
- Comm/assoc over `Energy` vars also blows up; omitted for the spike.
- Old rewriter intentionally retained in `gdk9.egglog_bridge.fallback` / `--fallback-only`.
