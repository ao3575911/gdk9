from __future__ import annotations

from typing import Tuple

from .energy import attune_text, synthesize_sigil
from .principles import Principle


def attune(text: str, target: int, principle: Principle, symbol: str = ".") -> Tuple[str, int, int, int]:
  return attune_text(text, target, principle, method="append", symbol=symbol)


def sigil(text: str, principle: Principle, style: str = "grid") -> str:
  return synthesize_sigil(text, principle, style=style)

