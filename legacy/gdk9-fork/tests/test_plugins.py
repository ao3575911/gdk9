import json
import os
import tempfile
import unittest
from pathlib import Path

from gdk9.cli import main
from gdk9.plugins.loader import find_plugin, load_plugin, list_available
from gdk9.state import load_state, save_state


PLUGIN_JSON = {
  "name": "t_pack",
  "version": "0.1",
  "description": "test pack",
  "rules": [
    {"type": "split", "name": "T_SPLIT", "out_a": "A", "out_b": "B", "ratio": 0.5},
    {"type": "fusion", "name": "T_JOIN", "out": "AUTO", "arity": 2}
  ],
  "symbols": {"X": 10.0},
  "checks": [
    {"rule": "T_SPLIT", "inputs": [{"name": "X", "energy": 10.0}]}
  ]
}


class TestPlugins(unittest.TestCase):
  def setUp(self):
    self.tmpdir = tempfile.TemporaryDirectory()
    self.base = Path(self.tmpdir.name)
    (self.base / 'plugins').mkdir()
    self.pack_path = self.base / 'plugins' / 't_pack.json'
    self.pack_path.write_text(json.dumps(PLUGIN_JSON), encoding='utf-8')
    # state file
    self.state = {"symbols": {}, "rules": {}}
    self.state_path = self.base / 'state.json'
    save_state(self.state, str(self.state_path))

  def tearDown(self):
    self.tmpdir.cleanup()

  def test_loader_validate(self):
    p = find_plugin(str(self.pack_path))
    self.assertTrue(p.exists())
    plg = load_plugin(p)
    self.assertEqual(plg.name, 't_pack')
    self.assertEqual(len(plg.rules), 2)

  def test_cli_validate_and_load(self):
    # validate
    rc = main(["--state", str(self.state_path), "plugin", "validate", str(self.pack_path)])
    self.assertEqual(rc, 0)
    # load (also enables)
    rc = main(["--state", str(self.state_path), "plugin", "load", str(self.pack_path), "--no-enable"])  # avoid touching home config
    self.assertEqual(rc, 0)
    st = load_state(str(self.state_path))
    self.assertIn("T_SPLIT", st.get("rules", {}))
    self.assertIn("T_JOIN", st.get("rules", {}))
    self.assertIn("X", st.get("symbols", {}))


if __name__ == "__main__":  # pragma: no cover
  unittest.main()

