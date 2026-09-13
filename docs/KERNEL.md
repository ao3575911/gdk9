# Symbolic Implication Kernel

The kernel is the smallest stable surface for GDk9 implication work. It is pure
Python, in-memory, and free of CLI, state-file, plugin, TUI, crypto, and home
directory side effects.

## Kernel Modules

- `gdk9.kernel.principle`: immutable valuation context over the existing
  GDk9 principle data.
- `gdk9.kernel.symbol`: named symbolic unit with evaluated energy.
- `gdk9.kernel.expression`: ordered symbolic expression.
- `gdk9.kernel.rule`: pure implication rule metadata and transform function.
- `gdk9.kernel.engine`: evaluation, rule application, normalization, and
  bounded implication search.
- `gdk9.kernel.proof`: traceable judgments and proof steps.

## Boundary

Kernel code may use `gdk9.energy` and `gdk9.principles` for valuation
compatibility. Kernel code must not import `gdk9.cli`, `gdk9.state`,
`gdk9.plugins`, `gdk9.crypto`, `gdk9.tui`, or terminal formatting helpers.

Adapters can wrap the kernel later, but the implication semantics should remain
testable without filesystem state or process-global configuration.

## Smoke adapter

`gdk9.kernel_cli` (and the `gdk9 kernel eval|apply|search` CLI group) adapt a
`Principle` into `KernelPrinciple` and print JSON. The adapter is deliberately
outside `gdk9/kernel/` so the pure kernel boundary stays intact.


## Research walkthrough (handbook demos)

Three CLI beats that stay inside the conservation law:

```bash
gdk9 kernel eval ABC
# total 6.0, digital_root 6  (A=1,B=2,C=3)

gdk9 kernel apply fuse A B
# before energy 3 → after AB=3, conserved true, delta 0

gdk9 kernel search A B --target AB --max-depth 2 --rules fuse
# found true — one ProofStep: fuse A,B → AB
```

Deliberate miss (research honesty):

```bash
# library: infer toward an energy-mismatched target → found false
python examples/09_kernel_search_walkthrough.py
```

## Handbook CLI doctest gate

The three smoke commands above (`eval ABC`, `apply fuse A B`, `search A B → AB`)
are pinned as CI fixtures so handbook / KERNEL examples cannot drift from live
CLI JSON.

- Fixture: `tests/fixtures/kernel_cli_handbook.json`
- Gate: `tests/test_kernel_cli_handbook.py` (subprocess `python -m gdk9.cli …`)
- Regenerate fixtures (must match *current correct* live behaviour):

```bash
python -m gdk9.cli kernel eval ABC
python -m gdk9.cli kernel apply fuse A B
python -m gdk9.cli kernel search A B --target AB --max-depth 2 --rules fuse
```

If handbook text disagrees with live CLI, fix the handbook to match live (truth),
then re-pin the fixture. See also `docs/PROVE.md`.

CI on `main` is the prove gate for changes to this surface — see `docs/PROVE.md`.