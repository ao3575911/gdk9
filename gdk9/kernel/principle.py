from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from gdk9.energy import char_energy, digital_root
from gdk9.principles import Principle


@dataclass(frozen=True)
class KernelPrinciple:
  """Immutable valuation context for kernel expressions."""

  name: str
  symbol_energy: Mapping[str, float] = field(default_factory=dict)
  source: Principle | None = None
  normalize_zero_to_nine: bool = True

  @classmethod
  def default(cls) -> "KernelPrinciple":
    principle = Principle.default()
    return cls(
      name=principle.name,
      symbol_energy=dict(principle.symbol_energy),
      source=principle,
      normalize_zero_to_nine=principle.normalize_zero_to_nine,
    )

  def energy_of(self, name: str) -> float:
    if len(name) == 1:
      if self.source is not None:
        return float(char_energy(name, self.source))
      explicit = self.symbol_energy.get(name)
      if explicit is not None:
        return float(explicit)
      return float(digital_root(ord(name), self.normalize_zero_to_nine))
    explicit = self.symbol_energy.get(name)
    if explicit is not None:
      return float(explicit)
    return sum(self.energy_of(ch) for ch in name)

  def total_root(self, total: float) -> int:
    return digital_root(int(round(total)), self.normalize_zero_to_nine)
