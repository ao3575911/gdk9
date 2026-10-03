"""Example 07 — Python API: use gdk9 modules directly.

All CLI commands are thin wrappers around importable Python functions.
This example exercises the core API without subprocess.
"""
import sys, os
# Allow running from the examples/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gdk9.energy import string_energy
from gdk9.dcg import (
    get_dcg, symmetry_class, sym_energy,
    homotopy_equivalent,
)
from gdk9.fmt import Box, section
from gdk9.principles import Principle

principle = Principle.default()

# ── Energy model ──────────────────────────────────────────────────────────────
print(section("energy model", enabled=False))

for word in ["FWEM", "dark", "swan"]:
    total, dr = string_energy(word, principle)
    print(f'  {word:<10}  total={total:>6}  dr={dr}')

# ── DCG ───────────────────────────────────────────────────────────────────────
print()
print(section("dcg", enabled=False))

g = get_dcg()
print(f'  nodes={g.node_count()}  edges={g.edge_count()}')

for ch in "FWEM":
    cls = symmetry_class(ch)
    e   = sym_energy(ch)
    print(f'  {ch}  {cls:<12}  e={e:.4f}')

print()
path = g.shortest_path("F", "M")
print(f'  shortest F→M:  {" → ".join(path)}')

equiv, detail = homotopy_equivalent("FWEM", "MWEF", tol=1.0)
print(f'  homotopy FWEM≅MWEF:  {equiv}  '
      f'(Δe={detail["energy_diff"]:.4f}  dist={detail["vector_distance"]:.4f})')

# ── fmt helpers ───────────────────────────────────────────────────────────────
print()
print(section("fmt — Box table", enabled=False))

box = Box(["char", "class", "energy", "dr"], col_align=["c", "l", "r", "c"], enabled=False)
for ch in "FWEM":
    e   = sym_energy(ch)
    cls = symmetry_class(ch)
    _, dr = string_energy(ch, principle)
    box.row([ch, cls, f"{e:.4f}", str(dr)])
print(box.render())
