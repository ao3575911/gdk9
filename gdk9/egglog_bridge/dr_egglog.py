"""Encode ONE GDk9 digital-root rewrite suite into egglog-python.

Suite (from gdk9.energy.digital_root + additive energy totals):
  R1  Energy(a) + Energy(b)  ->  Energy(a + b)          (const-fold sum)
  R2  Energy(a)  | a>0, a%9==0  ->  Energy.root(9)     (subsume)
  R3  Energy(a)  | a>0, a%9!=0  ->  Energy.root(a%9)   (subsume)
  R4  Energy(0)  ->  Energy.root(9)                      (zero_to_nine)

Saturation is two-phase so unbounded integer growth cannot explode the e-graph
(equating DR-equivalent integers while still adding would diverge).
"""
from __future__ import annotations

from typing import List, Sequence

from egglog import (
    EGraph,
    Expr,
    eq,
    i64,
    i64Like,
    ne,
    rewrite,
    ruleset,
    vars_,
)


class Energy(Expr):
    def __init__(self, value: i64Like) -> None: ...

    def __add__(self, other: Energy) -> Energy: ...

    @classmethod
    def root(cls, value: i64Like) -> Energy:
        """Collapsed digital-root form (preferred extract)."""
        ...


def build_dr_rules():
    a, b = vars_("a b", i64)
    rs_sum = ruleset(
        rewrite(Energy(a) + Energy(b)).to(Energy(a + b)),
    )
    rs_dr = ruleset(
        rewrite(Energy(a), subsume=True).to(
            Energy.root(9),
            a > 0,
            eq(a % 9).to(i64(0)),
        ),
        rewrite(Energy(a), subsume=True).to(
            Energy.root(a % 9),
            a > 0,
            ne(a % 9).to(i64(0)),
        ),
        rewrite(Energy(0), subsume=True).to(Energy.root(9)),
    )
    return rs_sum, rs_dr


def _parse_root(extracted: object) -> int | None:
    text = str(extracted)
    # Energy.root(N)
    if "root(" in text:
        inner = text.split("root(", 1)[1].rstrip(")")
        try:
            return int(inner)
        except ValueError:
            return None
    # Energy(N) fallback
    if text.startswith("Energy(") and text.endswith(")"):
        try:
            return int(text[len("Energy(") : -1])
        except ValueError:
            return None
    return None


def saturate_egglog(values: Sequence[int], sum_iters: int = 8, dr_iters: int = 8) -> dict:
    vals = [int(v) for v in values]
    if not vals:
        raise ValueError("need at least one value")

    egraph = EGraph()
    rs_sum, rs_dr = build_dr_rules()

    expr = Energy(vals[0])
    for v in vals[1:]:
        expr = expr + Energy(v)
    named = egraph.let("fixture", expr)

    before = egraph.extract(named)
    egraph.run(rs_sum * sum_iters)
    after_sum = egraph.extract(named)
    egraph.run(rs_dr * dr_iters)
    after_dr = egraph.extract(named)
    best = _parse_root(after_dr)

    return {
        "engine": "egglog",
        "inputs": vals,
        "before": str(before),
        "after_sum": str(after_sum),
        "after_dr": str(after_dr),
        "best_dr": best,
        "ok": best is not None and 1 <= best <= 9,
    }
