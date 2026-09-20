"""Phase B spike: one KeySuite compose.basic vector via outside-kernel adapter.

Vendored row: compose.basic.001 from gdk9_keysuite (read-only).
Asserts honest kernel name concatenation + conserved fusion — not the FSM.
See docs/KEYSUITE_BRIDGE.md (Phase B spike).
"""
from __future__ import annotations

import json
from pathlib import Path

from gdk9.kernel import ImplicationEngine, KernelPrinciple
from gdk9.kernel.engine import fusion_rule
from gdk9.keysuite_bridge.compose import (
  content_names,
  expression_from_compose_tokens,
)

_FIXTURE = Path(__file__).parent / "fixtures" / "compose.basic.001.json"


def _load_vector() -> dict:
  return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def test_compose_basic_001_kernel_names_match_output():
  """Partial-fit: content names concatenate to KeySuite output string."""
  vector = _load_vector()
  assert vector["id"] == "compose.basic.001"
  assert content_names(vector["tokens"]) == ("A", "B")

  expr = expression_from_compose_tokens(vector["tokens"])
  assert expr.text() == vector["output"] == "AB"
  assert expr.names() == ("A", "B")


def test_compose_basic_001_fusion_conserves_to_output_name():
  """Partial-fit: fusion_rule yields name AB with conserved energy."""
  vector = _load_vector()
  principle = KernelPrinciple.default()
  expr = expression_from_compose_tokens(vector["tokens"], principle)
  engine = ImplicationEngine(principle, (fusion_rule(),))
  judgment = engine.apply("fuse", expr)
  assert judgment.conserved is True
  assert judgment.after.names() == (vector["output"],)
  assert judgment.after.total_energy() == expr.total_energy()
