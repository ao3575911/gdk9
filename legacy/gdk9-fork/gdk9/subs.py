from __future__ import annotations

import json
from typing import Dict, List

from .principles import Principle
from .energy import char_energy, digital_root


ALL_LETTERS = [chr(c) for c in range(ord('A'), ord('Z') + 1)] + [chr(c) for c in range(ord('a'), ord('z') + 1)]
ALL_DIGITS = [str(i) for i in range(0, 10)]


def _build_energy_bins(pr: Principle) -> Dict[int, List[str]]:
  bins: Dict[int, List[str]] = {i: [] for i in range(1, 10)}
  for sym in pr.symbol_energy.keys():
    e = char_energy(sym, pr)
    bins[e].append(sym)
  # Ensure some diversity by sorting
  for k in bins:
    bins[k] = sorted(set(bins[k]))
  return bins


def generate_subs(principle: Principle, limit: int = 3, include_digits: bool = True) -> Dict[str, List[str]]:
  subs: Dict[str, List[str]] = {}
  bins = _build_energy_bins(principle)
  # helper to choose candidates by same energy then triad neighbors
  def candidates_for_energy(e: int) -> List[str]:
    same = list(bins.get(e, []))
    if len(same) >= limit:
      return same[:limit]
    # triad groups
    r = e % 9
    triad = []
    if r in (1, 4, 7):
      triad = [4, 7, 1]
    elif r in (2, 5, 8):
      triad = [5, 8, 2]
    else:
      triad = [6, 9, 3]
    out = same
    for t in triad:
      for s in bins.get(t, []):
        if s not in out:
          out.append(s)
        if len(out) >= limit:
          return out[:limit]
    return out[:limit]

  # Build for letters
  for ch in ALL_LETTERS:
    e = char_energy(ch, principle)
    cands = candidates_for_energy(e)
    if include_digits:
      # add digits that match energy
      for d in ALL_DIGITS:
        if char_energy(d, principle) == e and d not in cands:
          cands.append(d)
        if len(cands) >= limit:
          break
    if cands:
      subs[ch] = cands[:limit]

  # Build for digits
  for ch in ALL_DIGITS:
    e = char_energy(ch, principle)
    cands = candidates_for_energy(e)
    if cands:
      subs[ch] = cands[:limit]

  # Include common symbols mapping to alternatives (neighbors in bins)
  for e, sym_list in bins.items():
    for ch in sym_list:
      # pick neighbors by rotating list to add variety
      alts = [s for s in sym_list if s != ch][:limit]
      if alts:
        subs[ch] = alts

  return subs


def generate_allowed_inserts(principle: Principle) -> str:
  # Cover all residues 0..8 using available symbols
  bins = _build_energy_bins(principle)
  chosen: List[str] = []
  seen_residues = set()
  # Map energy to residue (9 -> 0)
  for e in range(1, 10):
    res = e % 9
    if res in seen_residues:
      continue
    syms = bins.get(e, [])
    if syms:
      chosen.append(syms[0])
      seen_residues.add(res)
    if len(seen_residues) == 9:
      break
  return "".join(chosen)


def build_subs_json(principle: Principle, limit: int = 3) -> str:
  data = {
    "subs": generate_subs(principle, limit=limit),
    "allowed_inserts": generate_allowed_inserts(principle),
  }
  return json.dumps(data, ensure_ascii=False, indent=2)

