# Reduction

ρ(B, μ) is computed only at COMMIT. The JSON envelope is host-level.

Algebra is `reduce_buffer` only: first-bind split, U+2192, optional `mode(core)` wrap.

Product name KeySuite. Standard name GDk9. MODE+BIND is out of scope.

## reduce_buffer

Find the first bind marker in the buffer. A bind marker is the syntax glyph `.` that was not introduced through escape `_`. Escaped `.` is CONTENT and is not a bind marker.

If a bind marker is present at index i:

result = join(buffer[:i]) + "→" + join(buffer[i+1:])

Otherwise:

result = join(buffer)

If μ is set, wrap: μ(result). Otherwise return result.

Empty-side cases are part of the algebra, not extra operators.

## Examples

```
reduce_buffer(["C", "C", ".", "3", "3"]) => CC→33
reduce_buffer(["A", "B"]) => AB
reduce_buffer(["A", ".", "B"]) => A→B
reduce_buffer(["A", ".", "B", ".", "C"]) => A→B.C
reduce_buffer([".", "B"]) => →B
reduce_buffer(["A", "."]) => A→
reduce_buffer([]) =>
reduce_buffer(["A", "B"], "X") => X(AB)
reduce_buffer(["A", ".", "B"], "X") => X(A→B)
reduce_buffer(["A", literal("."), "B"]) => A.B
```

MODE+BIND is out of scope: the FSM rejects BIND in MODE before ρ is called.
