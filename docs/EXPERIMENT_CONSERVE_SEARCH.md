# Experiment: Conserved search vs naive name-join

**Status:** research move 5 (Approach A — fuse→split→fuse chain + same-names mismatch)  
**Claim (bounded):** GDk9’s implication kernel **beats naive join/split on proof validity under conservation** — not speed, not SOTA, not a new energy law.

## Public / baseline system

**Naive name-concatenation “implication.”** Treat fuse as string-join of adjacent symbol names and split as cutting one name into two contiguous substrings. Search is a bounded BFS over name sequences only. Accept any path that reaches the target **name sequence**. Ignore energy conservation entirely.

This is a deliberately weak public baseline: it can “prove” joins/splits that look right as strings while saying nothing about whether energy is conserved.

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

| Dimension | Naive join/split | GDk9 kernel |
| --------- | ---------------- | ----------- |
| Finds `A,B → AB` (matching energy) within depth 2 | yes (names) | yes (names + conserved steps) |
| Finds `AB → A,B` (matching energy) within depth 2 | yes (names) | yes (names + conserved steps) |
| Accepts `AB` / `A,B` with **wrong** declared energy as “found” | yes | **no** (returns no valid proof) |
| Returns a step with `conserved is False` | N/A (no energy) | must not |

The beat is **validity**, not throughput: the naive joiner/splitter cannot distinguish conserved from non-conserved targets; the kernel can.

## Hypothesis

On tasks where a conserved fuse/split path exists, the kernel finds it within a small depth bound **and** every returned step has `delta ≈ 0`. The naive joiner either (1) accepts energy-breaking “proofs” the kernel rejects, or (2) cannot distinguish conserved from non-conserved targets.

## Fail criteria (pytest must fail if broken)

1. Kernel returns a path where any judgment has `conserved is False` or `|delta| > 1e-9`.
2. Kernel cannot find `A,B → AB` with fuse within `max_depth=2` under the default principle (matching target energy).
3. Naive baseline accepts at least one documented energy-mismatched fuse target as “found” while the kernel correctly returns no valid conserved proof (`None`).
4. **Move 4:** Kernel cannot find `AB → A,B` with `split_rule` within `max_depth=2` (matching part energies), or fuse→split round-trip fails conservation.
5. **Move 4 (new beat):** Naive split accepts documented energy-mismatched `A,B` (energies 50+50) while the kernel conserved-proof helper returns `None`.
6. **Move 5:** Fuse→split→fuse apply chain breaks conservation or fails to restore `AB` energy.
7. **Move 5 (new beat):** Naive join treats same-names wrong-energy target as found while `conserved_kernel_proof` returns `None`.

## Method

1. Build source `Expression.from_names(["A", "B"], principle)` and a conserved target `AB` with `energy = source.total_energy()`.
2. Run `ImplicationEngine(principle, (fusion_rule(),)).infer(..., max_depth=2)` and assert conservation on every step.
3. Run the naive adjacent-join BFS on names only for the same name sequences.
4. Repeat with a documented mismatched target `Symbol("AB", 99.0)`: naive must report found; kernel conserved-proof helper must return `None`.
5. **Move 4:** Register `split_rule(("A","B"), (eA,eB))` on conserved `AB`; assert kernel finds `A,B` and fuse→split round-trips.
6. **Move 4:** Mismatched split target `Symbol("A",50), Symbol("B",50)`: naive split finds by names; `infer` also reaches names, but conserved-proof helper returns `None` (final-energy gate).
7. **Move 5:** Apply fuse→split→fuse on conserved `A,B`; assert each judgment conserved and final `AB` energy matches source.
8. **Move 5:** Same names `A,B` with energies 50+50: naive join finds (identity); `infer` returns `[]`; conserved-proof helper returns `None`.

Executable specification: `tests/experiment/test_conserve_vs_naive.py` (pytest **is** the experiment). Optional runner: `examples/10_conserve_vs_naive.py`.

## Move 4 — split + energy mismatch

**What was added**

- `naive_split_search`: name-only BFS that cuts a token into two contiguous substrings (ignore energy).
- Conserved `split_rule` search: `AB → A,B` within `max_depth=2` with part energies from `KernelPrinciple.default()`.
- Fuse→split round-trip: `A,B → AB → A,B` via `fusion_rule` + `split_rule`, asserting `conserved` and energy restore.
- **New naive-vs-kernel beat:** mismatched split target `(A@50, B@50)` — naive finds; kernel rejects.

**Fail criteria (move 4)**

- Pytest fails if kernel misses conserved `AB → A,B`, if round-trip breaks conservation, or if kernel **accepts** the mismatched split target as a valid conserved proof.
- Non-theatre proof: `engine.infer` reaches names `A,B` even for the 50+50 target (name-only match). The final-energy check in `conserved_kernel_proof` is load-bearing — drop it and `test_naive_accepts_energy_mismatched_split_kernel_rejects` fails.

**How to run**

```bash
pip install -e ".[dev]"
python -m pytest -q tests/experiment/test_conserve_vs_naive.py
# or full suite:
python -m pytest -q
# optional JSON summary:
python examples/10_conserve_vs_naive.py
```

Critical lint (unchanged prove gate): `ruff check gdk9 --select E9,F63,F7,F82`.

## Move 5 — fuse→split→fuse chain + same-names energy mismatch

**What was added**

- Multi-step **apply** chain `A,B → AB → A,B → AB` via `fusion_rule` + `split_rule`, asserting `conserved` and energy restore on every step.
- **New naive-vs-kernel beat:** same name sequence `A,B` with wrong declared energies `(50, 50)` — naive join treats identity as found; kernel rejects.
- Why apply (not infer) for the chain: `ImplicationEngine.infer` tracks seen *names* and will not revisit `A,B` after fusing away, so fuse→split→fuse is not a recoverable infer path. The chain is still a live kernel conservation proof.

**Fail criteria (move 5)**

- Pytest fails if any step of fuse→split→fuse breaks conservation or final `AB` energy disagrees with the source.
- Pytest fails if `conserved_kernel_proof` accepts a same-names target whose declared energy disagrees with the source.
- Non-theatre proof: `engine.infer` returns `[]` when names already match. The final-energy check in `conserved_kernel_proof` is load-bearing — drop it and `test_naive_accepts_same_names_wrong_energy_kernel_rejects` fails.

**How to run**

```bash
pip install -e ".[dev]"
python -m pytest -q tests/experiment/test_conserve_vs_naive.py
# or full suite:
python -m pytest -q
# optional JSON summary:
python examples/10_conserve_vs_naive.py
```

Critical lint (unchanged prove gate): `ruff check gdk9 --select E9,F63,F7,F82`.


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
- No claim that the kernel is faster than naive join/split.
- Success language: **beats naive join/split on proof validity under conservation.**
