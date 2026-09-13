"""Example 10 — Conserved search vs naive name-join/split (research move 4).

Prints a short JSON summary. Full fail bar lives in pytest::

    python -m pytest -q tests/experiment/test_conserve_vs_naive.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gdk9.kernel import Expression, ImplicationEngine, KernelPrinciple
from gdk9.kernel.engine import fusion_rule, split_rule
from gdk9.kernel.symbol import Symbol
from tests.experiment.test_conserve_vs_naive import (
  MISMATCHED_AB_ENERGY,
  MISMATCHED_A_ENERGY,
  MISMATCHED_B_ENERGY,
  conserved_kernel_proof,
  naive_join_search,
  naive_split_search,
)


def main() -> int:
  principle = KernelPrinciple.default()
  ea = principle.energy_of("A")
  eb = principle.energy_of("B")
  source = Expression.from_names(["A", "B"], principle)
  conserved_target = Expression((Symbol("AB", source.total_energy()),))
  mismatched = Expression((Symbol("AB", MISMATCHED_AB_ENERGY),))
  fuse_engine = ImplicationEngine(principle, (fusion_rule(),))

  ab_source = Expression((Symbol("AB", ea + eb),))
  split_target = Expression.from_names(["A", "B"], principle)
  split_mismatched = Expression(
    (Symbol("A", MISMATCHED_A_ENERGY), Symbol("B", MISMATCHED_B_ENERGY))
  )
  split_engine = ImplicationEngine(principle, (split_rule(("A", "B"), (ea, eb)),))

  conserved_path = conserved_kernel_proof(fuse_engine, source, conserved_target, max_depth=2)
  mismatch_kernel = conserved_kernel_proof(fuse_engine, source, mismatched, max_depth=2)
  naive_ok = naive_join_search(source.names(), ("AB",), max_depth=2)

  split_path = conserved_kernel_proof(split_engine, ab_source, split_target, max_depth=2)
  split_mismatch_kernel = conserved_kernel_proof(
    split_engine, ab_source, split_mismatched, max_depth=2
  )
  naive_split_ok = naive_split_search(ab_source.names(), ("A", "B"), max_depth=2)

  summary = {
    "experiment": "conserve_vs_naive",
    "approach": "A",
    "move": 4,
    "claim": "beats naive join/split on proof validity under conservation",
    "source_names": list(source.names()),
    "source_energy": source.total_energy(),
    "conserved_ab": {
      "kernel_found": conserved_path is not None,
      "steps": len(conserved_path or ()),
      "all_conserved": bool(
        conserved_path
        and all(s.judgment.conserved for s in conserved_path)
      ),
    },
    "mismatched_ab_energy": MISMATCHED_AB_ENERGY,
    "mismatched_ab": {
      "naive_found": naive_ok is not None,
      "kernel_found": mismatch_kernel is not None,
    },
    "conserved_split": {
      "kernel_found": split_path is not None,
      "steps": len(split_path or ()),
      "all_conserved": bool(
        split_path and all(s.judgment.conserved for s in split_path)
      ),
    },
    "mismatched_split": {
      "naive_found": naive_split_ok is not None,
      "kernel_found": split_mismatch_kernel is not None,
      "part_energies": [MISMATCHED_A_ENERGY, MISMATCHED_B_ENERGY],
    },
    "validity_beat_fuse": naive_ok is not None and mismatch_kernel is None,
    "validity_beat_split": naive_split_ok is not None and split_mismatch_kernel is None,
  }
  print(json.dumps(summary, indent=2))
  ok = (
    summary["validity_beat_fuse"]
    and summary["validity_beat_split"]
    and summary["conserved_ab"]["kernel_found"]
    and summary["conserved_split"]["kernel_found"]
  )
  return 0 if ok else 1


if __name__ == "__main__":
  raise SystemExit(main())
