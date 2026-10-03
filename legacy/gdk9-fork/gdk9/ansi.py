from __future__ import annotations

import os
import sys


def supports_color() -> bool:
  if os.getenv("NO_COLOR") == "1":
    return False
  term = os.getenv("TERM", "")
  if term in ("dumb", ""):  # minimal terminals
    return False
  return sys.stdout.isatty()


def colorize(text: str, color: str | None, enabled: bool) -> str:
  if not enabled or not color:
    return text
  colors = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "bold": "\033[1m",
  }
  reset = "\033[0m"
  return f"{colors.get(color, '')}{text}{reset}"

