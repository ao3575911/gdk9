# Grammar

Control surface: `grammar/gdk9-v1.1.0.yaml`. v1.1.0 is a gap-close of v1.0.0, not a new operator.

Deltas vs v1.0.0, and only these:

- Unspecified event → ERROR
- MODE + BIND → ERROR
- Escape `_` documented as “next event is CONTENT”

Product KeySuite. Standard GDk9. MODE+BIND out of scope.

## Transition table

| State | Event | Next | Action |
| --- | --- | --- | --- |
| IDLE | CONTENT | COMPOSE | append |
| IDLE | COMMIT | IDLE | noop |
| IDLE | ABORT | IDLE | noop |
| COMPOSE | CONTENT | COMPOSE | append |
| COMPOSE | BIND | COMPOSE | mark_bind |
| COMPOSE | MODE_SHIFT | MODE | set_mode |
| COMPOSE | COMMIT | IDLE | reduce_and_emit |
| COMPOSE | ROLLBACK | COMPOSE | pop |
| COMPOSE | ABORT | IDLE | clear |
| MODE | CONTENT | MODE | append |
| MODE | BIND | ERROR | noop |
| MODE | COMMIT | IDLE | reduce_and_emit |
| MODE | ROLLBACK | MODE | pop |
| MODE | ABORT | IDLE | clear |
| ERROR | ABORT | IDLE | clear |

Any other pair is unspecified and enters ERROR.
