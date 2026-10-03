#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDk9 Core Engine — Unified Symbolic & Regression Framework
Author: Adam Grange (@sniprsec)
Version: 3.1
License: MIT
Date: October 09, 2025

Description:
    Unifies the GDk9 symbolic cognitive category system and regression engine.
    Models alphanumeric and symbolic characters as algebraic-cognitive operators.
    Provides regression tools for energy-mass-base relationships.
    
    Optimizations:
    - Precompute lambdified functions for efficiency.
    - Robust error handling for numerical stability and dependency issues.
    - Non-interactive matplotlib backend for server environments.
    - Refined lowercase classification for AC/DC duality.
    - Logging with stack traces for debugging.
    - Graph visualization optimized with caching and default file saving.
"""

import string
import numpy as np
import sympy as sp
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from dataclasses import dataclass
from sklearn.metrics import mean_squared_error
import logging
import traceback
from functools import lru_cache

# Check dependencies
try:
    import numpy, sympy, networkx, matplotlib, sklearn
except ImportError as e:
    print(f"Error: Missing required library: {e}")
    print("Please install dependencies: pip install numpy sympy networkx matplotlib scikit-learn")
    exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    """
    Classify a symbol based on GDk9 symmetry properties.
    Lowercase inherits from uppercase with AC adaptation.
    """
    idempotent_upper = set("AHIMOTUVWXY")
    biphasic_upper = set("BCDEK")
    involutive_upper = set("NSZ")
    asymmetric_upper = set("FGJLPQR")

    if ch.isupper():
        if ch in idempotent_upper:
            s, eq, cog = "idempotent", "x² = x", "stabilizer"
        elif ch in biphasic_upper:
            s, eq, cog = "biphasic", "x² = f(x)", "oscillator"
        elif ch in involutive_upper:
            s, eq, cog = "involutive", "x² = 1", "flip"
        elif ch in asymmetric_upper:
            s, eq, cog = "asymmetric", "x² ≠ x,1", "driver"
        else:
            s, eq, cog = "undefined", "x² = ?", "unknown"
    elif ch.islower():
        upper_entity = classify_symbol(ch.upper())
        s = f"alternating_{upper_entity.symmetry_type}"
        eq = upper_entity.equation.replace('x', 'x(t)')
        cog = f"AC_{upper_entity.cognitive_class}"
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
        "alternating_idempotent": "fluid self-similar archetype",
        "alternating_biphasic": "fluid dual-phase connector",
        "alternating_involutive": "fluid reversal state",
        "alternating_asymmetric": "fluid directional transformation",
        "alternating_undefined": "fluid unclassified pattern",
        "quantized": "discrete quantum value",
        "operator": "meta-symbolic instruction",
        "undefined": "unclassified pattern"
    }

    meaning = meanings.get(s, "unknown meaning")
    return SymbolicEntity(ch, s, cog, eq, meaning)


class GDk9Category:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_entity(self, entity: SymbolicEntity):
        self.graph.add_node(entity.symbol, data=entity)

    def add_morphism(self, src, tgt, label):
        if src in self.graph and tgt in self.graph:
            self.graph.add_edge(src, tgt, label=label)
        else:
            logger.warning(f"Cannot add morphism {src} -> {tgt}: Source or target not in graph.")

    def compose(self, path):
        if not path:
            return ""
        for node in path:
            if node not in self.graph:
                logger.error(f"Node {node} not in graph for composition.")
                return ""
        return " ∘ ".join(f"{a}->{b}" for a, b in zip(path[:-1], path[1:]))

    @lru_cache(maxsize=1)
    def _compute_layout(self, subnodes):
        return nx.spring_layout(self.graph.subgraph(subnodes), seed=42)

    def visualize(self, title="GDk9 Cognitive Category", limit=50, save_path="gdk9_graph.png"):
        try:
            plt.figure(figsize=(10, 10))
            subnodes = list(self.graph.nodes)[:limit]
            pos = self._compute_layout(tuple(subnodes))  # Cache layout
            subgraph = self.graph.subgraph(subnodes)
            nx.draw(subgraph, pos, with_labels=True, node_color="lightblue",
                    node_size=1000, edge_color="black", font_size=8)
            nx.draw_networkx_edge_labels(subgraph, pos,
                                         edge_labels=nx.get_edge_attributes(subgraph, 'label'),
                                         font_size=7)
            plt.title(title)
            plt.savefig(save_path)
            logger.info(f"Graph visualization saved to {save_path}")
            plt.close()
        except Exception as e:
            logger.error(f"Visualization error: {e}\n{traceback.format_exc()}")


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

# Precompute lambdified functions
f_funcs = {}
for name, expr in candidate_forms.items():
    try:
        f_funcs[name] = sp.lambdify(x, expr, 'numpy')
    except Exception as e:
        logger.error(f"Failed to lambdify {name}: {e}\n{traceback.format_exc()}")

def generate_data(mass=2, base_range=(1, 4), constant=3e8**2, noise=0.05, num_points=50):
    try:
        if base_range[0] >= base_range[1] or num_points <= 0:
            raise ValueError("Invalid base_range or num_points")
        x_vals = np.linspace(base_range[0], base_range[1], num_points)
        y_true = mass * constant * (x_vals**2)
        noise_vals = y_true * noise * np.random.randn(len(x_vals))
        return x_vals, y_true + noise_vals
    except Exception as e:
        logger.error(f"Data generation error: {e}\n{traceback.format_exc()}")
        return np.array([]), np.array([])

def evaluate_models(x_vals, y_vals, mass=2, constant=3e8**2):
    scores = {}
    for name, f_func in f_funcs.items():
        try:
            y_pred = mass * constant * f_func(x_vals)
            y_pred = np.clip(y_pred, -1e10, 1e10)  # Prevent overflow
            if np.any(np.isnan(y_pred)) or np.any(np.isinf(y_pred)):
                raise ValueError("NaN or Inf in predictions")
            scores[name] = mean_squared_error(y_vals, y_pred)
        except Exception as e:
            logger.warning(f"Error evaluating {name}: {e}")
            scores[name] = float('inf')
    return dict(sorted(scores.items(), key=lambda kv: kv[1] if kv[1] != float('inf') else float('inf')))

def best_fit(x_vals, y_vals):
    results = evaluate_models(x_vals, y_vals)
    valid_results = {k: v for k, v in results.items() if v != float('inf')}
    if not valid_results:
        logger.error("No valid models found")
        return None, results
    best = min(valid_results, key=valid_results.get)
    return best, results

def plot_fits(x_vals, y_vals, mass=2, constant=3e8**2, top_n=3, save_path="gdk9_fits.png"):
    try:
        ranked = evaluate_models(x_vals, y_vals)
        top = [k for k, v in ranked.items() if v != float('inf')][:top_n]
        if not top:
            raise ValueError("No valid models to plot")
        plt.figure(figsize=(9, 6))
        plt.scatter(x_vals, y_vals, color='black', label='True Data')
        for form in top:
            f_func = f_funcs[form]
            y_pred = np.clip(mass * constant * f_func(x_vals), -1e10, 1e10)
            plt.plot(x_vals, y_pred, label=f"{form} fit")
        plt.title("GDk9 Symbolic Regression: Top Models")
        plt.legend()
        plt.grid(True)
        plt.savefig(save_path)
        logger.info(f"Plot saved to {save_path}")
        plt.close()
    except Exception as e:
        logger.error(f"Plotting error: {e}\n{traceback.format_exc()}")

# ============================================================
# 3. MAIN EXECUTION
# ============================================================

if __name__ == '__main__':
    logger.info("Initializing GDk9 Core Engine...")
    try:
        category = build_gdk9_field()
        logger.info(f"Loaded {len(category.graph.nodes)} symbols, {len(category.graph.edges)} morphisms.")
        print("Composite Path:", category.compose(['A', 'V', 'W', 'M']))

        z_val, k_val = 2, 3e8**2
        x_vals, y_vals = generate_data(mass=z_val, constant=k_val)
        if len(x_vals) == 0:
            logger.error("Data generation failed. Check inputs or logs.")
            print("Error: Failed to generate data. Check logs for details.")
            exit(1)

        best, results = best_fit(x_vals, y_vals)
        if best is None:
            logger.error("No valid regression models. Check candidate functions.")
            print("Error: No valid regression models found.")
            exit(1)
        print(f"\nBest f(x): {candidate_forms[best]}\n")
        for name, err in results.items():
            print(f"{name:12s} -> MSE: {err:.3e}")

        plot_fits(x_vals, y_vals, top_n=3, save_path="gdk9_fits.png")
        # category.visualize(save_path="gdk9_graph.png")
    except Exception as e:
        logger.error(f"Main execution error: {e}\n{traceback.format_exc()}")
        print(f"Error: Execution failed. Check logs for details.")
        exit(1)