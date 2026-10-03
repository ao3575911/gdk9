import os
import tempfile
import unittest

from gdk9.state import load_state, save_state, set_symbol
from gdk9.imply import make_fusion, make_split, apply_rule


class TestRuleReversibility(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.NamedTemporaryFile(delete=False)
    self.tmp.close()
    self.state_path = self.tmp.name
    self.state = {"symbols": {}, "rules": {}}
    # Base symbols
    set_symbol(self.state, "A", 2.0)
    set_symbol(self.state, "B", 3.0)
    save_state(self.state, self.state_path)

  def tearDown(self):
    try:
      os.unlink(self.state_path)
    except FileNotFoundError:
      pass

  def test_fusion_then_split_is_reversible_by_ratio(self):
    # Fuse A and B -> AB with energy 5.0
    st = load_state(self.state_path)
    fuse = make_fusion("FUSE", "AUTO", 2)
    fused = apply_rule(fuse, st["symbols"], ["A", "B"], tol=1e-9)
    out = fused["outputs"][0]
    self.assertEqual(out["energy"], 5.0)
    ab_energy = out["energy"]
    # Register fused symbol for the split step
    set_symbol(st, "AB", ab_energy)
    save_state(st, self.state_path)

    # Split AB using exact ratio to recover original energies
    ratio = 2.0 / (2.0 + 3.0)
    split = make_split("SPLIT", "A_REC", "B_REC", ratio)
    res = apply_rule(split, load_state(self.state_path)["symbols"], ["AB"], tol=1e-9)
    outs = res["outputs"]
    vals = sorted(e["energy"] for e in outs)
    self.assertAlmostEqual(vals[0], 2.0, places=9)
    self.assertAlmostEqual(vals[1], 3.0, places=9)


if __name__ == "__main__":  # pragma: no cover
  unittest.main()

