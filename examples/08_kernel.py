"""Example 08 — Pure kernel smoke: evaluate, fuse, and bounded search.

The kernel package has no CLI/state/plugin I/O. This script uses the library
surface (and optionally the thin ``gdk9 kernel`` CLI adapter) for research.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gdk9.kernel import Expression, ImplicationEngine, KernelPrinciple
from gdk9.kernel.engine import fusion_rule
from gdk9.kernel.symbol import Symbol
from gdk9.kernel_cli import expression_payload, judgment_payload, proof_steps_payload, principle_to_kernel
from gdk9.principles import Principle

principle = Principle.default()
kp = principle_to_kernel(principle)
engine = ImplicationEngine(kp, (fusion_rule(),))

# Evaluate
expr = Expression.from_text("ABC", kp)
total, root = engine.evaluate(expr)
print(json.dumps({"eval": {"expression": expression_payload(expr), "total": total, "digital_root": root}}, indent=2))

# Apply fuse
source = Expression.from_names(["A", "B"], kp)
judgment = engine.apply("fuse", source)
print(json.dumps({"apply": judgment_payload(judgment)}, indent=2))

# Bounded search A,B -> AB
target = Expression((Symbol("AB", source.total_energy()),))
path = engine.infer(source, target, max_depth=2)
print(json.dumps({"search": {"found": path is not None, "steps": proof_steps_payload(path or ())}}, indent=2))
