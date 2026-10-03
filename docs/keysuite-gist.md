# KeySuite

Reference runtime for **GDk9** 1.1.0. Local web console. No model in the core.

| | |
|---|---|
| Product | KeySuite |
| Standard | GDk9 1.1.0 |
| Algebra | `reduce_buffer` only — first-bind split, U+2192, optional `mode(core)` wrap |
| Receipt | ρ(B, μ) exists only at COMMIT |
| Grammar | `grammar/gdk9-v1.1.0.yaml` |
| SHA-256 | `0c8974e76427799dc62ac6839057c8fff41d3ad7ae29c3e6c9d070dd9df1b7a7` |

Canonical vector:

```
tokens:  C C . 3 3 SPACE
receipt: CC→33
```

MODE+BIND is out of scope. Session is the only caller of ρ.

Source: https://github.com/ao3575911/keysuite
