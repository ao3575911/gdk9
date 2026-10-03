from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from .principles import Principle


def digital_root(n: int, zero_to_nine: bool = True) -> int:
  n = abs(int(n))
  if n == 0:
    return 9 if zero_to_nine else 0
  return 9 if (n % 9 == 0) else (n % 9)


def letter_value(ch: str) -> int:
  c = ch.upper()
  if "A" <= c <= "Z":
    return ord(c) - ord("A") + 1
  return ord(c)


def char_energy(ch: str, principle: Principle) -> int:
  if ch.isspace():
    return 0
  if ch.isalpha():
    base = letter_value(ch) if principle.letter_mode == "a1z26" else ord(ch)
    e = digital_root(base, principle.normalize_zero_to_nine)
    return digital_root(e * principle.weights.get("letter", 1), principle.normalize_zero_to_nine)
  if ch.isdigit():
    base = int(ch)
    e = digital_root(base, principle.normalize_zero_to_nine)
    return digital_root(e * principle.weights.get("digit", 1), principle.normalize_zero_to_nine)
  if ch in principle.symbol_energy:
    e = digital_root(principle.symbol_energy[ch], principle.normalize_zero_to_nine)
    return digital_root(e * principle.weights.get("symbol", 1), principle.normalize_zero_to_nine)
  # Fallback for other unicode symbols
  e = digital_root(ord(ch), principle.normalize_zero_to_nine)
  return digital_root(e * principle.weights.get("symbol", 1), principle.normalize_zero_to_nine)


def string_energy(text: str, principle: Principle) -> Tuple[int, int]:
  total = sum(char_energy(ch, principle) for ch in text)
  return total, digital_root(total, principle.normalize_zero_to_nine)


def tokenize_sentences(text: str) -> List[str]:
  # Simple sentence split on .!? while retaining textual coherence
  parts = re.split(r"(?<=[.!?])\s+", text.strip())
  return [p for p in parts if p]


def tokenize_words(text: str) -> List[str]:
  return re.findall(r"\b\w+\b", text, flags=re.UNICODE)


@dataclass
class UnitEnergy:
  unit: str
  value: str
  energy: int
  total: int


def analyze_text(text: str, principle: Principle) -> Dict[str, Iterable[UnitEnergy]]:
  chars: List[UnitEnergy] = []
  for ch in text:
    e = char_energy(ch, principle)
    total = e
    chars.append(UnitEnergy("char", ch, e, total))

  words: List[UnitEnergy] = []
  for w in tokenize_words(text):
    total, dr = string_energy(w, principle)
    words.append(UnitEnergy("word", w, dr, total))

  sentences: List[UnitEnergy] = []
  for s in tokenize_sentences(text):
    total, dr = string_energy(s, principle)
    sentences.append(UnitEnergy("sentence", s, dr, total))

  paragraphs: List[UnitEnergy] = []
  for p in [pp for pp in text.splitlines() if pp.strip()]:
    total, dr = string_energy(p, principle)
    paragraphs.append(UnitEnergy("paragraph", p, dr, total))

  doc_total, doc_dr = string_energy(text, principle)
  doc = [UnitEnergy("document", text, doc_dr, doc_total)]

  return {
    "chars": chars,
    "words": words,
    "sentences": sentences,
    "paragraphs": paragraphs,
    "document": doc,
  }


def vector_energy(text: str, principle: Principle) -> Dict[str, Dict[str, int]]:
  letters = 0
  digits = 0
  symbols = 0
  for ch in text:
    if ch.isspace():
      continue
    if ch.isalpha():
      letters += char_energy(ch, principle)
    elif ch.isdigit():
      digits += char_energy(ch, principle)
    else:
      symbols += char_energy(ch, principle)
  return {
    "sum": {"letters": letters, "digits": digits, "symbols": symbols},
    "dr": {
      "letters": digital_root(letters, principle.normalize_zero_to_nine),
      "digits": digital_root(digits, principle.normalize_zero_to_nine),
      "symbols": digital_root(symbols, principle.normalize_zero_to_nine),
    },
  }


def harmonic_triads(text: str, principle: Principle) -> Dict[str, int]:
  # Group by residue classes: 1/4/7=root, 2/5/8=wave, 3/6/9=peak
  triads = {"root": 0, "wave": 0, "peak": 0}
  for ch in text:
    e = char_energy(ch, principle)
    if e == 0:
      continue
    r = e % 9
    if r in (1, 4, 7):
      triads["root"] += 1
    elif r in (2, 5, 8):
      triads["wave"] += 1
    else:
      triads["peak"] += 1
  return triads


def energy_profile(text: str, principle: Principle) -> Dict[str, int]:
  profile: Dict[str, int] = {str(i): 0 for i in range(1, 10)}
  for ch in text:
    e = char_energy(ch, principle)
    key = str(9 if e == 0 else e)
    profile[key] += 1
  return profile


def required_delta(current: int, target: int, zero_to_nine: bool = True) -> int:
  if current == target:
    return 0
  # Determine minimal addition to move digital root to target
  # Try deltas 1..100 and pick the first that matches
  for d in range(1, 101):
    if digital_root(current + d, zero_to_nine) == target:
      return d
  return 0


def attune_text(
  text: str,
  target: int,
  principle: Principle,
  method: str = "append",
  symbol: str = ".",
) -> Tuple[str, int, int, int]:
  total, dr = string_energy(text, principle)
  if not (1 <= target <= 9):
    raise ValueError("Target energy must be 1..9")
  if dr == target:
    return text, total, dr, 0
  if method != "append":
    raise ValueError("Only 'append' method supported in default build")
  sym_e = char_energy(symbol, principle)
  delta = required_delta(total, target, principle.normalize_zero_to_nine)
  if sym_e == 0:
    raise ValueError("Chosen symbol has zero energy; pick another.")
  count = max(1, (delta + sym_e - 1) // sym_e)
  new_text = text + (symbol * count)
  new_total, new_dr = string_energy(new_text, principle)
  # Adjust if overshoot; ensure we hit target
  if new_dr != target:
    # Try up to 20 adjustments by adding one symbol until matched
    tries = 0
    while new_dr != target and tries < 20:
      new_text += symbol
      new_total, new_dr = string_energy(new_text, principle)
      tries += 1
  return new_text, new_total, new_dr, count


def synthesize_sigil(text: str, principle: Principle, style: str = "grid") -> str:
  total, dr = string_energy(text, principle)
  prof = energy_profile(text, principle)
  if style == "grid":
    # Build a 3x3 grid where each cell repeats count of that energy
    order = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    cells = ["" for _ in range(9)]
    for i, k in enumerate(order):
      cells[i] = str(prof[k])
    rows = [" ".join(cells[i:i+3]) for i in range(0, 9, 3)]
    title = f"DR={dr} TOTAL={total}"
    return title + "\n" + "\n".join(rows)
  if style == "bar":
    bars = []
    for i in range(1, 10):
      k = str(i)
      count = prof[k]
      bars.append(f"{i}: " + ("#" * min(count, 40)))
    return "\n".join(bars)
  return f"DR={dr} TOTAL={total}"
