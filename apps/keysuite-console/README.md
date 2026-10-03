# KeySuite

[![conformance](https://github.com/ao3575911/keysuite/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ao3575911/keysuite/actions/workflows/ci.yml)

Reference runtime for **GDk9** 1.1.0. Local web console. No model in the core.

Algebra is `reduce_buffer` only: first-bind split, U+2192, optional `mode(core)` wrap. Receipt ρ(B, μ) exists only at COMMIT.

## Install

```bash
npm install
npm test
npm run dev
```

Type `CC.33` then Commit.

```
CC→33
```

## Layout

```
grammar/gdk9-v1.1.0.yaml   control surface
src/lib/gdk9/              kernel (symbols → fsm → reducer → session)
src/components/keysuite/   console; buttons map 1:1 to event classes
docs/                      freeze: REDUCTION, SYNTAX, GRAMMAR
public/conformance/vectors official JSON vectors
```

Session is the only caller of ρ. MODE+BIND is out of scope.

## Grammar

- Artifact: [`grammar/gdk9-v1.1.0.yaml`](grammar/gdk9-v1.1.0.yaml)
- SHA-256: `0c8974e76427799dc62ac6839057c8fff41d3ad7ae29c3e6c9d070dd9df1b7a7`
- Freeze: [`docs/REDUCTION.md`](docs/REDUCTION.md) · [`docs/SYNTAX.md`](docs/SYNTAX.md) · [`docs/GRAMMAR.md`](docs/GRAMMAR.md)

v1.1.0 is a gap-close of v1.0.0 (unspecified events and BIND in MODE → ERROR), not a new operator.

## Conformance

```bash
npm test
```

Vector `gdk9-vector-001` is `C C . 3 3 SPACE` → `CC→33`.

## License

MIT
