import unittest

from gdk9.crypto import encrypt, decrypt, encrypt_secure, decrypt_secure
from gdk9.errors import InputError
from gdk9.principles import Principle


class TestCrypto(unittest.TestCase):
  def setUp(self) -> None:
    self.p = Principle.default()

  def test_roundtrip_letters_digits_symbols(self):
    text = "Ab9! <>"
    key = "Key!9"
    enc = encrypt(text, key, self.p)
    dec = decrypt(enc, key, self.p)
    self.assertEqual(dec, text)

  def test_nonempty_key_required(self):
    with self.assertRaises(ValueError):
      encrypt("hi", "", self.p)

  def test_secure_requires_dependency(self):
    # If 'cryptography' is missing, encrypt_secure should raise InputError.
    try:
      encrypt_secure("hi", "key")
      # If no exception, try round-trip
      dec = decrypt_secure(encrypt_secure("hi", "key"), "key")
      self.assertEqual(dec, "hi")
    except InputError:
      # Acceptable outcome when optional dependency is not present
      pass


if __name__ == '__main__':  # pragma: no cover
  unittest.main()
