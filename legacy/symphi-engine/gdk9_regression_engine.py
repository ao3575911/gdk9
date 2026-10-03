#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDk9 Core Engine — Unified Symbolic & Regression Framework
Author: Adam Grange (@beathovn)
Version: 3.0
License: MIT

Description:
    The GDk9 Core Engine unifies the symbolic cognitive category system and
    the symbolic regression engine. It models all alphanumeric and symbolic
    characters as algebraic-cognitive operators, and provides regression tools
    for energy-mass-base relationships within the GDk9 framework.
"""

import string
import numpy as np
import sympy as sp
import networkx as nx
import matplotlib.pyplot as plt
from dataclasses import dataclass
from sklearn.metrics import mean_squared_error

# ============================================================
# 1. SYMBOLIC COGNITIVE MODEL
# ============================================================

@dataclass
class SymbolicEntity:
    symbol: str
    symmetry_type: str
    cognitive_class: str
    equation: str
    meaning: str

    def __repr__(self):
        return f"{self.symbol}<{self.symmetry_type}:{self.cognitive_class}>"


def classify_symbol(ch: str) -> SymbolicEntity:
    idempotent_upper = set("AHIMOTUVWXY")
    biphasic_upper = set("BCDEK")
    involutive_upper = set("NSZ")
    asymmetric_upper = set("FGJLPQR")

    if ch in idempotent_upper:
        s, eq, cog = "idempotent", "x² = x", "stabilizer"
    elif ch in biphasic_upper:
        s, eq, cog = "biphasic", "x² = f(x)", "oscillator"
    elif ch in involutive_upper:
        s, eq, cog = "involutive", "x² = 1", "flip"
    elif ch in asymmetric_upper:
        s, eq, cog = "asymmetric", "x² ≠ x,1", "driver"
    elif ch.islower():
        s, eq, cog = "alternating", "x(t) = sin(t)", "AC dynamic"
    elif ch.isdigit():
        s, eq, cog = "quantized", f"x = {ch}", "numeric field"
    elif ch in string.punctuation:
        s, eq, cog = "operator", f"op({ch})", "meta-symbol"
    else:
        s, eq, cog = "undefined", "x² = ?", "unknown"

    meanings = {
        "idempotent": "self-similar archetype",
        "biphasic": "dual-phase connector",
        "involutive": "reversal state",
        "asymmetric": "directional transformation",
        "alternating": "fluid cognition",
        "quantized": "discrete quantum value",
        "operator": "meta-symbolic instruction",
        "undefined": "unclassified pattern"
    }

    return SymbolicEntity(ch, s, cog, eq, meanings[s])


class GDk9Category:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_entity(self, entity: SymbolicEntity):
        self.graph.add_node(entity.symbol, data=entity)

    def add_morphism(self, src, tgt, label):
        self.graph.add_edge(src, tgt, label=label)

    def compose(self, path):
        return " ∘ ".join(f"{a}->{b}" for a, b in zip(path[:-1], path[1:]))

    def visualize(self, title="GDk9 Cognitive Category", limit=100):
        plt.figure(figsize=(10, 10))
        subnodes = list(self.graph.nodes)[:limit]
        subgraph = self.graph.subgraph(subnodes)
        pos = nx.spring_layout(subgraph, seed=42)
        nx.draw(subgraph, pos, with_labels=True, node_color="white",
                node_size=1000, edge_color="black", font_size=8)
        nx.draw_networkx_edge_labels(subgraph, pos,
                                     edge_labels=nx.get_edge_attributes(subgraph, 'label'),
                                     font_size=7)
        plt.title(title)
        plt.show()


def build_gdk9_field():
    cat = GDk9Category()
    all_chars = list(string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation)

    for ch in all_chars:
        cat.add_entity(classify_symbol(ch))

    morphs = [
        ('A', 'V', 'inversion'),
        ('V', 'W', 'duplication'),
        ('W', 'M', 'integration'),
        ('F', 'E', 'DC→AC'),
        ('E', 'e', 'symbolic alternation'),
        ('1', 'I', 'numeric→identity'),
        ('0', 'O', 'null→wholeness'),
        ('$', 'S', 'value flow'),
        ('@', 'a', 'meta self-ref')
    ]
    for src, tgt, lbl in morphs:
        if src in cat.graph and tgt in cat.graph:
            cat.add_morphism(src, tgt, lbl)

    return cat

# ============================================================
# 2. SYMBOLIC REGRESSION ENGINE
# ============================================================

x, z, k = sp.symbols('x z k', real=True, positive=True)
candidate_forms = {
    "linear": x,
    "quadratic": x**2,
    "cubic": x**3,
    "exponential": sp.exp(x),
    "logarithmic": sp.log(x + 1),
    "sinusoidal": sp.sin(x),
    "reciprocal": 1/(x + 1),
    "hyperbolic": sp.tanh(x),
    "root": sp.sqrt(x),
    "mixed": sp.sin(x) + sp.log(x + 1)
}

def generate_data(mass=2, base_range=(1, 4), constant=3e8**2, noise=0.05):
    x_vals = np.linspace(base_range[0], base_range[1], 50)
    y_true = mass * constant * (x_vals**2)
    return x_vals, y_true + y_true * noise * np.random.randn(len(x_vals))

def evaluate_models(x_vals, y_vals, mass=2, constant=3e8**2):
    scores = {}
    for name, expr in candidate_forms.items():
        f_func = sp.lambdify(x, expr, 'numpy')
        y_pred = mass * constant * f_func(x_vals)
        scores[name] = mean_squared_error(y_vals, y_pred)
    return dict(sorted(scores.items(), key=lambda kv: kv[1]))

def best_fit(x_vals, y_vals):
    results = evaluate_models(x_vals, y_vals)
    best = min(results, key=results.get)
    return best, results

def plot_fits(x_vals, y_vals, mass=2, constant=3e8**2, top_n=3):
    ranked = evaluate_models(x_vals, y_vals)
    top = list(ranked.keys())[:top_n]
    plt.figure(figsize=(9, 6))
    plt.scatter(x_vals, y_vals, color='black', label='True Data')
    for form in top:
        expr = candidate_forms[form]
        f_func = sp.lambdify(x, expr, 'numpy')
        y_pred = mass * constant * f_func(x_vals)
        plt.plot(x_vals, y_pred, label=f"{form} fit")
    plt.title("GDk9 Symbolic Regression: Top Models")
    plt.legend(); plt.grid(True); plt.show()

# ============================================================
# 3. MAIN EXECUTION
# ============================================================

if __name__ == '__main__':
    print("Initializing GDk9 Core Engine...")
    category = build_gdk9_field()
    print(f"Loaded {len(category.graph.nodes)} symbols, {len(category.graph.edges)} morphisms.")
    print("Composite Path:", category.compose(['A', 'V', 'W', 'M']))

    z_val, k_val = 2, 3e8**2
    x_vals, y_vals = generate_data(mass=z_val, constant=k_val)
    best, results = best_fit(x_vals, y_vals)
    print(f"\nBest f(x): {candidate_forms[best]}\n")
    for name, err in results.items():
        print(f"{name:12s} -> MSE: {err:.3e}")

    plot_fits(x_vals, y_vals, top_n=3)
    # category.visualize()  # optional visualization
