from __future__ import annotations

from dataclasses import dataclass

from .expression import Expression


@dataclass(frozen=True)
class Judgment:
  """The result of applying one implication rule."""

  rule: str
  before: Expression
  after: Expression
  conserved: bool
  delta: float


@dataclass(frozen=True)
class ProofStep:
  """A traceable implication step suitable for proof paths."""

  judgment: Judgment
  index: int
