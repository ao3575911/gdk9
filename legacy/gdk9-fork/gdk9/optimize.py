from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .energy import digital_root, string_energy, char_energy
from .principles import Principle


@dataclass
class Plan:
  method: str
  target: int
  steps: List[Tuple[str, int]]  # (symbol, count)
  total_before: int
  dr_before: int
  total_after: int
  dr_after: int


def _residue(n: int) -> int:
  return n % 9


def _target_residue(total: int, target: int) -> int:
  cur_r = _residue(total)
  tgt_r = target % 9  # 9 -> 0
  return (tgt_r - cur_r) % 9


def _allowed_residues(allowed: List[Tuple[str, int]]) -> Dict[int, List[str]]:
  by_res: Dict[int, List[str]] = {i: [] for i in range(9)}
  for s, e in allowed:
    r = e % 9
    by_res[r].append(s)
  return by_res


def minimal_residue_combo(delta_res: int, allowed: List[Tuple[str, int]], max_steps: int = 64) -> Optional[List[int]]:
  # BFS on residues 0..8; each step adds one symbol residue
  residues = [e % 9 for _, e in allowed]
  if delta_res == 0:
    return []
  # If all residues are 0 we cannot change the residue
  if all(r == 0 for r in residues):
    return None
  parent = {0: (-1, -1)}  # residue -> (prev_residue, symbol_index)
  q = deque([0])
  depth = {0: 0}
  while q:
    cur = q.popleft()
    d = depth[cur]
    if d >= max_steps:
      continue
    for idx, r in enumerate(residues):
      nxt = (cur + r) % 9
      if nxt not in parent:
        parent[nxt] = (cur, idx)
        depth[nxt] = d + 1
        if nxt == delta_res:
          # reconstruct path of indices
          seq: List[int] = []
          at = nxt
          while at != 0:
            prev, i = parent[at]
            seq.append(i)
            at = prev
          seq.reverse()
          return seq
        q.append(nxt)
  return None


