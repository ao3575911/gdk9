# KeySuite Conformance Bridge (Phase A Inventory)

**Spec:** gdk9 Spec 7 — KeySuite conformance bridge  
**Phase:** A inventory + B spike (one compose adapter test)  
**Home repo:** [`ao3575911/gdk9`](https://github.com/ao3575911/gdk9)  
**Sibling literature (read-only):** [`ao3575911/gdk9_keysuite`](https://github.com/ao3575911/gdk9_keysuite)  
**Status:** Phase A inventory retained; Phase B spike adds one outside-kernel compose adapter test. KeySuite still untouched.

This note maps KeySuite's published GDk9 v1.0.0 conformance vectors onto what
`gdk9.kernel` actually exposes today. Claims below cite file paths in both
repos. No new maths is introduced.

---

## Non-goals (explicit)

- **No Redis / WebSocket / transport bridge.** KeySuite runtime docs cover
  websocket lifecycle, API auth, metrics, and session isolation
  (`gdk9_keysuite/docs/RUNTIME_CONFORMANCE.md`). Those surfaces are out of
  scope for `gdk9.kernel` and for this inventory.
- **No closing of KeySuite issues** and **no edits to `gdk9_keysuite`.**
  This document lives only in gdk9.
- **No invented implication semantics.** Where kernel support is absent or
  only loosely related, the matrix says `no` / `partial` with evidence —
  it does not redefine KeySuite reduction.

Preferred follow-on is still **Approach A** (keep this docs inventory). See
the PR description for Approaches B and C.

---

## Sources sampled (via GitHub API)

### KeySuite conformance artifacts

| Artifact | Path | Role |
| --- | --- | --- |
| Vector suite README | `gdk9_keysuite/conformance/README.md` | JSONL format; implementation-independent; SPACE and DONE as commit events |
| Core vectors | `gdk9_keysuite/conformance/vectors/gdk9-v1.0.0.jsonl` | compose, implication, mode, commit (11 rows) |
| Abort vectors | `gdk9_keysuite/conformance/vectors/abort-v1.0.0.jsonl` | ESC clears volatile state (4 rows) |
| Escape vectors | `gdk9_keysuite/conformance/vectors/escape-v1.0.0.jsonl` | `_` literal escape (7 rows) |
| Invalid vectors | `gdk9_keysuite/conformance/vectors/invalid-v1.0.0.jsonl` | ERROR state / recovery (6 rows) |
| Rollback vectors | `gdk9_keysuite/conformance/vectors/rollback-v1.0.0.jsonl` | BACKSPACE (4 rows) |
| Vector narrative | `gdk9_keysuite/docs/CONFORMANCE_VECTORS.md` | Human table of expected outputs |
| Runtime coverage list | `gdk9_keysuite/docs/RUNTIME_CONFORMANCE.md` | Broader behaviors (incl. transport; non-goals here) |
| Grammar control surface | `gdk9_keysuite/grammar/gdk9-v1.0.0.yaml` | States, event classes, transitions, commit set |

### gdk9 kernel / API evidence

| Artifact | Path | Role |
| --- | --- | --- |
| Kernel overview | `docs/KERNEL.md` | Pure in-memory implication surface; no CLI/state/plugins |
| Architecture | `docs/ARCHITECTURE.md` | Kernel boundary vs CLI / imply / state |
| Public API | `docs/API.md` | `gdk9.kernel.*` import surface |
| Engine | `gdk9/kernel/engine.py` | `evaluate`, `judge`, `apply`, `normalize`, `infer`; `fusion_rule` / `split_rule` |
| Expression / Symbol | `gdk9/kernel/expression.py`, `gdk9/kernel/symbol.py` | Ordered named units with energy |
| Rules | `gdk9/kernel/rule.py` | `RuleKind`: fusion / split / rewrite |
| Errors | `gdk9/kernel/errors.py` | `KernelError`, `ConservationError`, `ImplicationError`, … |
| Kernel tests | `tests/kernel/test_kernel_rules.py`, `tests/kernel/test_kernel_energy.py` | Fusion/split conservation and search |

---

## Vector schema (KeySuite)

From `gdk9_keysuite/conformance/README.md`, each JSONL line is a standalone object, e.g.:

```json
{
  "id": "implication.basic.001",
  "tokens": ["C", "C", ".", "3", "3", "SPACE"],
  "output": "CC→33",
  "final_state": "IDLE",
  "exit_code": 0
}
```

Grammar-declared event families (`gdk9_keysuite/grammar/gdk9-v1.0.0.yaml`):

| Event class | Tokens / symbols | States involved |
| --- | --- | --- |
| CONTENT | `a-z` `A-Z` `0-9` | IDLE → COMPOSE; buffer append |
| BIND | `.` | COMPOSE; mark implication boundary |
| MODE_SHIFT | `:` | COMPOSE → MODE |
| COMMIT | `SPACE`, `ENTER`, `TAB`, `TIMEOUT`, `DONE` | reduce_and_emit → IDLE |
| ROLLBACK | `BACKSPACE` | pop last buffered symbol |
| ABORT | `ESC` | clear → IDLE |
| Escape (lexer) | `_` + next token | literalize syntax / invalid / commit names |
| Invalid | e.g. `@`, `-` | unrecovered `ERROR` until ABORT |

KeySuite guarantees (grammar `conformance` block): deterministic; emits only on
commit; reduction is pure; mutation scope is volatile buffer until commit.

---

## Support matrix: vector class → `gdk9.kernel`

Legend: **yes** = kernel can implement the vector semantics as-is;
**partial** = related primitive exists but not the KeySuite token/FSM contract;
**no** = no corresponding API or state machine in `gdk9.kernel`.

| Vector class | Vector file / id prefix | Kernel support | Evidence (gdk9) | Evidence (KeySuite) | Notes |
| --- | --- | --- | --- | --- | --- |
| Plain composition | `gdk9-v1.0.0.jsonl` → `compose.basic.*` | **partial** | `Expression.from_names` / `Expression.text()` (`gdk9/kernel/expression.py`); `fusion_rule` joins names (`gdk9/kernel/engine.py`); tested in `tests/kernel/test_kernel_rules.py` | e.g. `["A","B","SPACE"]` → `"AB"` | Kernel can represent concatenated names and fuse energies, but has **no** token stream, COMMIT events, or IDLE/COMPOSE FSM. |
| Bind implication (`→`) | `gdk9-v1.0.0.jsonl` → `implication.basic.*` | **no** | Kernel `ImplicationRule` / `ImplicationEngine` apply **energy transforms** (fusion/split/rewrite), not grammar bind-marker string reduction to `→` (`docs/KERNEL.md`, `gdk9/kernel/rule.py`) | e.g. `["C","C",".","3","3","SPACE"]` → `"CC→33"`; `docs/CONFORMANCE_VECTORS.md` | Same English word "implication"; different contract. Do not equate without an adapter. |
| Mode shift | `gdk9-v1.0.0.jsonl` → `mode.basic.*` | **no** | No mode context field in kernel types (`gdk9/kernel/*.py`) | e.g. `["X",":","A","B","SPACE"]` → `"X(AB)"`; grammar `MODE_SHIFT` / `MODE` state | |
| Commit events | `gdk9-v1.0.0.jsonl` → `commit.*` | **no** | Kernel has no commit boundary; evaluation is synchronous API calls (`gdk9/kernel/engine.py`) | `SPACE` / `ENTER` / `TAB` / `TIMEOUT` / `DONE`; idle commit noop; grammar `COMMIT` | Includes `commit.done.*` and `commit.timeout.001`. |
| Abort (`ESC`) | `abort-v1.0.0.jsonl` → `abort.*` | **no** | No volatile buffer or abort action in kernel | ESC → `output: null`, `final_state: IDLE` | |
| Literal escape (`_`) | `escape-v1.0.0.jsonl` → `escape.*` | **no** | No escape lexer in kernel; tokenizer elsewhere (`gdk9/tokenize.py`) is energy-delimiter based, not `_`-escape | e.g. `["A","_",".","B","SPACE"]` → `"A.B"`; trailing `_` → ERROR | |
| Invalid / ERROR | `invalid-v1.0.0.jsonl` → `invalid.*` | **partial** | Kernel raises `ImplicationError` / `ConservationError` / `UnknownSymbolError` (`gdk9/kernel/errors.py`) on rule misuse — **not** an unrecovered FSM `ERROR` state with `exit_code` | `@` / `-` → `final_state: ERROR`, `exit_code: 1`; recovery via ESC | Exception types ≠ KeySuite ERROR jurisdiction. |
| Rollback (`BACKSPACE`) | `rollback-v1.0.0.jsonl` → `rollback.*` | **no** | Expressions are immutable tuples; no buffer `pop` (`gdk9/kernel/expression.py`) | BACKSPACE removes last buffered symbol before commit | |

### Aggregate (Phase A)

| Support | Count of classes (above) |
| --- | --- |
| yes | 0 |
| partial | 2 (compose, invalid/ERROR) |
| no | 6 (implication-bind, mode, commit, abort, escape, rollback) |

**Conclusion:** `gdk9.kernel` is a **pure symbolic implication / energy engine**,
not a KeySuite-compatible token runtime. Phase A stops at this inventory.
Any executable bridge needs an explicit adapter (Approach B) that owns FSM,
lexing, commit, and string reduction — without claiming those behaviors live
in the kernel today.

---

## What `gdk9.kernel` *does* cover (for orientation)

Cited from `docs/KERNEL.md` and `gdk9/kernel/__init__.py`:

- `KernelPrinciple` — immutable valuation over principle data
- `Symbol` / `Expression` — named units and ordered expressions
- `ImplicationRule` + `RuleKind` — fusion / split / rewrite metadata
- `ImplicationEngine` — evaluate, judge, apply, normalize, bounded `infer`
- `Judgment` / `ProofStep` — traceable proof steps
- Boundary: may use `gdk9.energy` / `gdk9.principles`; must not import CLI,
  state, plugins, crypto, TUI

Related but **non-kernel** gdk9 surfaces (also not KeySuite vector runners):

- `gdk9/imply.py` — named fusion/split over a symbols dict (state-oriented)
- `gdk9/tokenize.py` — energy-based text splitting
- `gdk9/state.py` / `gdk9/crdt.py` — filesystem LWW state (kernel forbids this)

---

## Sampled vector ids (complete inventory of published JSONL)

### `conformance/vectors/gdk9-v1.0.0.jsonl` (11)

`compose.basic.001`, `compose.basic.002`, `compose.basic.003`,
`implication.basic.001`, `implication.basic.002`, `mode.basic.001`,
`commit.idle.001`, `commit.timeout.001`, `commit.done.001`,
`commit.done.implication.001`, `commit.done.mode.001`

### `conformance/vectors/abort-v1.0.0.jsonl` (4)

`abort.compose.001`, `abort.bind.001`, `abort.mode.001`, `abort.error.001`

### `conformance/vectors/escape-v1.0.0.jsonl` (7)

`escape.literal.bind.001`, `escape.literal.mode.001`, `escape.literal.escape.001`,
`escape.compose.001`, `escape.literal.commit.001`, `escape.literal.invalid.001`,
`escape.trailing.001`

### `conformance/vectors/invalid-v1.0.0.jsonl` (6)

`invalid.symbol.001`, `invalid.symbol.002`, `invalid.symbol.003`,
`invalid.recovery.001`, `invalid.recovery.002`, `invalid.commit.001`

### `conformance/vectors/rollback-v1.0.0.jsonl` (4)

`rollback.basic.001`, `rollback.empty.001`, `rollback.bind.001`,
`rollback.after.escape.001`

**Total published vectors sampled:** 32 lines across 5 files.

---

## Suggested next steps (not done in this PR)

1. Keep this inventory as the Spec 7 Phase A record (**Approach A** — preferred).
2. Phase B spike (done): one compose adapter outside the kernel — see
   **Phase B spike** below. Full FSM JSONL runner still deferred.
3. Approach C: defer any bridge work; retain this doc as the decision record.

---



---

## Phase B spike (compose.basic.001)

**Date:** 2026-09-20  
**card_id:** `gdk9-keysuite-phase-b-spike`

### What was tried

- Vendored **one** KeySuite row read-only:
  `tests/keysuite/fixtures/compose.basic.001.json`
  (`id=compose.basic.001`, tokens `A B SPACE` → `AB`), sourced from
  `gdk9_keysuite/conformance/vectors/gdk9-v1.0.0.jsonl`. KeySuite repo not edited.
- Added outside-kernel adapter `gdk9/keysuite_bridge/compose.py`:
  strip COMMIT tokens → `Expression.from_names` → callers assert `text()` /
  conserved `fusion_rule`.
- Tests: `tests/keysuite/test_compose_basic_001.py`.

### Result

| Check | Outcome |
| --- | --- |
| Content names `("A","B")` → `Expression.text() == "AB"` | **pass** |
| `fusion_rule` → name `AB`, energy conserved | **pass** |
| KeySuite COMMIT / IDLE / COMPOSE FSM | **not implemented** (documented gap; Phase A `partial`) |
| implication-bind / mode / abort / escape / rollback | **out of scope** (Phase A `no`) |

No `pytest.xfail` — the partial-fit claims that *can* be stated honestly against
the kernel pass. The FSM gap remains explicit in this section and the matrix
above (compose stays **partial**, not **yes**).

### Gap citation

Compose is still **partial** in the support matrix: kernel can represent
concatenated names and fuse energies, but has no token stream or commit FSM.
This spike proves the name/energy slice only. Full JSONL runner / Approach B FSM
remains deferred.

### Non-goals held

No Redis/WS, no KeySuite mutations, no kernel semantics change, no full vector
suite runner.

## Provenance

- Inventory assembled from GitHub Contents / blob reads of
  `ao3575911/gdk9` and `ao3575911/gdk9_keysuite` (no clone of KeySuite into
  gdk9; KeySuite untouched).
- KeySuite runtime version cited in sibling docs:
  `docs/VERSION_MATRIX.md` / `docs/RUNTIME_CONFORMANCE.md`
  (GDk9 standard 1.0.0; KeySuite noted as `1.1.0.dev3` at sampling time).