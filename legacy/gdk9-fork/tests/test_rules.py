import os
import tempfile
import unittest

from gdk9.state import load_state, save_state, set_symbol
from gdk9.imply import make_fusion, make_split, apply_rule, Rule


class TestRules(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.NamedTemporaryFile(delete=False)
    self.tmp.close()
    self.state_path = self.tmp.name
    self.state = {"symbols": {}, "rules": {}}
    set_symbol(self.state, "A", 2.0)
    set_symbol(self.state, "B", 3.0)
    save_state(self.state, self.state_path)

  def tearDown(self):
    try:
      os.unlink(self.state_path)
    except FileNotFoundError:
      pass

  def test_fusion(self):
    r = make_fusion("FUSE", "AUTO", 2)
    res = apply_rule(r, load_state(self.state_path)["symbols"], ["A", "B"], tol=1e-9)
    outs = res["outputs"][0]
    self.assertEqual(outs["name"], "AB")
    self.assertAlmostEqual(outs["energy"], 5.0, places=9)

  def test_split(self):
    r = make_split("SPLIT", "A1", "A2", 0.4)
    res = apply_rule(r, load_state(self.state_path)["symbols"], ["B"], tol=1e-9)
    outs = res["outputs"]
    self.assertEqual(len(outs), 2)
    self.assertAlmostEqual(outs[0]["energy"], 1.2, places=9)
    self.assertAlmostEqual(outs[1]["energy"], 1.8, places=9)


if __name__ == "__main__":
  unittest.main()

