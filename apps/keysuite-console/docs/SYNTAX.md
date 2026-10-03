# Syntax

| Glyph | Class | Notes |
| --- | --- | --- |
| a–z A–Z 0–9 | CONTENT | User-authored literals |
| . | BIND | Implication boundary. First bind splits. Later binds are text on the right. |
| : | MODE_SHIFT | Buffer becomes μ; composition restarts in MODE |
| _ | ESCAPE | Next event is CONTENT, even if it is syntax |
| SPACE ENTER TAB TIMEOUT DONE | COMMIT | ρ runs; receipt emits |
| BACKSPACE | ROLLBACK | Pop one buffered symbol; no emit |
| ESC | ABORT | Clear volatile state; no emit |

## Illegal strings

- Undeclared tokens (example `@`) enter ERROR.
- Unspecified events (example BIND from IDLE, ROLLBACK from IDLE) enter ERROR.
- BIND in MODE enters ERROR (v1.1.0 gap-close).
- Trailing `_` with no following token enters ERROR at finalize.
- MODE+BIND would have emitted `X(A→B)`. That operator is out of scope.

TIMEOUT is grammar-declared COMMIT and is not a console control.
