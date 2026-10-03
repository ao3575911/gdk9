from __future__ import annotations

"""
Energy registry and parsing helpers.

This module centralizes access to the active principle's symbol energy
mapping to discourage arbitrary, ad hoc assignments. Use these helpers when
you need to resolve or expose symbol energies.
"""

from typing import Dict

from .principles import Principle, load_principle
from .energy import char_energy


def loadPrinciple(path: str | None) -> Principle:
  """Load a `Principle` from a JSON/YAML file or return the default when None."""
  return load_principle(path)


def energyRegistry(principle: Principle) -> Dict[str, int]:
  """Return the symbol-energy mapping for the active principle.

  The registry contains explicit symbol assignments (non-alphanumeric). Letters and digits
  remain computed via principle modes and weights using `char_energy`.
  """
  # Copy to avoid accidental mutation of the original mapping
  return dict(principle.symbol_energy)


def resolveCharEnergy(ch: str, principle: Principle) -> int:
  """Resolve the energy for a single character via the registry and rules."""
  return char_energy(ch, principle)

