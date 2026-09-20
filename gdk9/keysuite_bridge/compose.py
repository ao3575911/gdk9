"""Compose-vector adapter: content tokens → kernel Expression names.

KeySuite ``compose.basic.*`` emits concatenated content on COMMIT. The kernel
has no token stream or IDLE/COMPOSE FSM (Phase A: partial). This adapter only:

1. Drops known COMMIT event tokens (SPACE / ENTER / TAB / TIMEOUT / DONE).
2. Treats remaining tokens as symbol names for ``Expression.from_names``.
3. Returns the expression for callers to assert ``text()`` / fusion energy.

It does **not** implement bind, mode, abort, escape, rollback, or ERROR.
"""
from __future__ import annotations

from typing import Sequence

from gdk9.kernel import Expression, KernelPrinciple

# Grammar COMMIT set (gdk9_keysuite grammar) — stripped, not executed as FSM.
_COMMIT_TOKENS = frozenset({"SPACE", "ENTER", "TAB", "TIMEOUT", "DONE"})


def content_names(tokens: Sequence[str]) -> tuple[str, ...]:
  """Return non-COMMIT tokens as ordered symbol names."""
  return tuple(t for t in tokens if t not in _COMMIT_TOKENS)


def expression_from_compose_tokens(
  tokens: Sequence[str],
  principle: KernelPrinciple | None = None,
) -> Expression:
  """Build a kernel Expression from compose-vector content tokens."""
  names = content_names(tokens)
  if not names:
    raise ValueError("compose adapter: no content tokens after stripping COMMIT")
  return Expression.from_names(names, principle or KernelPrinciple.default())
