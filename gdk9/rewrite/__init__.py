"""
Symbol Rewrite Reactor (SRR) public API.

This package provides classes and functions for working with the symbol
rewrite reactor.  Users can construct a :class:`~gdk9.rewrite.symbol.SymbolRegistry`,
parse rewrite rules, execute a :class:`~gdk9.rewrite.runtime.Reactor` over an input
sequence and inspect the resulting symbol stream.  The module also
exposes the package version for introspection.
"""

from .symbol import SymbolRegistry
from .rules import Rule, PatternElement, parse_rules
from .runtime import Reactor, run_reactor

__all__ = [
    "SymbolRegistry",
    "Rule",
    "PatternElement",
    "parse_rules",
    "Reactor",
    "run_reactor",
]

__version__ = "1.0.0"