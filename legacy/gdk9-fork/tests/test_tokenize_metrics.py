import json
import unittest

from gdk9.principles import Principle
from gdk9.tokenize import to_json_payload


class TestTokenizeMetrics(unittest.TestCase):
  def setUp(self) -> None:
    self.p = Principle.default()

  def test_per_token_classes_and_metrics(self):
    text = 'Ab9!'
    payload = json.loads(to_json_payload(text, self.p, energy=1, keep_delims=True))
    tokens = payload['tokens']
    self.assertEqual(len(tokens), 1)
    t0 = tokens[0]
    # Per-token class counts and energies exist and are correct under default principle
    self.assertEqual(t0['letters'], 2)
    self.assertEqual(t0['digits'], 1)
    self.assertEqual(t0['symbols'], 1)
    self.assertEqual(t0['e_letters'], 3)
    self.assertEqual(t0['e_digits'], 9)
    self.assertEqual(t0['e_symbols'], 3)
    metrics = payload['metrics']
    self.assertIn('classes', metrics)
    self.assertEqual(metrics['classes']['content']['counts']['letters'], 2)
    self.assertEqual(metrics['classes']['content']['energy']['digits'], 9)


if __name__ == '__main__':  # pragma: no cover
  unittest.main()

