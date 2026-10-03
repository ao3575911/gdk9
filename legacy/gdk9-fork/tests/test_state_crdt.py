from gdk9.crdt import stamp
from gdk9.state import merge_state, set_rule, set_symbol


def _mk_state(symbols=None, rules=None):
  return {"symbols": symbols or {}, "rules": rules or {}, "crdt": {"symbols": {}, "rules": {}}}


def test_merge_state_prefers_newer_symbols():
  left = _mk_state()
  right = _mk_state()
  set_symbol(left, "A", 1.0, actor="left", timestamp=1.0)
  set_symbol(right, "A", 2.0, actor="right", timestamp=2.0)
  set_symbol(right, "B", 3.0, actor="right", timestamp=2.0)

  merged, stats = merge_state(left, right)

  assert merged["symbols"]["A"] == 2.0
  assert merged["symbols"]["B"] == 3.0
  assert merged["crdt"]["symbols"]["A"]["actor"] == "right"
  assert stats["symbols"]["updated"] == 1
  assert stats["symbols"]["added"] == 1


def test_merge_state_handles_legacy_rules():
  legacy = {"symbols": {"X": 9.0}, "rules": {"R1": {"name": "R1", "type": "fusion", "arity": 2, "params": {"out": "Z"}}}}
  incoming = _mk_state()
  set_rule(incoming, "R1", {"name": "R1", "type": "fusion", "arity": 3, "params": {"out": "Z"}}, actor="peer", timestamp=5.0)

  merged, stats = merge_state(legacy, incoming)

  assert merged["rules"]["R1"]["arity"] == 3
  assert merged["crdt"]["rules"]["R1"]["actor"] == "peer"
  assert stats["rules"]["updated"] == 1


def test_merge_state_keeps_local_when_peer_missing_entry():
  left = _mk_state()
  right = _mk_state()
  set_symbol(left, "A", 1.5, actor="local", timestamp=3.0)

  merged, stats = merge_state(left, right)

  assert merged["symbols"]["A"] == 1.5
  assert merged["crdt"]["symbols"]["A"]["actor"] == "local"
  assert stats["symbols"]["unchanged"] == 1
  assert stats["symbols"]["added"] == 0


def test_merge_state_falls_back_to_winner_metadata_value_when_data_missing():
  left = _mk_state()
  right = _mk_state({"A": 2.0})
  left["crdt"]["symbols"]["A"] = stamp(3.0, actor="left", ts=10.0)
  right["crdt"]["symbols"]["A"] = stamp(2.0, actor="right", ts=5.0)

  merged, stats = merge_state(left, right)

  assert merged["symbols"]["A"] == 3.0
  assert merged["crdt"]["symbols"]["A"]["actor"] == "left"
  assert stats["symbols"]["unchanged"] == 1


def test_merge_state_uses_rule_metadata_when_payload_missing():
  left = _mk_state()
  right = _mk_state({"R1": {"name": "R1", "type": "fusion", "arity": 2, "params": {"out": "X"}}})
  left["crdt"]["rules"]["R1"] = stamp({"name": "R1", "type": "fusion", "arity": 4, "params": {"out": "X"}}, actor="left", ts=8.0)
  right["crdt"]["rules"]["R1"] = stamp({"name": "R1", "type": "fusion", "arity": 2, "params": {"out": "X"}}, actor="right", ts=4.0)

  merged, stats = merge_state(left, right)

  assert merged["rules"]["R1"]["arity"] == 4
  assert merged["crdt"]["rules"]["R1"]["actor"] == "left"
  assert stats["rules"]["unchanged"] == 1


def test_merge_state_tolerates_partial_metadata_fields():
  left = _mk_state({"A": 1.0})
  left["crdt"]["symbols"]["A"] = {"value": 1.0, "timestamp": None}
  right = _mk_state({"A": 2.0})
  right["crdt"]["symbols"]["A"] = {"value": 2.0, "timestamp": "invalid", "actor": ""}

  merged, stats = merge_state(left, right)

  assert merged["symbols"]["A"] == 2.0
  assert merged["crdt"]["symbols"]["A"]["actor"] == "legacy"
  assert merged["crdt"]["symbols"]["A"]["timestamp"] == 0.0
  assert stats["symbols"]["updated"] == 1