def build_steps_from_seq(seq: List[int], allowed: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
  counts: Dict[int, int] = {}
  for i in seq:
    counts[i] = counts.get(i, 0) + 1
  steps: List[Tuple[str, int]] = []
  for i, (sym, _e) in enumerate(allowed):
    if i in counts:
      steps.append((sym, counts[i]))
  return steps


def optimize_attunement(
  text: str,
  target: int,
  principle: Principle,
  allowed_symbols: Optional[str] = None,
  method: str = "append",
  max_steps: int = 64,
) -> Plan:
  total, dr = string_energy(text, principle)
  if not (1 <= target <= 9):
    raise ValueError("Target energy must be 1..9")
  if dr == target:
    return Plan(method, target, [], total, dr, total, dr)
  # Determine allowed symbol energies
  if not allowed_symbols:
    allowed_symbols = ".!?,*+"  # sensible defaults with varied residues
  allowed: List[Tuple[str, int]] = []
  for s in allowed_symbols:
    e = char_energy(s, principle)
    if e == 0:
      continue
    allowed.append((s, e))
  if not allowed:
    raise ValueError("No valid allowed symbols; provide a non-empty set.")
  delta_res = _target_residue(total, target)
  seq = minimal_residue_combo(delta_res, allowed, max_steps=max_steps)
  if seq is None:
    raise ValueError("No feasible combination to reach target with given symbols.")
  steps = build_steps_from_seq(seq, allowed)
  added = sum(count * char_energy(sym, principle) for sym, count in steps)
  new_total = total + added
  new_dr = digital_root(new_total, principle.normalize_zero_to_nine)
  return Plan(method, target, steps, total, dr, new_total, new_dr)


def apply_plan(text: str, plan: Plan, spread: Optional[int] = None) -> str:
  if not plan.steps:
    return text
  if plan.method == "append":
    suffix = "".join(sym * count for sym, count in plan.steps)
    return text + suffix
  if plan.method == "prepend":
    prefix = "".join(sym * count for sym, count in plan.steps)
    return prefix + text
  if plan.method == "intersperse":
    # Spread symbols approximately evenly through text
    chars = list(text)
    inserts: List[str] = []
    for sym, count in plan.steps:
      inserts.extend([sym] * count)
    if not chars:
      return "".join(inserts)
    n = len(inserts)
    if n == 0:
      return text
    interval = spread or max(1, len(chars) // (n + 1))
    out: List[str] = []
    i_ins = 0
    for i, ch in enumerate(chars):
      out.append(ch)
      if (i + 1) % interval == 0 and i_ins < n:
        out.append(inserts[i_ins])
        i_ins += 1
    while i_ins < n:
      out.append(inserts[i_ins])
      i_ins += 1
    return "".join(out)
  raise ValueError(f"Unsupported method: {plan.method}")


@dataclass
class EditOp:
  kind: str  # 'sub', 'del', 'ins'
  pos: int
  ch: Optional[str] = None
  count: int = 1


@dataclass
class EditPlan:
  method: str  # 'substitute' or 'edit'
  target: int
  ops: List[EditOp]
  total_before: int
  dr_before: int
  total_after: int
  dr_after: int


def apply_edit_plan(text: str, plan: EditPlan) -> str:
  if not plan.ops:
    return text
  chars = list(text)
  # Apply deletions first from highest pos to lowest
  dels = [op for op in plan.ops if op.kind == 'del']
  for op in sorted(dels, key=lambda o: o.pos, reverse=True):
    if 0 <= op.pos < len(chars):
      del chars[op.pos]
  # Apply substitutions
  subs = [op for op in plan.ops if op.kind == 'sub']
  for op in subs:
    if 0 <= op.pos < len(chars) and op.ch is not None:
      chars[op.pos] = op.ch
  # Apply insertions from lowest pos to highest
  ins = [op for op in plan.ops if op.kind == 'ins']
  for op in sorted(ins, key=lambda o: o.pos):
    insert_str = (op.ch or '') * max(1, op.count)
    if 0 <= op.pos <= len(chars):
      left = ''.join(chars[:op.pos])
      right = ''.join(chars[op.pos:])
      chars = list(left + insert_str + right)
  return ''.join(chars)


def optimize_substitution(
  text: str,
  target: int,
  principle: Principle,
  subs: Optional[Dict[str, List[str]]] = None,
  allow_delete: bool = False,
  allowed_inserts: Optional[str] = None,
  max_edits: int = 8,
) -> EditPlan:
  total, dr = string_energy(text, principle)
  if not (1 <= target <= 9):
    raise ValueError("Target energy must be 1..9")
  if dr == target:
    return EditPlan('substitute', target, [], total, dr, total, dr)

  # Build per-position residue deltas for substitutions (and deletions)
  n = len(text)
  pos_deltas: List[List[Tuple[int, Optional[str]]]] = [[] for _ in range(n)]
  for i, ch in enumerate(text):
    cur_e = char_energy(ch, principle)
    seen: Dict[int, str] = {}
    # substitution options
    if subs and ch in subs:
      for repl in subs[ch]:
        new_e = char_energy(repl, principle)
        r = (new_e - cur_e) % 9
        if r not in seen:
          seen[r] = repl
    # trivial case-change option for letters
    if ch.isalpha():
      alt = ch.swapcase()
      if alt != ch:
        new_e = char_energy(alt, principle)
        r = (new_e - cur_e) % 9
        if r not in seen:
          seen[r] = alt
    for r, repl in seen.items():
      if r != 0:  # ignore no-ops
        pos_deltas[i].append((r, repl))
    # deletion option
    if allow_delete:
      rdel = (-cur_e) % 9
      if rdel != 0:
        pos_deltas[i].append((rdel, None))

  delta_res = _target_residue(total, target)
  # DP over residues with minimal edits, tracking choices
  # state: residue -> (count, prev_residue, (pos, r, repl))
  best: Dict[int, Tuple[int, int, Tuple[int, int, Optional[str]]]] = {0: (0, -1, (-1, 0, None))}
  frontier = [0]
  for i in range(n):
    new_best = best.copy()
    for res, (cnt, prev, info) in best.items():
      for r, repl in pos_deltas[i]:
        nr = (res + r) % 9
        nc = cnt + 1
        if nc > max_edits:
          continue
        if nr not in new_best or nc < new_best[nr][0]:
          new_best[nr] = (nc, res, (i, r, repl))
    best = new_best

  if delta_res not in best:
    # Try insertion-only fallback using symbol residues
    if allowed_inserts:
      append_plan = optimize_attunement(text, target, principle, allowed_symbols=allowed_inserts, method='append')
      ops: List[EditOp] = []
      for sym, cnt in append_plan.steps:
        ops.append(EditOp('ins', len(text), sym, cnt))
      out = apply_edit_plan(text, EditPlan('edit', target, ops, total, dr, total, dr))
      new_total, new_dr = string_energy(out, principle)
      return EditPlan('edit', target, ops, total, dr, new_total, new_dr)
    raise ValueError("No feasible substitution/deletion plan to reach target.")

  # Reconstruct
  ops: List[EditOp] = []
  cur = delta_res
  while cur != 0:
    cnt, prev, (pos, r, repl) = best[cur]
    if pos >= 0:
      if repl is None:
        ops.append(EditOp('del', pos))
      else:
        ops.append(EditOp('sub', pos, repl))
    cur = prev
  # Apply and compute totals
  out = apply_edit_plan(text, EditPlan('edit', target, list(reversed(ops)), total, dr, total, dr))
  new_total, new_dr = string_energy(out, principle)
  return EditPlan('edit', target, list(reversed(ops)), total, dr, new_total, new_dr)
