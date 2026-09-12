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

