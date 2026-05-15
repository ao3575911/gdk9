# gdk9-alphabet

Lightweight character embedding framework using the GDk9 hollow-vector model. Maps any character to a 3-element numeric vector — normalised code point, glyph hole count, and alphabetic flag — then aggregates across strings for analysis, comparison, and ML integration.

```bash
python demo.py "Hello World!"
# Character vectors:
#   'H' -> [0.573, 0.0, 1.0]
#   'o' -> [0.610, 1.0, 1.0]   # 'o' has one enclosed loop
# Mean vector: [0.5886, 0.4167, 0.8333]
# String value (magnitude): 1.1203
```

## Concept

The **GDk9 hollow vector** captures three features per character:

| Dimension | Description | Example |
|-----------|-------------|---------|
| Normalised code point | `unicode(ch) / 127`, clamped to ASCII range | `A` → 0.504 |
| Hole count | Enclosed loops in the glyph | `B`=2, `A`=1, `C`=0 |
| Alpha flag | `1.0` if letter, `0.0` otherwise | `5` → 0.0 |

These simple features preserve structural character properties while remaining fully numeric — making them directly usable in clustering, anomaly detection, and classification pipelines.

## Install

```bash
git clone https://github.com/ao3575911/gdk9-alphabet.git
cd gdk9-alphabet
python demo.py "Example"
```

Requires Python ≥ 3.11. Zero external dependencies.

## Usage

### Character vector

```python
from gdk9_alphabet import get_char_vector

get_char_vector("A")   # [0.504, 1.0, 1.0]  — code, 1 hole, is alpha
get_char_vector("B")   # [0.511, 2.0, 1.0]  — 2 holes
get_char_vector("5")   # [0.417, 0.0, 0.0]  — digit, no holes
```

### String vector and scalar value

```python
from vector_ops import string_vector, string_value

vec = string_vector("Hello")    # component-wise mean across all chars
val = string_value("Hello")     # Euclidean magnitude — scalar metric

# Compare strings
string_value("AAAA") < string_value("BBBB")   # quantitative ordering
```

### Directed character graph (DCG)

```python
from dcg import build_dcg, format_dcg

graph = build_dcg("LOLLOL")
print(format_dcg(graph))
# L -> O (2)
# O -> L (2)
# L -> L (1)
```

The DCG captures transition patterns: edge weight = number of consecutive occurrences. Useful for sequence analysis, Markov models, and visualisation.

## Module reference

| File | Contents |
|------|---------|
| `gdk9_alphabet.py` | `SUPPORTED_CHARACTERS` mapping + `get_char_vector(ch)` |
| `vector_ops.py` | `string_vector(text)`, `string_value(text)` |
| `dcg.py` | `build_dcg(text)`, `format_dcg(graph)` |
| `demo.py` | CLI demo — pass any string as argument |

## Extending the framework

- **Custom alphabets** — update `SUPPORTED_CHARACTERS` with hole counts for your symbol set
- **Additional features** — add stroke counts, phonetic properties, or frequency statistics
- **Graph analytics** — feed the DCG into networkx for PageRank, centrality, shortest-path
- **ML pipelines** — use `string_vector` outputs as feature vectors for classifiers

## License

MIT — © 2025 Adam Grange
