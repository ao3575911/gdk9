from typing import Protocol, Any, Dict, Iterable, List
import importlib
import importlib.metadata
import logging

logger = logging.getLogger(__name__)

class PluginSpec(Protocol):
    """Protocol for plugin classes."""

    name: str

    def setup(self, config: Dict[str, Any]) -> None:
        ...

    def run(self, *args, **kwargs) -> Any:
        ...

def _get_entry_points(group: str):
    # Support both older and newer importlib.metadata APIs
    try:
        eps = importlib.metadata.entry_points()
        select = getattr(eps, "select", None)
        if callable(select):
            return eps.select(group=group)
        # older style where entry_points returns a list
        return [ep for ep in eps if ep.group == group]
    except Exception:
        return []

def load_plugins(group: str = "gdk9.plugins") -> List[PluginSpec]:
    """Load plugin classes registered via entry points under the given group.

    Returns instantiated plugin objects (no args passed to constructor).
    """
    loaded = []
    for ep in _get_entry_points(group):
        try:
            plugin_obj = ep.load()
            # ep.load() may return a class or a factory function
            if isinstance(plugin_obj, type):
                inst = plugin_obj()
            else:
                inst = plugin_obj()
            logger.debug("Loaded plugin %s from %s", getattr(inst, "name", str(ep)), ep.value)
            loaded.append(inst)
        except Exception as e:
            logger.exception("Failed to load plugin %s: %s", getattr(ep, "name", ep), e)
    return loaded