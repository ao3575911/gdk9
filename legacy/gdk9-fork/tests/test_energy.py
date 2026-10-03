import unittest

from gdk9.energy import digital_root, string_energy, char_energy
from gdk9.principles import Principle


class TestEnergy(unittest.TestCase):
  def setUp(self) -> None:
    self.p = Principle.default()

  def test_digital_root(self):
    self.assertEqual(digital_root(0), 9)
    self.assertEqual(digital_root(9), 9)
    self.assertEqual(digital_root(10), 1)
    self.assertEqual(digital_root(26), 8)

  def test_char_energy_letters(self):
    self.assertEqual(char_energy("A", self.p), 1)
    self.assertEqual(char_energy("Z", self.p), 8)

  def test_char_energy_digit(self):
    self.assertEqual(char_energy("0", self.p), 9)
    self.assertEqual(char_energy("9", self.p), 9)
    self.assertEqual(char_energy("5", self.p), 5)

  def test_string_energy(self):
    total, dr = string_energy("ABC", self.p)
    self.assertEqual(total, 1 + 2 + 3)
    self.assertEqual(dr, 6)


if __name__ == "__main__":  # pragma: no cover
  unittest.main()

