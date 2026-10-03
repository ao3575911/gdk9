import argparse
from typing import List
from .symbol import SymbolRegistry
from .rules import parse_rules
from .runtime import Reactor


def _parse_input_sequence(s: str) -> List[str]:
    tokens: List[str] = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch.isspace():
            i += 1
            continue
        j = i
        while j < n and not s[j].isspace():
            j += 1
        tokens.append(s[i:j])
        i = j
    return tokens


def main() -> None:
    from . import __version__  # import here to avoid circular imports
    parser = argparse.ArgumentParser(prog="srr")
    parser.add_argument("--version", action="version", version=f"srr {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("rules_file", type=str)
    run_parser.add_argument("input_string", type=str)
    run_parser.add_argument("--max-iters", type=int, default=1000)
    run_parser.add_argument("--global-phase-toggle", action="store_true")
    run_parser.add_argument("--debug", action="store_true", help="print final sequence with phase information")

    
    repl_parser = subparsers.add_parser("repl")
    repl_parser.add_argument("rules_file", type=str)
    repl_parser.add_argument("--max-iters", type=int, default=1000)
    repl_parser.add_argument("--global-phase-toggle", action="store_true")

    args = parser.parse_args()
    if args.command == "run":
        import sys
        try:
            with open(args.rules_file, "r", encoding="utf-8") as f:
                rules_text = f.read()
            registry = SymbolRegistry()
            rules = parse_rules(rules_text, registry)
            input_symbols = _parse_input_sequence(args.input_string)
            reactor = Reactor(rules, registry, args.global_phase_toggle)
            seq = reactor.run(input_symbols, args.max_iters)
            if args.debug:
                debug_repr = [(registry.id_to_name[sid], phase) for sid, phase in seq]
                print(debug_repr)
            result = [registry.id_to_name[sid] for sid, _ in seq]
            print("".join(result))
        except FileNotFoundError:
            print("Error: rules file not found", file=sys.stderr)
            raise SystemExit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            raise SystemExit(1)
    elif args.command == "repl":
        import sys
        try:
            with open(args.rules_file, "r", encoding="utf-8") as f:
                rules_text = f.read()
            registry = SymbolRegistry()
            rules = parse_rules(rules_text, registry)
            reactor = Reactor(rules, registry, args.global_phase_toggle)
        except FileNotFoundError:
            print("Error: rules file not found", file=sys.stderr)
            raise SystemExit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            raise SystemExit(1)
        print("Symbol Rewrite Reactor REPL.  Type a sequence of symbols and press Enter.  Type 'exit' or 'quit' to leave.")
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                break
            if not line or line.lower() in {"exit", "quit"}:
                break
            try:
                input_symbols = _parse_input_sequence(line)
                seq = reactor.run(input_symbols, args.max_iters)
                out = [registry.id_to_name[sid] for sid, _ in seq]
                print("".join(out))
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()