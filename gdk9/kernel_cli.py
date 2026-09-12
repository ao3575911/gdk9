"""Thin CLI/API adapter for the pure implication kernel.

Lives outside ``gdk9.kernel`` so the kernel package stays free of CLI, state,
plugin, crypto, TUI, and terminal-formatting imports.
"""

from __future__ import annotations

import json
from typing import Any, Sequence

from gdk9.errors import InputError
from gdk9.kernel import Expression, ImplicationEngine, KernelPrinciple
from gdk9.kernel.engine import fusion_rule, split_rule
from gdk9.kernel.errors import ConservationError, ImplicationError, KernelError
from gdk9.kernel.proof import Judgment, ProofStep
from gdk9.kernel.rule import ImplicationRule
from gdk9.principles import Principle


def principle_to_kernel(principle: Principle) -> KernelPrinciple:
  """Adapt a GDk9 ``Principle`` into an immutable ``KernelPrinciple``."""
  return KernelPrinciple(
    name=principle.name,
    symbol_energy=dict(principle.symbol_energy),
    source=principle,
    normalize_zero_to_nine=principle.normalize_zero_to_nine,
  )


def expression_payload(expression: Expression) -> dict[str, Any]:
  return {
    "names": list(expression.names()),
    "text": expression.text(),
    "total_energy": expression.total_energy(),
    "symbols": [
      {"name": symbol.name, "energy": symbol.energy} for symbol in expression.symbols
    ],
  }


def judgment_payload(judgment: Judgment) -> dict[str, Any]:
  return {
    "rule": judgment.rule,
    "before": expression_payload(judgment.before),
    "after": expression_payload(judgment.after),
    "conserved": judgment.conserved,
    "delta": judgment.delta,
  }


def proof_steps_payload(steps: Sequence[ProofStep]) -> list[dict[str, Any]]:
  return [
    {"index": step.index, "judgment": judgment_payload(step.judgment)} for step in steps
  ]


def _parse_float_list(raw: str, label: str) -> tuple[float, ...]:
  parts = [p.strip() for p in raw.split(",") if p.strip()]
  if not parts:
    raise InputError(f"{label} must list at least one value")
  try:
    return tuple(float(p) for p in parts)
  except ValueError as exc:
    raise InputError(f"Invalid {label}: {raw}") from exc


def _parse_name_list(raw: str, label: str) -> tuple[str, ...]:
  parts = [p.strip() for p in raw.split(",") if p.strip()]
  if not parts:
    raise InputError(f"{label} must list at least one symbol name")
  return tuple(parts)


def builtin_rules(
  names: Sequence[str],
  *,
  split_parts: tuple[str, ...] | None = None,
  split_energies: tuple[float, ...] | None = None,
) -> tuple[ImplicationRule, ...]:
  """Build the small set of demo rules used by the kernel smoke path."""
  rules: list[ImplicationRule] = []
  for name in names:
    key = name.strip().lower()
    if key in {"fuse", "fusion"}:
      rules.append(fusion_rule(name="fuse"))
    elif key == "split":
      if not split_parts or not split_energies:
        raise InputError("split requires --parts and --energies")
      rules.append(split_rule(split_parts, split_energies, name="split"))
    else:
      raise InputError(f"Unknown builtin kernel rule: {name}")
  return tuple(rules)


def _print_json(payload: dict[str, Any]) -> int:
  print(json.dumps(payload, indent=2, ensure_ascii=False))
  return 0


def cmd_kernel_eval(args: Any, principle: Principle) -> int:
  kp = principle_to_kernel(principle)
  expr = Expression.from_text(args.text, kp)
  total, root = ImplicationEngine(kp).evaluate(expr)
  return _print_json(
    {
      "ok": True,
      "cmd": "eval",
      "expression": expression_payload(expr),
      "total": total,
      "digital_root": root,
      "principle": kp.name,
    }
  )


def cmd_kernel_apply(args: Any, principle: Principle) -> int:
  kp = principle_to_kernel(principle)
  names = tuple(args.symbols)
  if not names:
    raise InputError("apply requires at least one symbol name")
  expr = Expression.from_names(names, kp)
  split_parts = _parse_name_list(args.parts, "parts") if getattr(args, "parts", None) else None
  split_energies = (
    _parse_float_list(args.energies, "energies") if getattr(args, "energies", None) else None
  )
  rules = builtin_rules(
    [args.rule],
    split_parts=split_parts,
    split_energies=split_energies,
  )
  engine = ImplicationEngine(kp, rules)
  try:
    judgment = engine.apply(rules[0].name, expr)
  except KernelError as exc:
    return _print_json({"ok": False, "cmd": "apply", "error": str(exc)})
  return _print_json(
    {
      "ok": True,
      "cmd": "apply",
      "judgment": judgment_payload(judgment),
      "principle": kp.name,
    }
  )


def cmd_kernel_search(args: Any, principle: Principle) -> int:
  kp = principle_to_kernel(principle)
  source_names = tuple(args.source)
  target_names = tuple(args.target)
  if not source_names or not target_names:
    raise InputError("search requires --source and --target symbol names")
  source = Expression.from_names(source_names, kp)
  target = Expression.from_names(target_names, kp)
  rule_names = list(args.rules) if getattr(args, "rules", None) else ["fuse"]
  split_parts = _parse_name_list(args.parts, "parts") if getattr(args, "parts", None) else None
  split_energies = (
    _parse_float_list(args.energies, "energies") if getattr(args, "energies", None) else None
  )
  rules = builtin_rules(
    rule_names,
    split_parts=split_parts,
    split_energies=split_energies,
  )
  engine = ImplicationEngine(kp, rules)
  max_depth = int(getattr(args, "max_depth", 4))
  path = engine.infer(source, target, max_depth=max_depth)
  return _print_json(
    {
      "ok": path is not None,
      "cmd": "search",
      "found": path is not None,
      "max_depth": max_depth,
      "source": expression_payload(source),
      "target": expression_payload(target),
      "rules": [rule.name for rule in rules],
      "steps": proof_steps_payload(path or ()),
      "principle": kp.name,
    }
  )


def run_kernel(args: Any, principle: Principle) -> int:
  """Dispatch ``gdk9 kernel …`` subcommands."""
  cmd = getattr(args, "kernel_cmd", None)
  try:
    if cmd == "eval":
      return cmd_kernel_eval(args, principle)
    if cmd == "apply":
      return cmd_kernel_apply(args, principle)
    if cmd == "search":
      return cmd_kernel_search(args, principle)
  except (ConservationError, ImplicationError) as exc:
    return _print_json({"ok": False, "cmd": cmd, "error": str(exc)})
  raise InputError(f"Unknown kernel subcommand: {cmd}")
