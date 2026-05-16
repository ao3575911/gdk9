import pytest

from gdk9.kernel import Expression, ImplicationEngine, KernelPrinciple
from gdk9.kernel.engine import fusion_rule, split_rule
from gdk9.kernel.errors import ConservationError
from gdk9.kernel.rule import ImplicationRule, RuleKind
from gdk9.kernel.symbol import Symbol


def test_fusion_rule_conserves_energy():
  principle = KernelPrinciple.default()
  expr = Expression.from_names(["A", "B"], principle)
  engine = ImplicationEngine(principle, (fusion_rule(),))

  judgment = engine.apply("fuse", expr)

  assert judgment.conserved is True
  assert judgment.after.names() == ("AB",)
  assert judgment.after.total_energy() == expr.total_energy()


def test_split_rule_conserves_energy_when_outputs_match_input():
  principle = KernelPrinciple.default()
  expr = Expression((Symbol("AB", 3.0),))
  engine = ImplicationEngine(principle, (split_rule(("A", "B"), (1.0, 2.0)),))

  judgment = engine.apply("split", expr)

  assert judgment.conserved is True
  assert judgment.after.names() == ("A", "B")
  assert judgment.delta == 0


def test_engine_rejects_non_conserving_rewrite():
  principle = KernelPrinciple.default()
  expr = Expression.from_names(["A"], principle)
  rule = ImplicationRule(
    "inflate",
    RuleKind.REWRITE,
    lambda _expr: Expression((Symbol("X", 99.0),)),
  )
  engine = ImplicationEngine(principle, (rule,))

  with pytest.raises(ConservationError):
    engine.apply("inflate", expr)


def test_infer_returns_trace_to_target():
  principle = KernelPrinciple.default()
  source = Expression.from_names(["A", "B"], principle)
  target = Expression((Symbol("AB", 3.0),))
  engine = ImplicationEngine(principle, (fusion_rule(),))

  path = engine.infer(source, target, max_depth=2)

  assert path is not None
  assert [step.judgment.rule for step in path] == ["fuse"]
  assert path[-1].judgment.after.names() == ("AB",)
