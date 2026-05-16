"""Minimal symbolic implication kernel.

The kernel package is intentionally independent from the CLI and plugin
surfaces. It exposes small, typed primitives that can be composed and tested
without file-system state, terminal output, or user configuration side effects.
"""

from .engine import ImplicationEngine
from .expression import Expression
from .principle import KernelPrinciple
from .proof import Judgment, ProofStep
from .rule import ImplicationRule, RuleKind
from .symbol import Symbol

__all__ = [
  "Expression",
  "ImplicationEngine",
  "ImplicationRule",
  "Judgment",
  "KernelPrinciple",
  "ProofStep",
  "RuleKind",
  "Symbol",
]
