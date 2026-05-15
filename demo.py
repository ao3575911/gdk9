"""
demo.py
=======

This script demonstrates the use of the GDk9 alphabet framework for
character analysis.  Given a string of text, it performs the following
operations:

* Computes the hollow vector for each individual character and prints
  these vectors.
* Aggregates the string into a mean hollow vector and computes a
  scalar value representing the "magnitude" of that vector.
* Constructs a directed character graph (DCG) that records the
  transitions between adjacent characters.
* Prints a formatted representation of the DCG.

Run this script directly with a string argument or provide input
interactively when prompted.  For example:

```
python demo.py "Hello World!"
```
"""
from __future__ import annotations

import sys
from typing import List

from gdk9_alphabet import get_char_vector
from vector_ops import string_vector, string_value
from dcg import build_dcg, format_dcg


def _print_char_vectors(text: str) -> None:
    print("Character vectors:")
    for ch in text:
        vec = get_char_vector(ch)
        print(f"  '{ch}' -> {vec}")


def main(args: List[str]) -> None:
    if args:
        input_text = " ".join(args)
    else:
        input_text = input("Enter text: ")
    # Compute and display character vectors
    _print_char_vectors(input_text)
    # Compute and display string vector and value
    vec = string_vector(input_text)
    value = string_value(input_text)
    print(f"\nMean vector: {vec}")
    print(f"String value (magnitude): {value:.4f}\n")
    # Build and display DCG
    graph = build_dcg(input_text)
    if graph:
        print("Directed Character Graph:")
        print(format_dcg(graph))
    else:
        print("Directed Character Graph: (empty)")


if __name__ == "__main__":
    main(sys.argv[1:])