import unittest

from gdk9.principles import Principle
from gdk9.tokenize import delimiter_set, tokenize, tokens_with_energy


class TestTokenize(unittest.TestCase):
  def setUp(self) -> None:
    self.p = Principle.default()

  def test_delimiter_set_energy_1_includes_arrows(self):
    ds = delimiter_set(self.p, energy=1)
    self.assertIn('<', ds)
    self.assertIn('>', ds)
    self.assertIn('|', ds)

  def test_tokenize_keep_and_drop(self):
    text = 'alpha|beta<gamma> delta'
    kept = tokenize(text, self.p, energy=1, keep_delims=True)
    # Delimiters are separate tokens, words are stripped
    self.assertEqual(kept, ['alpha', '|', 'beta', '<', 'gamma', '>', 'delta'])

    dropped = tokenize(text, self.p, energy=1, keep_delims=False)
    self.assertEqual(dropped, ['alpha', 'beta', 'gamma', 'delta'])

  def test_tokens_with_energy_shapes(self):
    text = 'A|B'
    toks = tokens_with_energy(text, self.p, energy=1, keep_delims=True)
    # Expect three tokens: 'A', '|', 'B'
    self.assertEqual(len(toks), 3)
    self.assertEqual([t.kind for t in toks], ['token', 'delim', 'token'])
    # Digital roots in default principle: A=1, '|'=1, B=2
    self.assertEqual([t.dr for t in toks], [1, 1, 2])


if __name__ == '__main__':  # pragma: no cover
  unittest.main()

