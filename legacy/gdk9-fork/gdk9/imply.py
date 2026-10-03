from __future__ import annotations

import math
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Tuple

from .errors import InputError


NAME_RE = re.compile(r"^[A-Z][A-Za-z0-9_]*$")


@dataclass
class Rule:
  name: str
  type: str  # 'fusion' or 'split'
  arity: int
  params: Dict[str, Any]

  def to_json(self) -> Dict[str, Any]:
    return asdict(self)


def validate_symbol_name(name: str) -> None:
  if not NAME_RE.match(name):
    raise InputError(f"Invalid symbol name: {name}")


def make_fusion(rule_name: str, out_name: str, arity: int) -> Rule:
  if arity < 2:
    raise InputError("Fusion arity must be >= 2")
  return Rule(name=rule_name, type="fusion", arity=arity, params={"out": out_name})


def make_split(rule_name: str, out_a: str, out_b: str, ratio: float) -> Rule:
  if not (0.0 <= ratio <= 1.0):
    raise InputError("Split ratio must be between 0 and 1")
  return Rule(name=rule_name, type="split", arity=1, params={"out_a": out_a, "out_b": out_b, "ratio": float(ratio)})


def apply_rule(rule: Rule, symbols: Dict[str, float], inputs: List[str], tol: float = 1e-9) -> Dict[str, Any]:
  if rule.type == "fusion":
    if len(inputs) < rule.arity:
      raise InputError(f"Rule '{rule.name}' requires at least {rule.arity} inputs")
    energies = []
    for name in inputs:
      if name not in symbols:
        raise InputError(f"Unknown symbol: {name}")
      energies.append(float(symbols[name]))
    total = sum(energies)
    out_name = rule.params.get("out", "AUTO")
    if out_name.upper() == "AUTO":
      out_name = "".join(inputs)
    validate_symbol_name(out_name)
    outputs = [{"name": out_name, "energy": total}]
    if abs(sum(energies) - sum(o["energy"] for o in outputs)) > tol:
      raise InputError("Conservation failed in fusion")
    return {"inputs": list(zip(inputs, energies)), "outputs": outputs}

  if rule.type == "split":
    if len(inputs) != 1:
      raise InputError(f"Rule '{rule.name}' requires exactly 1 input")
    name = inputs[0]
    if name not in symbols:
      raise InputError(f"Unknown symbol: {name}")
    ein = float(symbols[name])
    ratio = float(rule.params.get("ratio", 0.5))
    out_a = str(rule.params.get("out_a", "OUT_A"))
    out_b = str(rule.params.get("out_b", "OUT_B"))
    validate_symbol_name(out_a)
    validate_symbol_name(out_b)
    ea = ein * ratio
    eb = ein * (1.0 - ratio)
    if not math.isfinite(ea) or not math.isfinite(eb):
      raise InputError("Non-finite energies in split")
    if abs(ein - (ea + eb)) > tol:
      raise InputError("Conservation failed in split")
    outputs = [{"name": out_a, "energy": ea}, {"name": out_b, "energy": eb}]
    return {"inputs": [(name, ein)], "outputs": outputs}

  raise InputError(f"Unsupported rule type: {rule.type}")

