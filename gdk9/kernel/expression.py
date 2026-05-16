from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Sequence

from .principle import KernelPrinciple
from .symbol import Symbol


@dataclass(frozen=True)
class Expression:
  """An ordered symbolic expression."""

  symbols: tuple[Symbol, ...]

  @classmethod
  def from_names(cls, names: Iterable[str], principle: KernelPrinciple) -> "Expression":
    return cls(tuple(Symbol(name, principle.energy_of(name)) for name in names))

  @classmethod
  def from_text(cls, text: str, principle: KernelPrinciple) -> "Expression":
    return cls.from_names(text, principle)

  def __iter__(self) -> Iterator[Symbol]:
    return iter(self.symbols)

  def __len__(self) -> int:
    return len(self.symbols)

  def names(self) -> tuple[str, ...]:
    return tuple(symbol.name for symbol in self.symbols)

  def total_energy(self) -> float:
    return sum(symbol.energy for symbol in self.symbols)

  def digital_root(self, principle: KernelPrinciple) -> int:
    return principle.total_root(self.total_energy())

  def text(self) -> str:
    return "".join(self.names())

  def replace(self, symbols: Sequence[Symbol]) -> "Expression":
    return Expression(tuple(symbols))
