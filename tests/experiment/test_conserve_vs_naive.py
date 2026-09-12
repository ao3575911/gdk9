"""Experiment: conserved kernel search vs naive name-join baseline.

Pytest IS the experiment. See docs/EXPERIMENT_CONSERVE_SEARCH.md.
"""
from __future__ import annotations

from collections import deque
from typing import Sequence

from gdk9.kernel import Expression, ImplicationEngine, KernelPrinciple, ProofStep
from gdk9.kernel.engine import fusion_rule
from gdk9.kernel.symbol import Symbol

TOL = 1e-9
# Documented energy-mismatched target energy (not equal to A+B under default principle).
MISMATCHED_AB_ENERGY = 99.0


def naive_join_search(
  source_names: Sequence[str],
  target_names: Sequence[str],
  max_depth: int = 2,
) -> list[tuple[str, ...]] | None:
  """Bounded BFS: fuse = join adjacent names; ignore energy entirely."""
  start = tuple(source_names)
  goal = tuple(target_names)
  if start == goal:
    return []
  queue: deque[tuple[tuple[str, ...], list[tuple[str, ...]]]] = deque([(start, [])])
  seen = {start}
  while queue:
    current, path = queue.popleft()
    if len(path) >= max_depth:
      continue
    for i in range(len(current) - 1):
      joined = current[i] + current[i + 1]
      nxt = current[:i] + (joined,) + current[i + 2 :]
      if nxt in seen:
        continue
      next_path = [*path, nxt]
      if nxt == goal:
        return next_path
      seen.add(nxt)
      queue.append((nxt, next_path))
  return None


def conserved_kernel_proof(
  engine: ImplicationEngine,
  source: Expression,
  target: Expression,
  max_depth: int = 2,
) -> list[ProofStep] | None:
  """infer + conservation + final energy agreement with the declared target."""
  path = engine.infer(source, target, max_depth=max_depth)
  if path is None:
    return None
  for step in path:
    j = step.judgment
    if j.conserved is False or abs(j.delta) > TOL:
      return None
  final = path[-1].judgment.after if path else source
  if abs(final.total_energy() - target.total_energy()) > TOL:
    return None
  return path


def test_kernel_fuse_ab_within_depth_2_conserves():
  """Fail bar 2 + 1: find A,B→AB and every step conserved with |delta|≤1e-9."""
  principle = KernelPrinciple.default()
  source = Expression.from_names(["A", "B"], principle)
  target = Expression((Symbol("AB", source.total_energy()),))
  engine = ImplicationEngine(principle, (fusion_rule(),))

  path = conserved_kernel_proof(engine, source, target, max_depth=2)
  assert path is not None, "kernel must find A,B → AB with fuse within max_depth=2"
  assert len(path) <= 2
  for step in path:
    j = step.judgment
    assert j.conserved is True
    assert abs(j.delta) <= TOL
  assert path[-1].judgment.after.names() == ("AB",)
  assert abs(path[-1].judgment.after.total_energy() - source.total_energy()) <= TOL


def test_naive_accepts_energy_mismatched_ab_kernel_rejects():
  """Fail bar 3: naive finds mismatched AB; kernel returns no valid proof."""
  principle = KernelPrinciple.default()
  source = Expression.from_names(["A", "B"], principle)
  assert abs(source.total_energy() - MISMATCHED_AB_ENERGY) > TOL

  mismatched = Expression((Symbol("AB", MISMATCHED_AB_ENERGY),))
  engine = ImplicationEngine(principle, (fusion_rule(),))

  naive = naive_join_search(source.names(), mismatched.names(), max_depth=2)
  assert naive is not None, "naive join must accept AB by name sequence alone"

  kernel_path = conserved_kernel_proof(engine, source, mismatched, max_depth=2)
  assert kernel_path is None, (
    "kernel must reject energy-mismatched AB (validity beat, not speed)"
  )


def test_naive_also_finds_conserved_ab_by_names():
  """Sanity: naive join finds the same name path when energy happens to match."""
  principle = KernelPrinciple.default()
  source = Expression.from_names(["A", "B"], principle)
  target_names = ("AB",)
  assert naive_join_search(source.names(), target_names, max_depth=2) is not None