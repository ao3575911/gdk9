from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from .errors import InputError


def read_input(text: Optional[str], file: Optional[str]) -> str:
  if file and text:
    raise InputError("Provide either text or --file, not both.")
  if file:
    p = Path(file)
    if not p.exists() or not p.is_file():
      raise InputError(f"File not found: {file}")
    return p.read_text(encoding="utf-8", errors="replace")
  if text:
    return text
  data = sys.stdin.read()
  if not data:
    raise InputError("No input provided. Pass text, --file, or pipe stdin.")
  return data

