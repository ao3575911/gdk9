# Experiment: Conserved search vs naive name-join

**Status:** research move 3 (Approach A)  
**Claim (bounded):** GDk9’s implication kernel **beats naive join on proof validity under conservation** — not speed, not SOTA, not a new energy law.

## Public / baseline system

**Naive name-concatenation “implication.”** Treat fuse as string-join of adjacent symbol names. Search is a bounded BFS over name sequences only. Accept any path that reaches the target **name sequence**. Ignore energy conservation entirely.

This is a deliberately weak public baseline: it can “prove” joins that look right as strings while saying nothing about whether energy is conserved.

## GDk9 system under test

- `gdk9.kernel.ImplicationEngine.infer` — bounded BFS over registered rules
- Live fuse/split helpers: `gdk9.kernel.engine.fusion_rule` / `split_rule`
- Existing maths only (`KernelPrinciple.default()`, fuse total energy, judgment `conserved` / `delta`)
- A path counts as a **valid conserved proof of the target** only if:
  1. `infer` returns steps within `max_depth`, and
  2. every judgment has `conserved is True` and `|delta| ≤ 1e-9`, and
  3. the final expression energy matches the target energy within `1e-9`

Criterion (3) is the soundness bridge: name reachability under conserving rules is not enough to claim the *declared* target when that target’s energy disagrees with conservation.

## Where GDk9 could beat the baseline

On tasks where a conserved fuse/split path exists:

| Dimension | Naive join | GDk9 kernel |
| --------- | ---------- | ----------- |
| Finds `A,B → AB` (matching energy) within depth 2 | yes (names) | yes (names + conserved steps) |
| Accepts `AB` with **wrong** declared energy as “found” | yes | **no** (returns no valid proof) |
| Returns a step with `conserved is False` | N/A (no energy) | must not |

The beat is **validity**, not throughput: the naive joiner cannot distinguish conserved from non-conserved targets; the kernel can.

## Hypothesis

On tasks where a conserved fuse/split path exists, the kernel finds it within a small depth bound **and** every returned step has `delta ≈ 0`. The naive joiner either (1) accepts energy-breaking “proofs” the kernel rejects, or (2) cannot distinguish conserved from non-conserved targets.

## Fail criteria (pytest must fail if broken)

1. Kernel returns a path where any judgment has `conserved is False` or `|delta| > 1e-9`.
2. Kernel cannot find `A,B → AB` with fuse within `max_depth=2` under the default principle (matching target energy).
3. Naive baseline accepts at least one documented energy-mismatched target as “found” while the kernel correctly returns no valid conserved proof (`None`).

## Method

1. Build source `Expression.from_names(["A", "B"], principle)` and a conserved target `AB` with `energy = source.total_energy()`.
2. Run `ImplicationEngine(principle, (fusion_rule(),)).infer(..., max_depth=2)` and assert conservation on every step.
3. Run the naive adjacent-join BFS on names only for the same name sequences.
4. Repeat with a documented mismatched target `Symbol("AB", 99.0)`: naive must report found; kernel conserved-proof helper must return `None`.

Executable specification: `tests/experiment/test_conserve_vs_naive.py` (pytest **is** the experiment). Optional runner: `examples/10_conserve_vs_naive.py`.

## How to run

```bash
pip install -e ".[dev]"
python -m pytest -q tests/experiment/test_conserve_vs_naive.py
# or full suite:
python -m pytest -q
# optional JSON summary:
python examples/10_conserve_vs_naive.py
```

Critical lint (unchanged prove gate): `ruff check gdk9 --select E9,F63,F7,F82`.

## Competing approaches considered

| ID | Approach | Decision |
| -- | -------- | -------- |
| **A** | Conserved search vs naive join | **Chosen** — smallest, uses live kernel, clear fail bar |
| B | DCG vectors vs bag-of-codepoints | Deferred — mixes SymPhi with DR kernel; easy false SOTA |
| C | EDPC vs Fernet | Deferred — security theatre, not research implication |

## Non-claims

- No SOTA claim.
- No new energy laws; fuse/split use existing kernel maths only.
- No claim that the kernel is faster than naive join.
- Success language: **beats naive join on proof validity under conservation.**