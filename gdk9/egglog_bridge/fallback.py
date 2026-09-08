"""Legacy GDk9 digital-root rewriter (kept as fallback)."""
from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from gdk9.energy import digital_root


def collapse_totals(values: Sequence[int], zero_to_nine: bool = True) -> Tuple[int, int]:
    """Sum values then digital-root (classic GDk9 path)."""
    total = sum(int(v) for v in values)
    return total, digital_root(total, zero_to_nine=zero_to_nine)


def collapse_each_then_sum(values: Sequence[int], zero_to_nine: bool = True) -> Tuple[List[int], int]:
    """DR each term, sum, DR again — congruence check path."""
    folded = [digital_root(int(v), zero_to_nine=zero_to_nine) for v in values]
    _total, dr = collapse_totals(folded, zero_to_nine=zero_to_nine)
    return folded, dr


def saturate_fallback(values: Iterable[int]) -> dict:
    vals = [int(v) for v in values]
    total, dr_direct = collapse_totals(vals)
    folded, dr_via = collapse_each_then_sum(vals)
    return {
        "engine": "gdk9.energy.digital_root (fallback)",
        "inputs": vals,
        "total": total,
        "folded_terms": folded,
        "best_dr": dr_direct,
        "congruence_dr": dr_via,
        "ok": dr_direct == dr_via,
    }
