# GDk9 Cheatsheet

> v0.3.0 · AGPL-3.0-or-later · `pip install -e .` → `gdk9 --help`

---

## Installation

```bash
git clone <repo>
cd gdk9
pip install -e .          # editable install
pip install -e ".[dev]"   # with ruff, black, pytest
gdk9 --version
```

---

## Global Flags

| Flag | Short | Effect |
|------|-------|--------|
| `--principle FILE` | `-P` | Load custom principle (JSON/YAML) |
| `--state FILE` | `-S` | Override state file (default `~/.gdk9/state.json`) |
| `--debug` | `-d` | Verbose step-by-step logs |
| `--color` | `-C` | Force ANSI color output |
| `--no-color` | `-N` | Disable color output |
| `--version` | | Print version and license |

---

## Command Reference

### analyze / an
```bash
gdk9 an "Hello"                        # table: document→paragraph→sentence→word
gdk9 an "Hello" -F json               # JSON output
gdk9 an -f file.txt -m extended       # include vectors and harmonic triads
gdk9 -C an "Hello"                    # colorized table
```
**Output columns:** unit | value | energy (DR) | total

---

### profile / prof
```bash
gdk9 prof "The quick brown fox"       # distribution histogram bins 1–9
gdk9 prof -f file.txt -F json        # JSON: {profile, total, dr}
gdk9 -C prof "Hello"                 # color bars
```

---

### assign / asg
```bash
gdk9 asg "abc123"                     # per-character energy table
gdk9 asg -f file.txt
```

---

### attune / att
```bash
gdk9 att "Hello" -t 7                          # append to reach DR=7
gdk9 att "Hello" -t 7 -m prepend -a ".!?"     # prepend allowed symbols
gdk9 att "Hello" -t 7 -m intersperse -p 3     # spread every ~3 chars
gdk9 att "Hello" -t 7 -m substitute           # character substitutions
gdk9 att "Hello" -t 7 -m edit                 # minimal edit plan
gdk9 att -f file.txt -t 9 -m append -I        # include attuned text in output
gdk9 att -f file.txt -t 7 -w                  # write result back in-place
gdk9 att "Hello" -t 5 --subs-file subs.json   # custom substitution map
```

**Flags:**
| Flag | Description |
|------|-------------|
| `-t N` | Target energy 1–9 (required) |
| `-m METHOD` | `append` `prepend` `intersperse` `substitute` `edit` |
| `-a SYMS` | Allowed symbols e.g. `'.!?*'` |
| `-p N` | Intersperse interval |
| `-s N` | Max steps (default 64) |
| `-I` | Include attuned text in JSON |
| `-w` | Write result in-place to `--file` |
| `--allow-delete` | Allow deletions in edit mode |
| `--subs-file` | JSON substitution map file |

---

### compare / cmp
```bash
gdk9 cmp "alpha" --right "beta"
gdk9 cmp -L file_a.txt -R file_b.txt
```
**Output:** left/right totals and DR; delta (green=0, yellow=+, red=−).

---


### kernel / kn
Pure implication kernel — no state file, JSON only.
```bash
gdk9 kernel eval ABC
gdk9 kernel apply fuse A B
gdk9 kernel apply split AB --parts A,B --energies 1,2
gdk9 kernel search A B --target AB --max-depth 2 --rules fuse
gdk9 kn eval "Hello"                 # alias
```
**Facts (default principle):** `eval ABC` → total 6 / DR 6; fuse A,B → AB energy 3 conserved; search finds the fuse proof within depth 2; impossible targets return `found: false`.

Walkthrough: `docs/HANDBOOK.md` §8 · `examples/09_kernel_search_walkthrough.py` · prove gate: `docs/PROVE.md`

---
### encode / enc
```bash
gdk9 enc "Hi" -s annotate            # H[8]i[9]
gdk9 enc "Hi" -s json                # JSON energy breakdown
```

### decode / dec
```bash
gdk9 dec "H[8]i[9]"                  # strips [n] annotations → Hi
```

---

### synthesize / sig
```bash
gdk9 sig "Hello" -s grid             # energy grid visual
gdk9 sig "Hello" -s bar              # horizontal bar chart
gdk9 -C sig "Hello" -s grid          # colorized
```

---

### tokenize / tok
```bash
gdk9 tok "<a|b> c" -e 1             # tokenize on energy-1 delimiters
gdk9 tok "a.b.c" -d "."             # explicit delimiter set
gdk9 tok "text" -k                   # keep delimiters as tokens
gdk9 tok "text" -D                   # drop delimiters
gdk9 tok "text" -F json              # JSON with full metrics
gdk9 tok "text" -F annotate          # inline energy annotations
gdk9 tok "text" -x                   # suppress footer
gdk9 tok "text" -u                   # summary/metrics only
```

