from __future__ import annotations

import os
import sys
from typing import Any


class Logger:
  def __init__(self, enabled: bool = False) -> None:
    self.enabled = enabled or (os.getenv("GDK9_DEBUG") == "1")

  def set_enabled(self, enabled: bool) -> None:
    self.enabled = bool(enabled)

  def debug(self, *args: Any) -> None:
    if self.enabled:
      msg = " ".join(str(a) for a in args)
      print(f"[gdk9:debug] {msg}", file=sys.stderr)

  def info(self, *args: Any) -> None:
    msg = " ".join(str(a) for a in args)
    print(msg)

  def error(self, *args: Any) -> None:
    msg = " ".join(str(a) for a in args)
    print(msg, file=sys.stderr)


logger = Logger()

