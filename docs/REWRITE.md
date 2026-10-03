# Symbol Rewrite Reactor

Symbol Rewrite Reactor (SRR) is a symbolic execution engine built around **rewrite rules** and **idempotent collapse**.  It allows you to define simple transformation rules over strings of symbols and then iteratively apply those rules until a canonical form or cycle is reached.  SRR supports multi‑character symbols, per‑symbol phase annotations, rule priorities, idempotent declarations, default phase declarations and directional semantics.  You can use SRR as a lightweight research tool for exploring symbolic grammars, language evolution, compression or emergent behaviours.

## Features

- **Multi‑character symbols** and optional phase annotations (e.g. `A0`, `foo1`).
- **Idempotent declarations** (`idempotent: A,B`) collapse adjacent repeats of idempotent symbols.
- **Default phase declarations** (`default_phase: A=0,B=1`) assign a starting phase to each symbol.
- **Rewrite rules** of the form `pattern -> replacement` with optional `priority=` to control application order.
- **Directional semantics**: patterns respect symbol order (`AB` and `BA` are distinct).
- **Biphasic state management** via phase annotations on symbols and replacement sequences.
- **CLI tool** to run rules on an input string: `python -m srr.cli run rules.txt "A B C"`.
- **Extensible Python API** for integrating SRR into other applications.
- **Test suite** driven by `pytest` and `hypothesis`.

## Installation

To install SRR in a virtual environment, clone the repository and run:

```bash
python -m pip install --upgrade pip
python -m pip install -e .[test]
```

This installs SRR along with its test dependencies.  You can run the test suite with:

```bash
pytest
```

## Rule File Syntax

A rule file is a plain text file.  Blank lines and lines starting with `#` are ignored.  Each directive or rule must appear on its own line.

### Idempotent Declaration

```
idempotent: A,B
```

Declares `A` and `B` as idempotent; consecutive duplicates will collapse into a single symbol.

### Default Phase Declaration

```
default_phase: A=1,B=0
```

Assigns a default phase to each symbol.  When a symbol first appears, it receives this phase unless overridden by an annotation in the rule.

### Rewrite Rules

```
AB -> C
foo1 bar -> baz0 priority=10
```

The left‑hand side and right‑hand side are sequences of symbols separated by whitespace.  A symbol may end with a digit to set its phase.  You can assign a priority to a rule using `priority=NUMBER`.  Lower priority numbers run earlier.

### DSL Specification

The SRR rewrite language is deliberately simple and human‑readable.  Each rule file consists of a series of directives and rewrite rules:

* **Idempotent declarations** mark one or more symbols as idempotent.  Adjacent duplicates of an idempotent symbol are collapsed into a single instance.  Syntax: `idempotent: A,B,C`.
* **Default phase declarations** assign an initial phase (0 or 1) to each symbol.  When a symbol first appears, it takes this phase unless an explicit phase suffix is provided.  Syntax: `default_phase: A=0,B=1`.
* **Rewrite rules** map a pattern of one or more symbols to a replacement sequence.  A pattern and replacement are separated by `->`.  Symbols can include a trailing digit (0 or 1) to indicate their phase.  You can specify a rule's priority either with `priority=NUMBER` after the replacement or by appending `priority NUMBER` at the end of the line.  Lower numbers run first.

The grammar can be summarised informally as:

```
file        := (directive | rule | blank | comment)*
directive   := 'idempotent' ':' symbol_list
             | ('default_phase' | 'phase') ':' phase_list
rule        := pattern '->' replacement [ 'priority' '='? INT ]
symbol_list := symbol (',' symbol)*
phase_list  := symbol '=' phase (',' symbol '=' phase)*
pattern     := token+
replacement := token+
token       := symbol [phase]
symbol      := NAME
phase       := '0' | '1'
blank       := EMPTY_LINE
comment     := '#' .* (ignored)
```

Where `NAME` is any non‑empty sequence of non‑whitespace characters except digits at the end.  Tokens are separated by whitespace or `+` signs.  Phases must be 0 or 1; any other digit is rejected.

### Running With Debugging

The CLI provides a `--debug` flag on the `run` subcommand.  When set, the reactor prints the final sequence as a list of `(symbol, phase)` pairs instead of concatenating the symbol names together.  This is useful for inspecting the internal phases of your symbols.  Example:

```bash
python -m srr.cli run --debug rules.txt "A B C"
```

The `--version` flag prints the installed SRR version.  You can always run `--help` to see available options.

### Interactive REPL

For quick experimentation you can use the built‑in REPL.  Invoke the `repl` subcommand with a rule file:

```bash
python -m srr.cli repl rules.txt
```

This will load the rules and drop you into an interactive loop.  Type a sequence of symbols and press Enter to see the reactor's output.  Enter `quit` or `exit` to leave the REPL.

### Troubleshooting

* **Invalid token** – Every token in a pattern or replacement must start with a letter or underscore.  If you see `ValueError: Invalid token without symbol name`, ensure you have not started a token with a digit or left a space between a symbol name and its phase.
* **Invalid phase** – Phases must be `0` or `1`.  Any other digit will raise a `ValueError`.
* **Conflicting default phase** – Assigning different default phases to the same symbol across directives is not permitted and will raise an error.
* **Unexpected line** – Lines that are not directives or valid rules cause an error.  Remove stray text or prefix it with `#` to comment it out.

## Example

Create a file `rules.txt`:

```
# declare idempotent symbols
idempotent: X,Y

# default phases
default_phase: X=0,Y=0,Z=1

# rewrite rules
XY -> Z
XZ -> Y1
Z1 -> X0 priority=0
```

Run the reactor from the command line:

```bash
python -m srr.cli run rules.txt "X Y X Z"
```

The program will print the final canonical sequence after applying the rules until no further changes occur.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the terms of the [MIT License](LICENSE).