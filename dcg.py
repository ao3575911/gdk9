"""
dcg.py
======

This module constructs a **directed character graph (DCG)** from text.

The concept of a DCG here is deliberately simple: every distinct
character in the input text becomes a node, and a directed edge from
character ``a`` to character ``b`` is created for every occurrence of
``a`` immediately followed by ``b`` in the text.  Edges carry integer
weights equal to the number of observed transitions.

This representation captures local sequencing information – it records
which characters tend to precede others and with what frequency.  Such
graphs can be used to analyse patterns, detect anomalies or drive
generative models.

Functions provided in this module build the graph and offer simple
interfaces for inspecting and exporting it.
"""
from __future__ import annotations

from typing import Dict, Tuple

__all__ = ["build_dcg", "format_dcg"]


def build_dcg(text: str) -> Dict[str, Dict[str, int]]:
    """Construct a directed character graph from the input text.

    Parameters
    ----------
    text : str
        The input string.  Adjacent pairs of characters define the
        directed edges of the graph.  If the string has length ``n``
        then ``n - 1`` transitions will be considered.

    Returns
    -------
    Dict[str, Dict[str, int]]
        A nested mapping ``graph[u][v]`` giving the weight of the edge
        from ``u`` to ``v``.  If no edge exists, the inner dictionary
        will not contain the corresponding key.
    """
    graph: Dict[str, Dict[str, int]] = {}
    if len(text) < 2:
        return graph
    # Iterate over adjacent character pairs
    for i in range(len(text) - 1):
        u, v = text[i], text[i + 1]
        if u not in graph:
            graph[u] = {}
        if v not in graph[u]:
            graph[u][v] = 0
        graph[u][v] += 1
    return graph


def format_dcg(graph: Dict[str, Dict[str, int]]) -> str:
    """Return a string representation of the directed character graph.

    The output lists each node and its outgoing edges in a readable
    format.  For example:

    ```
    A -> B (3), C (1)
    B -> A (2)
    ...
    ```

    Parameters
    ----------
    graph : Dict[str, Dict[str, int]]
        The adjacency mapping produced by :func:`build_dcg`.

    Returns
    -------
    str
        A human‑readable representation of the graph.
    """
    lines = []
    for u, targets in graph.items():
        parts = [f"{v} ({w})" for v, w in targets.items()]
        line = f"{u} -> " + ", ".join(parts)
        lines.append(line)
    return "\n".join(lines)