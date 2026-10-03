"""Plugin system stubs for Gdk9.

Future work will expose a stable interface for loading user-defined symbolic
grammars and rule packs at runtime. See `registry.py` for the current
experimental surface.
"""

from .registry import PluginRegistry

__all__ = ["PluginRegistry"]

