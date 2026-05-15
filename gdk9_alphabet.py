"""
gdk9_alphabet.py
=================

This module defines a simple representation of the **GDk9 Alphabet**.  In the
context of this project the ``GDk9`` alphabet is an abstraction over the
Latin letters (A–Z), digits (0–9) and a handful of punctuation characters.

Each supported character is assigned a small **hollow vector**.  A hollow
vector is a fixed‑length list of numeric features describing basic
properties of the character.  The current implementation uses three
dimensions:

1. **Normalized ASCII code** – the raw Unicode code point scaled to the range
   ``[0.0, 1.0]``.  This preserves ordering information while keeping the
   magnitude bounded.
2. **Hole count** – an integer count of closed loops or “holes” present in
   the typical glyph shape.  For example, ``A`` and ``D`` each have one
   enclosed space, ``B`` has two, and ``C`` has none.  This feature is
   inspired by letter classification puzzles and provides a simple
   measure of geometric complexity.
3. **Alpha flag** – a binary indicator that is ``1.0`` if the character is
   alphabetic (a letter) and ``0.0`` otherwise.  This feature helps
   differentiate letters from digits or punctuation.

The combination of these dimensions forms a minimal yet informative
representation suitable for simple vector arithmetic and string
embedding tasks.

The mapping defined here is not exhaustive; unsupported characters
default to zero vectors.  Additional features or characters can be
added as needed.
"""

from typing import Dict, List

__all__ = ["SUPPORTED_CHARACTERS", "get_char_vector"]

# Map of uppercase characters to their hole counts.  Lowercase letters
# inherit the same value.  The counts reflect the number of closed loops
# inside typical sans‑serif glyphs.
_hole_counts: Dict[str, int] = {
    "A": 1, "B": 2, "C": 0, "D": 1, "E": 0, "F": 0, "G": 0, "H": 0,
    "I": 0, "J": 0, "K": 0, "L": 0, "M": 0, "N": 0, "O": 1, "P": 1,
    "Q": 1, "R": 1, "S": 0, "T": 0, "U": 0, "V": 0, "W": 0, "X": 0,
    "Y": 0, "Z": 0,
}

# Digits mapped to approximate hole counts based on common digital display
# fonts.  Note that the count for ``4`` varies by style; here it is
# treated as having one enclosed space to differentiate it from other
# linear digits.
_digit_hole_counts: Dict[str, int] = {
    "0": 1, "1": 0, "2": 0, "3": 0, "4": 1, "5": 0, "6": 1,
    "7": 0, "8": 2, "9": 1,
}

# Aggregate supported characters by merging letters, digits and a small
# subset of punctuation.  Punctuation characters have zero holes and are
# not considered alphabetic.
SUPPORTED_CHARACTERS: Dict[str, int] = {}
for letter, count in _hole_counts.items():
    SUPPORTED_CHARACTERS[letter] = count
    SUPPORTED_CHARACTERS[letter.lower()] = count
for digit, count in _digit_hole_counts.items():
    SUPPORTED_CHARACTERS[digit] = count

# Add punctuation and special symbols with zero holes.
for symbol in [" ", ",", ".", "!", "?", "-", "_", ":", ";", "'", "\"", "(", ")", "[", "]", "{", "}", "@", "#", "$", "%", "&", "*", "+", "="]:
    SUPPORTED_CHARACTERS[symbol] = 0


def get_char_vector(ch: str) -> List[float]:
    """Return a 3‑element hollow vector for a single character.

    The vector components are ordered as follows:

    1. ``normalized_ascii`` – the Unicode code point of the character
       divided by 127.  If the code point exceeds 127 (i.e. non‑ASCII
       characters), it is clamped at 127 to keep the value within
       ``[0.0, 1.0]``.
    2. ``hole_count`` – the number of closed loops contained within the
       glyph, as defined in the ``SUPPORTED_CHARACTERS`` mapping.  Unknown
       characters default to ``0``.
    3. ``alpha_flag`` – ``1.0`` if the character is alphabetic and
       ``0.0`` otherwise.

    Parameters
    ----------
    ch : str
        The character to convert.  If more than one code point is
        provided, only the first is considered.

    Returns
    -------
    List[float]
        A list of three numeric features representing the character.
    """
    if not ch:
        return [0.0, 0.0, 0.0]
    # Use the first code point only
    code_point = ord(ch[0])
    # Clamp to 127 to normalise
    capped = min(code_point, 127)
    normalized_ascii = capped / 127.0
    # Determine hole count and alpha flag
    hole_count = SUPPORTED_CHARACTERS.get(ch[0], 0)
    # For unsupported unicode characters, treat holes as zero
    alpha_flag = 1.0 if ch[0].isalpha() else 0.0
    return [normalized_ascii, float(hole_count), alpha_flag]