---

### optimize / opt
```bash
gdk9 opt "Hello" --target 7
gdk9 opt "Hello" --target 7 --method intersperse --allowed ".!?"
```
Returns JSON plan without modifying text.

---

### tui / ui
```bash
gdk9 ui                              # interactive curses UI (default target=9)
gdk9 ui --target 7 --allowed ".!?*"
```
Type freely; energy updates live. Ctrl-C to exit.

---

### principles / prin
```bash
gdk9 prin show                        # dump active principle as JSON
gdk9 prin validate --file my.json    # validate custom principle file
gdk9 prin install --file my.json     # install as official.json
```

---

### symbol / sym
```bash
gdk9 sym add ALPHA 5.0               # add/update symbol
gdk9 sym ls                           # list all symbols
```

---

### imply / im
```bash
# Define rules
gdk9 im fuse JOIN AUTO 2             # fusion rule: 2 inputs → concatenated output
gdk9 im split HALVE L R 0.5          # split rule: 50/50
gdk9 im ls                            # list rules

# Apply rules
gdk9 im ap JOIN X Y                  # apply JOIN to symbols X and Y
gdk9 im ap HALVE X --commit          # apply and persist outputs to state
```

---

### plugin / pl
```bash
gdk9 pl list                          # discover plugins in ./plugins/ and ~/.gdk9/plugins/
gdk9 pl validate ./plugins/pack.yaml  # validate without loading
gdk9 pl info ./plugins/pack.yaml      # show metadata and rules
gdk9 pl load ./plugins/pack.yaml      # load into state and enable auto-boot
gdk9 pl load ./plugins/pack.yaml --no-enable  # load only this session
gdk9 pl enable my_pack               # enable for auto-boot
gdk9 pl disable my_pack              # disable auto-boot
```

---

### state
```bash
gdk9 state merge -i peer.json        # CRDT merge peer state into local
gdk9 state merge -i peer.json --dry-run  # preview without writing
```

---

### crypto / crypt
```bash
gdk9 crypto encrypt "message" -k KEY         # EDPC (playful, energy-path cipher)
gdk9 crypto decrypt "ciphertext" -k KEY
gdk9 crypto encrypt "message" -k KEY -m secure  # Fernet + PBKDF2-HMAC-SHA256 (200k); needs cryptography
gdk9 crypto decrypt "ciphertext" -k KEY -m secure
```

---

### subs / sub
```bash
gdk9 subs example                    # print an example substitution JSON
gdk9 subs generate                   # auto-generate from active principle
gdk9 subs generate -o subs.json      # write to file
```

---

### DCG — Directed Cognition Graph
```bash
gdk9 dcg classify FWEM              # symmetry class + energy + 4D vector per letter
gdk9 dcg classify FWEM -F json
gdk9 dcg path FWEM                   # per-step edge validity along word path
gdk9 dcg vector FWEM                 # 4D vector sum for word
gdk9 dcg shortest F M               # Dijkstra shortest path between two letters
gdk9 dcg homotopy FWEM FeWM         # check homotopy equivalence (energy+vector tol)
gdk9 dcg homotopy FWEM FeWM --tol 2.0
gdk9 dcg info                        # graph statistics (node/edge counts by type)
```

---

### repl / sh
```bash
gdk9 repl                            # interactive REPL for symbols and rules
# Inside REPL:
# symbol add NAME ENERGY
# symbol list
# imply define-fusion RULE OUT ARITY
# imply define-split RULE A B RATIO
# imply apply RULE INPUT...
# quit / exit
```

---

### handbook / hb
```bash
gdk9 handbook                        # print full EN+RU handbook
gdk9 help                            # argparse help
gdk9 help plugin                     # subcommand help
```

---

### reset / clear
```bash
gdk9 reset                           # reset state (prompts for confirmation)
gdk9 reset --yes                     # skip confirmation
gdk9 reset --plugins                 # reset plugin auto-boot config only
gdk9 reset --rules-only              # clear rules, keep symbols
gdk9 reset --symbols-only            # clear symbols, keep rules
gdk9 reset --all --yes               # reset state + plugins
```

---

## Energy Arithmetic

### A1Z26 Letter Values
```
A=1  B=2  C=3  D=4  E=5  F=6  G=7  H=8  I=9
J=10 K=11 L=12 M=13 N=14 O=15 P=16 Q=17 R=18
S=19 T=20 U=21 V=22 W=23 X=24 Y=25 Z=26
```
Lowercase = same value (case-insensitive in A1Z26 mode).

### Digital Root
```
DR(n) = 9  if n % 9 == 0  (and n ≠ 0)
DR(n) = n % 9  otherwise
DR(0) = 9  (zero normalised to nine)
```

