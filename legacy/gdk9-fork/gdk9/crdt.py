from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class LwwEntry:
  value: Any
  timestamp: float
  actor: str


def coerce_entry(raw: Any, default_actor: str = "legacy", default_ts: float = 0.0) -> LwwEntry:
  if isinstance(raw, dict):
    value = raw.get("value", raw)
    try:
      ts = float(raw.get("timestamp", default_ts))
    except (TypeError, ValueError):
      ts = float(default_ts)
    actor_raw = raw.get("actor", default_actor)
    actor = default_actor if actor_raw in {None, ""} else str(actor_raw)
    return LwwEntry(value, ts, actor)
  return LwwEntry(raw, float(default_ts), default_actor)


def lww_merge(a: LwwEntry, b: LwwEntry) -> LwwEntry:
  if b.timestamp > a.timestamp:
    return b
  if b.timestamp < a.timestamp:
    return a
  return b if b.actor >= a.actor else a


def stamp(value: Any, actor: str | None = None, ts: float | None = None) -> Dict[str, Any]:
  return {
    "value": value,
    "timestamp": float(time.time() if ts is None else ts),
    "actor": actor or "anonymous",
  }


def merge_maps(
  left: Dict[str, Any],
  right: Dict[str, Any],
  default_actor: str = "legacy",
  default_ts: float = 0.0,
) -> Tuple[Dict[str, Any], Dict[str, int], Dict[str, str]]:
  """Merge two LWW maps.

  The returned tuple contains the merged map, update statistics, and the winner side for
  each key ("left" or "right"). When inputs omit CRDT metadata, ``default_actor`` and
  ``default_ts`` supply deterministic fallbacks so downstream consumers never see missing
  fields.
  """
  merged: Dict[str, Any] = {}
  stats = {"added": 0, "updated": 0, "unchanged": 0}
  winners: Dict[str, str] = {}
  keys = set(left.keys()) | set(right.keys())
  for key in keys:
    has_left = key in left
    has_right = key in right
    if has_left and not has_right:
      lentry = coerce_entry(left[key], default_actor, default_ts)
      merged[key] = {"value": lentry.value, "timestamp": lentry.timestamp, "actor": lentry.actor}
      winners[key] = "left"
      stats["unchanged"] += 1
      continue
    if has_right and not has_left:
      rentry = coerce_entry(right[key], default_actor, default_ts)
      merged[key] = {"value": rentry.value, "timestamp": rentry.timestamp, "actor": rentry.actor}
      winners[key] = "right"
      stats["added"] += 1
      continue

    lentry = coerce_entry(left.get(key), default_actor, default_ts)
    rentry = coerce_entry(right.get(key), default_actor, default_ts)
    winner = lww_merge(lentry, rentry)
    merged[key] = {"value": winner.value, "timestamp": winner.timestamp, "actor": winner.actor}
    winners[key] = "left" if winner is lentry else "right"
    if winner is lentry:
      stats["unchanged"] += 1
    elif lentry.value != rentry.value or lentry.timestamp != rentry.timestamp or lentry.actor != rentry.actor:
      stats["updated"] += 1
    else:
      stats["unchanged"] += 1
  return merged, stats, winners
