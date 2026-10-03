from __future__ import annotations

"""
Lightweight plugin registry (experimental).

Allows registering and retrieving logic packs or grammar providers by name.
This is a minimal in-memory registry intended as a stepping stone toward a
dynamic plugin loader.
"""

from typing import Any, Callable, Dict, Iterable, Optional


class PluginRegistry:
  def __init__(self) -> None:
    self._loaders: Dict[str, Callable[[], Any]] = {}

  def register(self, name: str, loader: Callable[[], Any]) -> None:
    """Register a plugin by name with a zero-arg loader callable.

    Loader should return an object that exposes the plugin interface (to be
    formalized). Duplicate registrations overwrite by design.
    """
    if not isinstance(name, str) or not name:
      raise ValueError("Plugin name must be a non-empty string")
    if not callable(loader):
      raise TypeError("loader must be callable")
    self._loaders[name] = loader

  def get(self, name: str) -> Any:
    """Load and return the plugin by name, raising KeyError if unknown."""
    loader = self._loaders[name]
    return loader()

  def list(self) -> Iterable[str]:
    """List registered plugin names."""
    return sorted(self._loaders.keys())

  def unregister(self, name: str) -> None:
    """Remove a plugin by name if present."""
    self._loaders.pop(name, None)

