import os
import tempfile
import unittest

from gdk9.cli import main
from gdk9.state import load_state, save_state, set_symbol


class TestRulesCommit(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.NamedTemporaryFile(delete=False)
    self.tmp.close()
    self.state_path = self.tmp.name
    state = {"symbols": {}, "rules": {}}
    set_symbol(state, "X", 10.0)
    save_state(state, self.state_path)

  def tearDown(self):
    try:
      os.unlink(self.state_path)
    except FileNotFoundError:
      pass

  def test_apply_commit(self):
    # define split
    rc = main(["--state", self.state_path, "imply", "define-split", "SPL", "X1", "X2", "0.5"])
    self.assertEqual(rc, 0)
    # apply with commit
    rc = main(["--state", self.state_path, "imply", "apply", "SPL", "X", "--commit"])
    self.assertEqual(rc, 0)
    st = load_state(self.state_path)
    self.assertIn("X1", st.get("symbols", {}))
    self.assertIn("X2", st.get("symbols", {}))
    self.assertAlmostEqual(st["symbols"]["X1"], 5.0, places=6)
    self.assertAlmostEqual(st["symbols"]["X2"], 5.0, places=6)


if __name__ == "__main__":
  unittest.main()

