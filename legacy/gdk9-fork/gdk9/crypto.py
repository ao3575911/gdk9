from __future__ import annotations

"""
Experimental energy-driven cipher (EDPC-9).

WARNING: This is not cryptographically secure. It is a reversible
energy-guided polyalphabetic transform intended for creative/symbolic
applications, not data security. Do not use for protecting secrets.
"""

from typing import List
import base64
import os
from .errors import InputError

from .principles import Principle
from .energy import char_energy


def _keystream(principle: Principle, key: str, length: int) -> List[int]:
  if not key:
    raise ValueError("Key must be non-empty")
  ks = [char_energy(ch, principle) or 1 for ch in key]
  # normalize to 1..9, avoid zeros
  out: List[int] = []
  i = 0
  while len(out) < length:
    out.append(ks[i % len(ks)] or 1)
    i += 1
  return out


def _rotate_letter(ch: str, k: int) -> str:
  if not ch.isalpha():
    return ch
  base = ord('A') if ch.isupper() else ord('a')
  off = (ord(ch) - base + k) % 26
  return chr(base + off)


def _rotate_digit(ch: str, k: int) -> str:
  if not ch.isdigit():
    return ch
  base = ord('0')
  off = (ord(ch) - base + (k % 10)) % 10
  return chr(base + off)


def _rotate_symbol(ch: str, k: int, principle: Principle) -> str:
  # Build a stable ordered list of known symbols; fallback to identity
  symbols = sorted(set(principle.symbol_energy.keys()))
  if ch not in symbols:
    return ch
  idx = symbols.index(ch)
  return symbols[(idx + k) % len(symbols)]


def encrypt(text: str, key: str, principle: Principle) -> str:
  ks = _keystream(principle, key, len(text))
  out = []
  for i, ch in enumerate(text):
    k = ks[i]
    if ch.isalpha():
      out.append(_rotate_letter(ch, k))
    elif ch.isdigit():
      out.append(_rotate_digit(ch, k))
    elif ch.isspace():
      out.append(ch)
    else:
      out.append(_rotate_symbol(ch, k, principle))
  return "".join(out)


def decrypt(cipher: str, key: str, principle: Principle) -> str:
  ks = _keystream(principle, key, len(cipher))
  out = []
  for i, ch in enumerate(cipher):
    k = ks[i]
    if ch.isalpha():
      out.append(_rotate_letter(ch, -k))
    elif ch.isdigit():
      out.append(_rotate_digit(ch, -k))
    elif ch.isspace():
      out.append(ch)
    else:
      out.append(_rotate_symbol(ch, -k, principle))
  return "".join(out)


# Secure mode (optional dependency on 'cryptography')

def _derive_key(passphrase: str, salt: bytes) -> bytes:
  if not passphrase:
    raise InputError("Key must be non-empty")
  # 32-byte key via PBKDF2-HMAC-SHA256
  from hashlib import pbkdf2_hmac
  raw = pbkdf2_hmac('sha256', passphrase.encode('utf-8'), salt, 200_000, dklen=32)
  return base64.urlsafe_b64encode(raw)


def encrypt_secure(text: str, key: str) -> str:
  try:
    from cryptography.fernet import Fernet
  except Exception as exc:  # pragma: no cover - optional dependency
    raise InputError("Secure mode requires 'cryptography' package. Install it to use --mode secure.") from exc
  salt = os.urandom(16)
  f = Fernet(_derive_key(key, salt))
  token = f.encrypt(text.encode('utf-8'))
  payload = b'G9F' + salt + token
  return base64.urlsafe_b64encode(payload).decode('ascii')


def decrypt_secure(ciphertext: str, key: str) -> str:
  try:
    from cryptography.fernet import Fernet
  except Exception as exc:  # pragma: no cover - optional dependency
    raise InputError("Secure mode requires 'cryptography' package. Install it to use --mode secure.") from exc
  raw = base64.urlsafe_b64decode(ciphertext.encode('ascii'))
  if not raw.startswith(b'G9F') or len(raw) < 19:
    raise InputError("Invalid secure ciphertext")
  salt = raw[3:19]
  token = raw[19:]
  f = Fernet(_derive_key(key, salt))
  try:
    out = f.decrypt(token)
  except Exception as exc:
    raise InputError("Decryption failed; wrong key or corrupted data") from exc
  return out.decode('utf-8')

