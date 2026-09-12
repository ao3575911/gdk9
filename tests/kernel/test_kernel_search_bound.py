from gdk9.kernel import Expression, ImplicationEngine, KernelPrinciple
from gdk9.kernel.engine import fusion_rule, split_rule
from gdk9.kernel.symbol import Symbol


def test_infer_respects_max_depth_bound():
  principle = KernelPrinciple.default()
  # A,B -> AB needs depth 1; depth 0 must fail closed.
  source = Expression.from_names(["A", "B"], principle)
  target = Expression((Symbol("AB", source.total_energy()),))
  engine = ImplicationEngine(principle, (fusion_rule(),))

  assert engine.infer(source, target, max_depth=0) is None
  assert engine.infer(source, target, max_depth=1) is not None


def test_fuse_then_split_conserves_energy():
  principle = KernelPrinciple.default()
  source = Expression.from_names(["A", "B"], principle)
  total = source.total_energy()
  fuse = fusion_rule()
  # Split the fused symbol back into equal-named parts with matching energies.
  energies = (source.symbols[0].energy, source.symbols[1].energy)
  split = split_rule(("A", "B"), energies)
  engine = ImplicationEngine(principle, (fuse, split))

  fused = engine.apply("fuse", source)
  assert fused.conserved is True
  assert abs(fused.after.total_energy() - total) <= 1e-9

  split_j = engine.apply("split", fused.after)
  assert split_j.conserved is True
  assert abs(split_j.after.total_energy() - total) <= 1e-9
  assert split_j.after.names() == ("A", "B")
