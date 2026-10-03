# Gdk9 CLI

Gdk9 assigns and utilizes symbolic energy for characters, numbers, strings, sentences,
paragraphs, and files. The default "Ninefold Grid" principle uses A1Z26 for letters,
digital-root for numbers, and a curated symbol table; customize via JSON/YAML.

## Quick Start
- Analyze text: `gdk9 an "Hello, world!"`
- Extended analysis: `gdk9 -C an -m extended "Hello"`
- Profile file: `gdk9 prof -f input.txt`
- Assign per-char energy: `gdk9 asg "abc123!?"`
- Attune to 7: `gdk9 att -f input.txt -t 7 -m intersperse -a '.!?*' -I`
- Compare two inputs: `gdk9 cmp "alpha" --right "beta"`
- Encode annotations: `gdk9 enc "Hi" -s annotate`
- Synthesize sigil: `gdk9 sig "Hello" -s grid`
- Show principle: `gdk9 prin show`
- Optimize plan only: `gdk9 opt "Hello" --target 5 --allowed '.!+'`
- Live TUI: `gdk9 ui --target 7 --allowed '.!?*'`

## Commands
- `an|analyze [--file FILE] [--format table|json] [TEXT]`
  Summarizes energies at document, paragraph, sentence, and word levels.
  Options: `--mode core|extended` to include vectors and harmonic triads.
- `prof|profile [--file FILE] [--format table|json] [TEXT]`
  Distribution of energies 1–9 with totals and digital-root.
- `asg|assign [--file FILE] [TEXT]`
  Per-character energy mapping.
- `att|attune -t N [--symbol S] [--file FILE] [TEXT]`
  Adjusts text to reach target digital-root (1–9).
  Options: `-m append|prepend|intersperse`, `-a '.!?*'`, `-p N`, `-w` (in-place), `-I` (include text).
  Advanced: `--method substitute|edit`, `--subs-file subs.json`, `--allow-delete`.
- `cmp|compare LEFT [--left-file PATH] RIGHT [--right-file PATH]`
  Compares totals and digital-roots.
- `enc|encode [--file FILE] [-s annotate|json] [TEXT]`
  Annotates characters with energies or emits JSON.
- `dec|decode [--file FILE] [TEXT]`
  Removes simple `[n]` annotations.
- `sig|synthesize [--file FILE] [-s grid|bar] [TEXT]`
  Visualizes energy profile as grid or bars.
- `prin|principles show|validate [--file FILE]`
  Displays active principle or validates a principle file.
- `opt|optimize --target N [--allowed SYMS] [--method M] [--file FILE] [TEXT]`
  Prints minimal-step plan to reach target energy.
- `ui|tui [--target N] [--allowed SYMS] [--method M]`
  Interactive curses UI for live typing and immediate feedback.

### Plugins
- `pl|plugin list`
  Lists discovered plugins under `./plugins` and `~/.gdk9/plugins`.
- `pl|plugin validate <NAME|PATH>`
  Validates a plugin pack (YAML/JSON/Python with top-level PLUGIN literal).
- `pl|plugin info <NAME|PATH>`
  Shows plugin metadata, rules, and symbol contributions.
- `pl|plugin load <NAME|PATH> [--no-enable] [--state PATH]`
  Loads rules/symbols into state, merges symbol energy into the active principle for this run, and enables for auto-boot unless `--no-enable`.
- `pl|plugin enable <NAME|PATH>` / `pl|plugin disable <NAME>`
  Toggle plugin auto-boot in `~/.gdk9/plugins.json`.

### Symbols & Implication Rules
- `sym|symbol add <NAME> <ENERGY> [--state PATH]`
  Adds or updates a symbol in state. Energy is a finite float.
- `sym|symbol ls|list [--state PATH]`
  Lists symbols sorted by name.
- `im|imply df|fuse <RULE> <OUT_NAME|AUTO> <ARITY> [--state PATH]`
  Defines a fusion rule combining >=2 inputs; energy conserved; output name AUTO concatenates inputs.
- `im|imply ds|split <RULE> <OUT_A> <OUT_B> <RATIO> [--state PATH]`
  Defines a split rule with ratio 0..1; energies conserve.
- `im|imply ls|list [--state PATH]`
  Lists defined rules.
- `im|imply ap|apply <RULE> <INPUTS...> [--state PATH]`
  Applies a rule to named input symbols in state and prints outputs.
  Use `--commit` to persist the resulting output symbols (names and energies) back into state.
- `repl [--state PATH]`
  Minimal interactive shell for symbols/rules.

## Official Mapping (Default)
Place your official mapping at `gdk9/data/official.json` to make it the default principle.
An example template is provided at `gdk9/data/official.example.json`.

## Principles (Config)
Use `--principle path.json` to load a custom model:
```
{
  "name": "Custom",
  "letter_mode": "a1z26",
  "number_mode": "digital_root",
  "normalize_zero_to_nine": true,
  "symbol_energy": {".": 1, "!": 3}
}
```

Substitution profile example for `--subs-file`:
```
{
  "subs": {
    "i": ["1", "!"],
    "s": ["$"],
    "e": ["3"],
    ",": [";", ":"]
  },
  "allowed_inserts": ".!?+"
}
```

## Errors & Debug
- Exit code 2 on user/config/optimization errors; clear messages on stderr.
- `--debug` or `GDK9_DEBUG=1` enables step-by-step logs.
- Color auto-detected; force with `--color` or disable with `--no-color`.

## Tokenization Details
- Command: `tok|tokenize [TEXT] [-f FILE] [-e N] [-d DELIMS] [-k|-D] [-n] [-x] [-F table|json|annotate]`
- Options:
  - `-e, --energy` 1..9 — derive delimiter set from the active principle’s `symbol_energy` for this energy (default 1)
  - `-d, --delims` — override delimiter set explicitly, e.g. `"<>|"`
  - `-k, --keep-delims` — keep delimiter runs as tokens; `-D, --drop-delims` to drop them
  - `-n, --no-strip` — do not strip whitespace around non-delimiter tokens
  - `-x, --no-footer` — suppress metrics/footer in table mode
  - `-F, --format` — `table` (default), `json`, or `annotate`
- JSON format includes rich metrics: token counts, energy sums, DR histograms, length stats, top tokens by energy, and delimiter character frequencies.
