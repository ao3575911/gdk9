"""Experiment: conserved kernel search vs naive name-join/split baseline.

Pytest IS the experiment. See docs/EXPERIMENT_CONSERVE_SEARCH.md.
"""
from __future__ import annotations

from collections import deque
from typing import Sequence

from gdk9.kernel import Expression, ImplicationEngine, KernelPrinciple, ProofStep
from gdk9.kernel.engine import fusion_rule, split_rule
from gdk9.kernel.symbol import Symbol

TOL = 1e-9
# Documented energy-mismatched target energy (not equal to A+B under default principle).
MISMATCHED_AB_ENERGY = 99.0
# Documented mismatched part energies for split target A,B (sum != conserved AB).
MISMATCHED_A_ENERGY = 50.0
MISMATCHED_B_ENERGY = 50.0


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


def naive_split_search(
  source_names: Sequence[str],
  target_names: Sequence[str],
  max_depth: int = 2,
) -> list[tuple[str, ...]] | None:
  """Bounded BFS: split = cut one name into two contiguous parts; ignore energy."""
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
    for i, name in enumerate(current):
      if len(name) < 2:
        continue
      for cut in range(1, len(name)):
        nxt = current[:i] + (name[:cut], name[cut:]) + current[i + 1 :]
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


def test_kernel_split_ab_within_depth_2_conserves():
  """Move 4: find AB→A,B with split_rule; every step conserved with |delta|≤1e-9."""
  principle = KernelPrinciple.default()
  ea = principle.energy_of("A")
  eb = principle.energy_of("B")
  source = Expression((Symbol("AB", ea + eb),))
  target = Expression.from_names(["A", "B"], principle)
  engine = ImplicationEngine(principle, (split_rule(("A", "B"), (ea, eb)),))

  path = conserved_kernel_proof(engine, source, target, max_depth=2)
  assert path is not None, "kernel must find AB → A,B with split within max_depth=2"
  assert len(path) <= 2
  for step in path:
    j = step.judgment
    assert j.conserved is True
    assert abs(j.delta) <= TOL
  assert path[-1].judgment.after.names() == ("A", "B")
  assert abs(path[-1].judgment.after.total_energy() - source.total_energy()) <= TOL


def test_kernel_fuse_split_round_trip_conserves():
  """Move 4: A,B —fuse→ AB —split→ A,B round-trips with conserved energy."""
  principle = KernelPrinciple.default()
  ea = principle.energy_of("A")
  eb = principle.energy_of("B")
  source = Expression.from_names(["A", "B"], principle)
  engine = ImplicationEngine(
    principle,
    (fusion_rule(), split_rule(("A", "B"), (ea, eb))),
  )

  fuse_j = engine.apply("fuse", source)
  assert fuse_j.conserved is True
  assert abs(fuse_j.delta) <= TOL
  assert fuse_j.after.names() == ("AB",)

  split_j = engine.apply("split", fuse_j.after)
  assert split_j.conserved is True
  assert abs(split_j.delta) <= TOL
  assert split_j.after.names() == ("A", "B")
  assert abs(split_j.after.total_energy() - source.total_energy()) <= TOL
  assert [s.energy for s in split_j.after] == [ea, eb]


def test_naive_accepts_energy_mismatched_split_kernel_rejects():
  """Move 4 fail bar (new beat): naive finds A,B by name split; kernel rejects wrong energy.

  Theatre check: ``infer`` matches names only, so a path to names A,B exists even when the
  declared target energies are 50+50. If ``conserved_kernel_proof`` dropped the final-energy
  gate, this test would FAIL (kernel would wrongly return a conserved-looking path). That
  is the documented non-theatre fail case for move 4.
  """
  principle = KernelPrinciple.default()
  ea = principle.energy_of("A")
  eb = principle.energy_of("B")
  source = Expression((Symbol("AB", ea + eb),))
  mismatched = Expression(
    (Symbol("A", MISMATCHED_A_ENERGY), Symbol("B", MISMATCHED_B_ENERGY))
  )
  assert abs(mismatched.total_energy() - source.total_energy()) > TOL

  engine = ImplicationEngine(principle, (split_rule(("A", "B"), (ea, eb)),))

  naive = naive_split_search(source.names(), mismatched.names(), max_depth=2)
  assert naive is not None, "naive split must accept A,B by name sequence alone"

  # Name-only infer would succeed; conserved proof must still reject.
  name_only = engine.infer(source, mismatched, max_depth=2)
  assert name_only is not None, "setup: infer must reach A,B by names (load-bearing)"

  kernel_path = conserved_kernel_proof(engine, source, mismatched, max_depth=2)
  assert kernel_path is None, (
    "kernel must reject energy-mismatched A,B split target (validity beat, not speed)"
  )
