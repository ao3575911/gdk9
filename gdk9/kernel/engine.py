from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from .errors import ConservationError, ImplicationError
from .expression import Expression
from .principle import KernelPrinciple
from .proof import Judgment, ProofStep
from .rule import ImplicationRule, RuleKind
from .symbol import Symbol


@dataclass
class ImplicationEngine:
  """Pure symbolic implication engine."""

  principle: KernelPrinciple = field(default_factory=KernelPrinciple.default)
  rules: tuple[ImplicationRule, ...] = ()

  def evaluate(self, expression: Expression) -> tuple[float, int]:
    total = expression.total_energy()
    return total, expression.digital_root(self.principle)

  def judge(self, rule: ImplicationRule, expression: Expression) -> Judgment:
    before_total = expression.total_energy()
    after = rule.apply(expression)
    after_total = after.total_energy()
    delta = after_total - before_total
    conserved = abs(delta) <= rule.tolerance
    if rule.preserves_energy and not conserved:
      raise ConservationError(
        f"Rule '{rule.name}' changed energy by {delta:.12g}"
      )
    return Judgment(rule.name, expression, after, conserved, delta)

  def apply(self, rule_name: str, expression: Expression) -> Judgment:
    for rule in self.rules:
      if rule.name == rule_name:
        return self.judge(rule, expression)
    raise ImplicationError(f"Unknown rule: {rule_name}")

  def normalize(self, expression: Expression, max_steps: int = 64) -> list[ProofStep]:
    """Apply the first valid rule repeatedly until no rule changes the expression."""
    steps: list[ProofStep] = []
    current = expression
    seen = {current.names()}
    for index in range(max_steps):
      for rule in self.rules:
        try:
          judgment = self.judge(rule, current)
        except ImplicationError:
          continue
        if judgment.after.names() == current.names():
          continue
        if judgment.after.names() in seen:
          return steps
        step = ProofStep(judgment, index)
        steps.append(step)
        current = judgment.after
        seen.add(current.names())
        break
      else:
        return steps
    return steps

  def infer(
    self,
    source: Expression,
    target: Expression,
    max_depth: int = 4,
  ) -> list[ProofStep] | None:
    """Find a bounded implication path from source to target."""
    if source.names() == target.names():
      return []
    queue: deque[tuple[Expression, list[ProofStep]]] = deque([(source, [])])
    seen = {source.names()}
    while queue:
      current, path = queue.popleft()
      if len(path) >= max_depth:
        continue
      for rule in self.rules:
        try:
          judgment = self.judge(rule, current)
        except (ConservationError, ImplicationError):
          continue
        names = judgment.after.names()
        if names in seen:
          continue
        next_path = [*path, ProofStep(judgment, len(path))]
        if names == target.names():
          return next_path
        seen.add(names)
        queue.append((judgment.after, next_path))
    return None


def fusion_rule(name: str = "fuse") -> ImplicationRule:
  def transform(expression: Expression) -> Expression:
    if len(expression) < 2:
      raise ImplicationError("Fusion requires at least two symbols")
    fused_name = "".join(expression.names())
    return Expression((Symbol(fused_name, expression.total_energy()),))

  return ImplicationRule(name, RuleKind.FUSION, transform, reversible=True)


def split_rule(
  parts: tuple[str, ...],
  energies: tuple[float, ...],
  name: str = "split",
) -> ImplicationRule:
  if len(parts) != len(energies):
    raise ValueError("Split parts and energies must have the same length")
  if not parts:
    raise ValueError("Split requires at least one output part")

  def transform(expression: Expression) -> Expression:
    if len(expression) != 1:
      raise ImplicationError("Split requires exactly one input symbol")
    return Expression(tuple(Symbol(part, energy) for part, energy in zip(parts, energies)))

  return ImplicationRule(name, RuleKind.SPLIT, transform, reversible=True)
