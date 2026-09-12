"""Secure-mode crypto tests (requires cryptography / [secure] extra)."""

import pytest

pytest.importorskip("cryptography")

from gdk9.crypto import decrypt_secure, encrypt_secure
from gdk9.errors import InputError


def test_encrypt_decrypt_secure_roundtrip():
  plaintext = "secret message — round-trip"
  key = "correct-horse-battery"
  token = encrypt_secure(plaintext, key)
  assert decrypt_secure(token, key) == plaintext


def test_decrypt_secure_wrong_key_raises_input_error():
  token = encrypt_secure("payload", "right-key")
  with pytest.raises(InputError):
    decrypt_secure(token, "wrong-key")


def test_decrypt_secure_invalid_ciphertext_raises_input_error():
  with pytest.raises(InputError):
    decrypt_secure("not-a-valid-secure-payload", "any-key")
