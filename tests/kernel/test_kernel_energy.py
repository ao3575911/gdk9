from gdk9.kernel import Expression, ImplicationEngine, KernelPrinciple


def test_kernel_evaluates_text_with_default_principle():
  principle = KernelPrinciple.default()
  expr = Expression.from_text("ABC", principle)
  total, root = ImplicationEngine(principle).evaluate(expr)

  assert total == 6
  assert root == 6


def test_expression_names_and_text_are_stable():
  principle = KernelPrinciple.default()
  expr = Expression.from_names(["A", "B", "C"], principle)

  assert expr.names() == ("A", "B", "C")
  assert expr.text() == "ABC"
