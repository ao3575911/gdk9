"""
vector_ops.py
==============

This module provides helper functions for working with **hollow vectors** at
the sequence level.  While ``gdk9_alphabet`` defines a mapping for
individual characters, the functions in this file handle entire strings
by aggregating per‑character vectors.

Key functionality includes:

* Computing a mean vector representation for an arbitrary string.
* Calculating a scalar *value* for a string based on the magnitude of its
  mean vector.  This value can be interpreted as a rough measure of
  complexity or "information content" in the sense of this toy system.

The design is intentionally simple.  More sophisticated schemes (e.g.,
weighted sums, convolutional embeddings, or neural encoders) could be
substituted if the application demands it.
"""
from __future__ import annotations

import math
from typing import Iterable, List

from gdk9_alphabet import get_char_vector

__all__ = ["string_vector", "string_value"]


def string_vector(text: str) -> List[float]:
    """Return the mean hollow vector for the given string.

    The hollow vector for each character is computed via
    ``gdk9_alphabet.get_char_vector``.  The resulting sequence of vectors
    is averaged component‑wise.  An empty string yields a zero vector.

    Parameters
    ----------
    text : str
        The string to embed.  Unicode characters outside the supported
        range contribute a zero vector.

    Returns
    -------
    List[float]
        A three‑element list representing the mean vector.
    """
    if not text:
        return [0.0, 0.0, 0.0]
    vectors: List[List[float]] = [get_char_vector(ch) for ch in text]
    length = len(vectors)
    # Compute component‑wise sum
    sum_components = [0.0, 0.0, 0.0]
    for vec in vectors:
        sum_components[0] += vec[0]
        sum_components[1] += vec[1]
        sum_components[2] += vec[2]
    # Compute mean
    return [c / length for c in sum_components]


def string_value(text: str) -> float:
    """Compute a scalar value for the given string.

    The value is defined as the Euclidean (L2) norm of the mean hollow
    vector returned by :func:`string_vector`.  Intuitively, this
    aggregates the contributions of the normalised code point, hole
    count and alphabetic indicator into a single non‑negative number.

    Parameters
    ----------
    text : str
        The input string.  An empty string yields ``0.0``.

    Returns
    -------
    float
        The magnitude of the mean hollow vector.
    """
    vec = string_vector(text)
    return math.sqrt(sum(component * component for component in vec))