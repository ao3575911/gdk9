"""Example 10 — Conserved search vs naive name-join (research move 3).

Prints a short JSON summary. Full fail bar lives in pytest::

    python -m pytest -q tests/experiment/test_conserve_vs_naive.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gdk9.kernel import Expression, ImplicationEngine, KernelPrinciple
from gdk9.kernel.engine import fusion_rule
from gdk9.kernel.symbol import Symbol
from tests.experiment.test_conserve_vs_naive import (
  MISMATCHED_AB_ENERGY,
  conserved_kernel_proof,
  naive_join_search,
)


def main() -> int:
  principle = KernelPrinciple.default()
  source = Expression.from_names(["A", "B"], principle)
  conserved_target = Expression((Symbol("AB", source.total_energy()),))
  mismatched = Expression((Symbol("AB", MISMATCHED_AB_ENERGY),))
  engine = ImplicationEngine(principle, (fusion_rule(),))

  conserved_path = conserved_kernel_proof(engine, source, conserved_target, max_depth=2)
  mismatch_kernel = conserved_kernel_proof(engine, source, mismatched, max_depth=2)
  naive_ok = naive_join_search(source.names(), ("AB",), max_depth=2)

  summary = {
    "experiment": "conserve_vs_naive",
    "approach": "A",
    "claim": "beats naive join on proof validity under conservation",
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
    "validity_beat": naive_ok is not None and mismatch_kernel is None,
  }
  print(json.dumps(summary, indent=2))
  return 0 if summary["validity_beat"] and summary["conserved_ab"]["kernel_found"] else 1


if __name__ == "__main__":
  raise SystemExit(main())