import unittest

from gdk9.optimize import optimize_attunement, apply_plan
from gdk9.principles import Principle


class TestOptimize(unittest.TestCase):
  def test_optimize_reaches_target(self):
    p = Principle.default()
    text = "Hello, world!"
    plan = optimize_attunement(text, 7, p, allowed_symbols='.!?*+')
    out = apply_plan(text, plan)
    # Confirm digital root matches
    from gdk9.energy import string_energy
    total, dr = string_energy(out, p)
    self.assertEqual(dr, 7)


if __name__ == "__main__":  # pragma: no cover
  unittest.main()

