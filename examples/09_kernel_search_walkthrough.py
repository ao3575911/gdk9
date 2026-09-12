"""Example 09 — Kernel search walkthrough (handbook voice).

Three short scenes. Each conserves energy. Each can fail if the depth bound
is too tight or the target energy does not match — that failure is the point.

Run::

    python examples/09_kernel_search_walkthrough.py

Or mirror with the CLI::

    gdk9 kernel eval A B C
    gdk9 kernel apply fuse A B
    gdk9 kernel search A B --target AB --max-depth 2 --rules fuse
    gdk9 kernel apply split AB --parts A,B --energies 1,2
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gdk9.kernel import Expression, ImplicationEngine
from gdk9.kernel.engine import fusion_rule, split_rule
from gdk9.kernel.symbol import Symbol
from gdk9.kernel_cli import (
  judgment_payload,
  principle_to_kernel,
  proof_steps_payload,
)
from gdk9.principles import Principle


def scene(title: str, payload: dict) -> None:
  print(f"\n## {title}")
  print(json.dumps(payload, indent=2, ensure_ascii=False))


def main() -> int:
  kp = principle_to_kernel(Principle.default())
  fuse = fusion_rule()
  a_e = Expression.from_names(["A"], kp).total_energy()
  b_e = Expression.from_names(["B"], kp).total_energy()
  split = split_rule(("A", "B"), (a_e, b_e))

  # Scene 1 — weigh the letters (eval)
  eng = ImplicationEngine(kp, (fuse,))
  abc = Expression.from_names(["A", "B", "C"], kp)
  total, root = eng.evaluate(abc)
  scene(
    "1. Weigh — eval ABC",
    {
      "names": list(abc.names()),
      "total_energy": total,
      "digital_root": root,
      "note": "A=1, B=2, C=3 under the default principle; sum=6, DR=6.",
    },
  )

  # Scene 2 — one conserved fuse, then find it by bounded search
  src = Expression.from_names(["A", "B"], kp)
  judgment = eng.apply("fuse", src)
  target = Expression((Symbol("AB", src.total_energy()),))
  path = eng.infer(src, target, max_depth=2)
  scene(
    "2. Fuse — then search A,B → AB (max_depth=2)",
    {
      "apply": judgment_payload(judgment),
      "search_found": path is not None,
      "steps": proof_steps_payload(path or ()),
      "note": "Search is not magic: it is bounded BFS over conserving rules.",
    },
  )

  # Scene 3 — reverse the arrow (split) with matching energies
  eng2 = ImplicationEngine(kp, (fuse, split))
  ab = judgment.after
  back = eng2.apply("split", ab)
  scene(
    "3. Split — AB → A,B with matching energies (conserved)",
    {
      "judgment": judgment_payload(back),
      "note": "Split needs explicit part energies that sum to the whole.",
    },
  )

  # Scene 4 — deliberate miss (prove it can fail)
  miss = eng.infer(src, Expression((Symbol("ZZ", 99.0),)), max_depth=2)
  scene(
    "4. Miss — impossible target (energy 99) within depth 2",
    {
      "found": miss is not None,
      "note": "A honest research tool must be able to say no.",
    },
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())