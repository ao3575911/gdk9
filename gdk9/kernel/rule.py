from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from .expression import Expression

Transform = Callable[[Expression], Expression]


class RuleKind(str, Enum):
  FUSION = "fusion"
  SPLIT = "split"
  REWRITE = "rewrite"


@dataclass(frozen=True)
class ImplicationRule:
  """A pure implication transform with invariant metadata."""

  name: str
  kind: RuleKind
  transform: Transform
  reversible: bool = False
  preserves_energy: bool = True
  tolerance: float = 1e-9

  def apply(self, expression: Expression) -> Expression:
    return self.transform(expression)
