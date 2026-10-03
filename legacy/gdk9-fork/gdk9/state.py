from __future__ import annotations

import copy
import json
import math
import os
import socket
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from .crdt import merge_maps, stamp
from .errors import InputError


DEFAULT_STATE_PATH = os.path.expanduser("~/.gdk9/state.json")
LEGACY_ACTOR = "legacy"
_MISSING = object()


def _ensure_parent(path: Path) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)


def load_state(path: Optional[str] = None) -> Dict[str, Any]:
  p = Path(path or DEFAULT_STATE_PATH)
  if not p.exists():
    return {"symbols": {}, "rules": {}, "crdt": {"symbols": {}, "rules": {}}}
  try:
    state = json.loads(p.read_text(encoding="utf-8"))
    return _ensure_state_shape(state)
  except Exception as exc:
    raise InputError(f"Failed to read state from {p}: {exc}")


def save_state(state: Dict[str, Any], path: Optional[str] = None) -> None:
  p = Path(path or DEFAULT_STATE_PATH)
  _ensure_parent(p)
  tmp = p.with_suffix(p.suffix + ".tmp")
  tmp.write_text(json.dumps(_ensure_state_shape(state), ensure_ascii=False, indent=2), encoding="utf-8")
  tmp.replace(p)


def _ensure_state_shape(state: Dict[str, Any]) -> Dict[str, Any]:
  state.setdefault("symbols", {})
  state.setdefault("rules", {})
  crdt = state.setdefault("crdt", {})
  crdt.setdefault("symbols", {})
  crdt.setdefault("rules", {})
  for name in list(state.get("symbols", {}).keys()):
    crdt["symbols"].setdefault(name, stamp(state["symbols"].get(name), LEGACY_ACTOR, 0.0))
  for name in list(state.get("rules", {}).keys()):
    crdt["rules"].setdefault(name, stamp(state["rules"].get(name), LEGACY_ACTOR, 0.0))
  return state


def _default_actor() -> str:
  return os.getenv("GDK9_ACTOR_ID") or socket.gethostname() or "anonymous"


def get_symbol(state: Dict[str, Any], name: str) -> Optional[float]:
  return state.get("symbols", {}).get(name)


def set_symbol(state: Dict[str, Any], name: str, energy: float, actor: Optional[str] = None, timestamp: Optional[float] = None) -> None:
  if not math.isfinite(energy):
    raise InputError("Energy must be a finite float")
  st = _ensure_state_shape(state)
  st.setdefault("symbols", {})[name] = float(energy)
  st.setdefault("crdt", {}).setdefault("symbols", {})[name] = stamp(float(energy), actor or _default_actor(), timestamp)


def list_symbols(state: Dict[str, Any]) -> Dict[str, float]:
  return dict(sorted(state.get("symbols", {}).items()))


def set_rule(state: Dict[str, Any], name: str, data: Dict[str, Any], actor: Optional[str] = None, timestamp: Optional[float] = None) -> None:
  st = _ensure_state_shape(state)
  st.setdefault("rules", {})[name] = data
  st.setdefault("crdt", {}).setdefault("rules", {})[name] = stamp(data, actor or _default_actor(), timestamp)


def merge_state(left: Dict[str, Any], right: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Dict[str, int]]]:
  lstate = _ensure_state_shape(copy.deepcopy(left))
  rstate = _ensure_state_shape(copy.deepcopy(right))
  merged: Dict[str, Any] = {"symbols": {}, "rules": {}, "crdt": {"symbols": {}, "rules": {}}}
  sym_meta, sym_stats, sym_winners = merge_maps(
    lstate.get("crdt", {}).get("symbols", {}),
    rstate.get("crdt", {}).get("symbols", {}),
    LEGACY_ACTOR,
    0.0,
  )
  merged["crdt"]["symbols"] = sym_meta
  for name in sym_meta.keys():
    merged["symbols"][name] = _resolve_value(
      name,
      sym_winners.get(name),
      sym_meta,
      lstate.get("symbols", {}),
      rstate.get("symbols", {}),
    )
  rule_meta, rule_stats, rule_winners = merge_maps(
    lstate.get("crdt", {}).get("rules", {}),
    rstate.get("crdt", {}).get("rules", {}),
    LEGACY_ACTOR,
    0.0,
  )
  merged["crdt"]["rules"] = rule_meta
  for name in rule_meta.keys():
    merged["rules"][name] = _resolve_value(
      name,
      rule_winners.get(name),
      rule_meta,
      lstate.get("rules", {}),
      rstate.get("rules", {}),
    )
  return merged, {"symbols": sym_stats, "rules": rule_stats}


def _resolve_value(
  name: str,
  winner: Optional[str],
  meta: Dict[str, Dict[str, Any]],
  left_data: Dict[str, Any],
  right_data: Dict[str, Any],
) -> Any:
  """Resolve the value for a CRDT key using winner metadata and payload fallbacks."""
  side = winner if winner in {"left", "right"} else ("left" if name in left_data else "right")
  primary = left_data if side == "left" else right_data
  secondary = right_data if side == "left" else left_data
  value = primary.get(name, _MISSING)
  if value is _MISSING:
    meta_value = meta.get(name, {}).get("value", _MISSING)
    if meta_value is not _MISSING:
      value = meta_value
  if value is _MISSING:
    value = secondary.get(name, _MISSING)
  return None if value is _MISSING else value