### Same-Energy Groups (DR by A1Z26)
| DR | Letters |
|----|---------|
| 1 | A, J, S |
| 2 | B, K, T |
| 3 | C, L, U |
| 4 | D, M, V |
| 5 | E, N, W |
| 6 | F, O, X |
| 7 | G, P, Y |
| 8 | H, Q, Z |
| 9 | I, R    |

### Harmonic Triads
| Triad | Energies | Character |
|-------|----------|-----------|
| Root  | 1, 4, 7  | Grounding, stable |
| Wave  | 2, 5, 8  | Oscillating, connective |
| Peak  | 3, 6, 9  | Transformative, peak |

---

## DCG Symmetry Classes

| Class | DC (Uppercase) | AC (Lowercase) | Base Equation | SymPhi Energy |
|-------|---------------|----------------|---------------|---------------|
| **Idempotent** | A H I M O T U V W X Y | a h i m o t u v w x y | x² = x | E = pos (1–26) |
| **Biphasic**   | B C D E K             | b c d e k             | x² = f(x) | E = sin(pos) |
| **Involutive** | N S Z                 | n s z                 | x² = 1    | E = 1/pos |
| **Asymmetric** | F G J L P Q R         | f g j l p q r         | x² ≠ x,1  | E = pos+1 |

### DCG 4D Vector per Character
```
v = [pos, type_id, √|E|, sin(pos·π/26)]

type_id: idempotent=1, biphasic=2, involutive=3, asymmetric=4
```

---

## Default Symbol Energies (Ninefold Grid)

| E | Symbols |
|---|---------|
| 1 | `. < > \|` |
| 2 | `, ( ) [ ] { }` |
| 3 | `! / \\` |
| 4 | `? +` |
| 5 | `: # %` |
| 6 | `; =` |
| 7 | `- $` |
| 8 | `_ ^ @` |
| 9 | `* ~ &` |

---

## Principle File Format

```json
{
  "name": "My Principle",
  "description": "optional",
  "letter_mode": "a1z26",
  "number_mode": "digital_root",
  "normalize_zero_to_nine": true,
  "weights": {"letter": 1, "digit": 1, "symbol": 1},
  "symbol_energy": {".": 1, "!": 3, "?": 4}
}
```

---

## Plugin Pack Format

```yaml
name: my_pack
version: "0.1"
description: "Short summary"
symbol_energy:
  "~": 9
symbols:
  X: 10.0
rules:
  - type: split
    name: HALVE
    out_a: L
    out_b: R
    ratio: 0.5
  - type: fusion
    name: JOIN
    out: AUTO
    arity: 2
checks:
  - rule: HALVE
    inputs:
      - name: X
        energy: 10.0
```

---

## Substitution Profile Format

```json
{
  "subs": {
    "i": ["1", "!"],
    "s": ["$", "5"],
    "e": ["3"],
    "a": ["4", "@"]
  },
  "allowed_inserts": ".!?+"
}
```

---

## State File Format (`~/.gdk9/state.json`)

```json
{
  "symbols": {
    "ALPHA": {"energy": 5.0, "ts": 1716000000.0}
  },
  "rules": {
    "HALVE": {"name": "HALVE", "type": "split", "arity": 2,
              "params": {"out_a": "L", "out_b": "R", "ratio": 0.5}, "ts": 1716000000.0}
  }
}
```

---

## Environment Variables

| Variable | Effect |
|----------|--------|
| `GDK9_DEBUG=1` | Enable debug logging (same as `--debug`) |
| `NO_COLOR=1` | Disable ANSI color output |

---

## Common Workflows

### Attune a file to DR=9 in-place
```bash
gdk9 att -f notes.txt -t 9 -m intersperse -a '.!?*' -w
```

### Generate and save a substitution profile
```bash
gdk9 subs generate -o subs.json
```

### Bulk encode a file with per-char energy annotations
```bash
gdk9 enc -f input.txt -s annotate > annotated.txt
```

### Compare before/after energy
```bash
gdk9 cmp "original text" --right "modified text"
```

### CRDT sync two state files
```bash
gdk9 state merge -i peer_state.json
```

### Full JSON export for piping
```bash
gdk9 an "text" -F json | jq '.words[] | {val: .value, e: .energy}'
```

### DCG path analysis
```bash
gdk9 -C dcg classify "GENESIS"
gdk9 dcg path "FWEM"
gdk9 dcg shortest F M
gdk9 dcg homotopy "FWEM" "FeWM"
```

### Load and use a plugin
```bash
gdk9 pl load ./plugins/harmonic_suite.json
gdk9 sym add ROOT 7.0
gdk9 im ap TRIAD ROOT WAVE PEAK --commit
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | User/config/optimization error |