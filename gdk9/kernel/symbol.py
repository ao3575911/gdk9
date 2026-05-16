from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class Symbol:
  """A named symbolic unit with an evaluated energy."""

  name: str
  energy: float
  traits: Mapping[str, str] = field(default_factory=dict)

  def __post_init__(self) -> None:
    if not self.name:
      raise ValueError("Symbol name must be non-empty")
    if not isinstance(self.energy, (int, float)):
      raise TypeError("Symbol energy must be numeric")
