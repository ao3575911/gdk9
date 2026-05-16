"""Kernel-specific exceptions."""


class KernelError(Exception):
  """Base exception for symbolic implication kernel failures."""


class ConservationError(KernelError):
  """Raised when a transformation violates an invariant."""


class ImplicationError(KernelError):
  """Raised when a rule cannot be applied to an expression."""


class UnknownSymbolError(KernelError):
  """Raised when an expression references a symbol absent from a principle."""
