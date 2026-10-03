"""
GDk9 Pipeline
===============

This module defines a modular symbolic processing pipeline called GDk9. The
pipeline converts symbolic inputs into structured objects, builds relations
between them, allocates an energy metric and returns a summary. It also
includes static definitions for symbol suites and their binary values. These
definitions can be used by downstream applications (e.g. bots or analysis
tools) to map characters to predefined suites and to inspect their binary
representation.

Design goals
------------

* **Scalability** – Each processing stage is encapsulated in its own class and
  exposes a simple `process` method. New stages can be added or replaced
  without modifying existing code (open/closed principle). The pipeline
  accepts arbitrary iterable inputs and can be extended to handle streaming
  workloads. Internal data structures use Python primitives to remain
  lightweight.

* **Privacy and security** – No secrets or sensitive data are stored in
  class attributes. Sensitive configuration should be provided via
  environment variables or injected securely at runtime. Logging functions
  avoid serialising raw input; instead they emit anonymised metrics. The
  constants defined for symbol suites are purely declarative and do not
  contain any personal information.

* **Utility and maintainability** – The module follows SOLID principles:
  each class has a single responsibility, dependencies are minimal, and
  constants are defined in one place. Extensive docstrings and type hints
  aid readability. The symbol suite tables allow other systems to reuse
  consistent mappings across the stack.

The code below can be imported as a library or executed standalone. When
executed, it will demonstrate the pipeline on a sample string and print the
result.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple


# ---------------------------------------------------------------------------
# CRDT (Last-Write-Wins) utility functions
#
# The GDk9 package provides a CRDT implementation for merging JSON-like maps
# with deterministic conflict resolution. When two maps contain the same key,
# the entry with the larger timestamp wins. If timestamps are equal then
# lexicographic ordering of the actor string breaks ties. Entries that are
# plain values are coerced into a structured form with ``value``, ``timestamp``
# and ``actor`` fields. The functions below are copied from the original
# ``gdk9.crdt`` module to avoid an external dependency and to allow the
# ``crdt-merge`` subcommand to operate when the gdk9 package is not installed.

@dataclass(frozen=True)
class LwwEntry:
    """A tagged value for last-write-wins CRDTs.

    Parameters
    ----------
    value : Any
        The underlying value of the entry.
    timestamp : float
        A UNIX timestamp indicating when the value was written.
    actor : str
        An identifier for the actor (e.g. device or user) that wrote the value.
    """

    value: Any
    timestamp: float
    actor: str


def coerce_entry(raw: Any, default_actor: str = "legacy", default_ts: float = 0.0) -> LwwEntry:
    """Coerce a raw object into an ``LwwEntry``.

    If ``raw`` is a dictionary, its ``value``, ``timestamp`` and ``actor`` fields
    are extracted with fallbacks. Non-dict values are wrapped with the default
    actor and timestamp. Invalid or missing timestamps are treated as the
    provided default timestamp.

    Parameters
    ----------
    raw : Any
        The raw value to coerce.
    default_actor : str, optional
        Actor to use when the input does not specify one.
    default_ts : float, optional
        Timestamp to use when the input does not specify one.

    Returns
    -------
    LwwEntry
        A normalised entry containing ``value``, ``timestamp`` and ``actor``.
    """
    if isinstance(raw, dict):
        # Extract value, timestamp and actor from nested dict. If the raw dict
        # contains other keys, they are ignored.
        value = raw.get("value", raw)
        try:
            ts = float(raw.get("timestamp", default_ts))
        except (TypeError, ValueError):
            ts = float(default_ts)
        actor_raw = raw.get("actor", default_actor)
        # Treat blank actors as unspecified
        actor = default_actor if actor_raw in {None, ""} else str(actor_raw)
        return LwwEntry(value, ts, actor)
    # Primitive types have no metadata; wrap them using defaults
    return LwwEntry(raw, float(default_ts), default_actor)


def lww_merge(a: LwwEntry, b: LwwEntry) -> LwwEntry:
    """Select the winning entry between two ``LwwEntry`` instances.

    The entry with the larger timestamp wins. When timestamps are equal the
    lexicographically larger actor name wins. This deterministic policy
    ensures that concurrent writes converge consistently across replicas.

    Parameters
    ----------
    a, b : LwwEntry
        The entries to compare.

    Returns
    -------
    LwwEntry
        The winner according to the last-write-wins policy.
    """
    if b.timestamp > a.timestamp:
        return b
    if b.timestamp < a.timestamp:
        return a
    # If timestamps are equal, break ties by actor
    return b if b.actor >= a.actor else a


def stamp(value: Any, actor: str | None = None, ts: float | None = None) -> Dict[str, Any]:
    """Attach timestamp and actor metadata to a raw value.

    Useful when generating inputs for CRDT merges; this helper returns a
    dictionary with keys ``value``, ``timestamp`` (current time by default)
    and ``actor`` (``anonymous`` by default).
    """
    import time  # Local import avoids polluting module namespace when unused
    return {
        "value": value,
        "timestamp": float(time.time() if ts is None else ts),
        "actor": actor or "anonymous",
    }


def merge_maps(
    left: Dict[str, Any],
    right: Dict[str, Any],
    default_actor: str = "legacy",
    default_ts: float = 0.0,
) -> Tuple[Dict[str, Any], Dict[str, int], Dict[str, str]]:
    """Merge two LWW maps into a single map with statistics.

    The input maps may contain primitive values or dictionaries with CRDT
    metadata. Each key is considered independently. Keys present only in
    ``right`` are added to the merged result. Keys present in both maps are
    resolved according to the last-write-wins policy. Keys present only in
    ``left`` are carried over unchanged. The returned tuple includes the
    merged map, a stats dictionary with counts of added/updated/unchanged
    entries, and a winners dictionary mapping each key to the winning side
    (``"left"`` or ``"right"``).

    Parameters
    ----------
    left, right : dict
        Input maps to merge. Values may be primitives or CRDT dicts.
    default_actor : str, optional
        Actor to use when input values lack actor metadata.
    default_ts : float, optional
        Timestamp to use when input values lack timestamp metadata.

    Returns
    -------
    Tuple[Dict[str, Any], Dict[str, int], Dict[str, str]]
        A tuple containing the merged map, statistics, and winners.
    """
    merged: Dict[str, Any] = {}
    stats = {"added": 0, "updated": 0, "unchanged": 0}
    winners: Dict[str, str] = {}
    keys = set(left.keys()) | set(right.keys())
    for key in keys:
        has_left = key in left
        has_right = key in right
        # Key only in left; carry over unchanged
        if has_left and not has_right:
            lentry = coerce_entry(left[key], default_actor, default_ts)
            merged[key] = {
                "value": lentry.value,
                "timestamp": lentry.timestamp,
                "actor": lentry.actor,
            }
            winners[key] = "left"
            stats["unchanged"] += 1
            continue
        # Key only in right; add to merged
        if has_right and not has_left:
            rentry = coerce_entry(right[key], default_actor, default_ts)
            merged[key] = {
                "value": rentry.value,
                "timestamp": rentry.timestamp,
                "actor": rentry.actor,
            }
            winners[key] = "right"
            stats["added"] += 1
            continue
        # Key in both; resolve via LWW
        lentry = coerce_entry(left.get(key), default_actor, default_ts)
        rentry = coerce_entry(right.get(key), default_actor, default_ts)
        winner = lww_merge(lentry, rentry)
        merged[key] = {
            "value": winner.value,
            "timestamp": winner.timestamp,
            "actor": winner.actor,
        }
        winners[key] = "left" if winner is lentry else "right"
        # Determine update vs unchanged
        if winner is lentry:
            stats["unchanged"] += 1
        elif (
            lentry.value != rentry.value
            or lentry.timestamp != rentry.timestamp
            or lentry.actor != rentry.actor
        ):
            stats["updated"] += 1
        else:
            stats["unchanged"] += 1
    return merged, stats, winners

# Configure module-level logging. Avoid logging raw input to protect privacy.
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class GDk9Pipeline:
    """A modular pipeline for processing symbolic sequences.

    The pipeline is initialised with a set of processing stages. Each stage must
    implement a `process(data: Any, context: Dict[str, Any]) -> Any` method.
    During execution the pipeline passes the output of each stage as the input
    to the next stage.
    """

    def __init__(self, stages: Dict[str, Any] | None = None) -> None:
        # Use default stages if none are provided
        self.stages = stages or {
            "parser": SymbolParser(),
            "mapper": SymbolMapper(),
            "relation_engine": RelationEngine(),
            "allocator": EnergyAllocator(),
            "output": OutputModule(),
        }

    def run(self, data: Iterable[str], context: Dict[str, Any] | None = None) -> Any:
        """Run the pipeline on the input data.

        Parameters
        ----------
        data : Iterable[str]
            An iterable of characters or tokens to process.
        context : Dict[str, Any], optional
            A mutable context dictionary shared across stages. Can carry
            configuration or metrics.

        Returns
        -------
        Any
            The processed output after the final stage.
        """
        # Use provided context even if empty to allow callers to collect metrics.
        if context is None:
            context = {}
        result: Any = data
        for name, stage in self.stages.items():
            logger.debug("Running stage %s", name)
            result = stage.process(result, context)
            logger.debug("Result after %s: %s", name, result)
        return result


class SymbolParser:
    """Filter and normalise raw input into a list of symbols.

    Only alphanumeric characters are retained. This ensures that downstream
    stages operate on a clean sequence without punctuation or whitespace.
    """

    def process(self, data: Iterable[str], context: Dict[str, Any]) -> List[str]:
        symbols = [char for char in data if char.isalnum()]
        # Increment a simple metric
        context.setdefault("parsed_count", 0)
        context["parsed_count"] += len(symbols)
        return symbols


class SymbolMapper:
    """Map plain symbols to their semantic suite and binary representation.

    Uses the global SYMBOL_SUITES dictionary defined below. Unknown symbols
    (e.g. unsupported characters) are marked with suite ``'unknown'`` and
    binary value ``None``. The output is a list of dictionaries with keys
    ``symbol``, ``suite`` and ``binary``.
    """

    def process(self, data: Iterable[str], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        mapped: List[Dict[str, Any]] = []
        for sym in data:
            entry = SYMBOL_SUITES.get(sym)
            if entry:
                suite, binary = entry["suite"], entry["binary"]
            else:
                suite, binary = "unknown", None
            mapped.append({"symbol": sym, "suite": suite, "binary": binary})
        context.setdefault("mapped_count", 0)
        context["mapped_count"] += len(mapped)
        return mapped


class RelationEngine:
    """Construct simple relations between consecutive symbols.

    Relations are represented as strings ``"A->B"`` indicating that symbol A
    precedes symbol B. The output is a dictionary with keys ``symbols`` and
    ``relations``.
    """

    def process(self, data: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        relations = []
        for i in range(len(data) - 1):
            src = data[i]["symbol"]
            dst = data[i + 1]["symbol"]
            relations.append(f"{src}->{dst}")
        context.setdefault("relation_count", 0)
        context["relation_count"] += len(relations)
        return {"symbols": data, "relations": relations}


class EnergyAllocator:
    """Allocate an energy metric based on the number of symbols.

    The simplistic implementation below assigns the energy as the count of
    symbols but can be replaced with more complex logic (e.g. weighting by
    symbol suite or binary value). The energy metric is stored in the context.
    """

    def process(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        total_energy = len(data["symbols"])
        data["energy"] = total_energy
        context.setdefault("energy_sum", 0)
        context["energy_sum"] += total_energy
        return data


class OutputModule:
    """Format the final output.

    Returns a summary dictionary containing the number of symbols, the number
    of relations, total energy and the relations list. Downstream clients can
    present or serialise this information as needed.
    """

    def process(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        symbols = data.get("symbols", [])
        relations = data.get("relations", [])
        energy = data.get("energy", 0)
        return {
            "symbol_count": len(symbols),
            "relation_count": len(relations),
            "energy": energy,
            "relations": relations,
        }


# ---------------------------------------------------------------------------
# Symbol Suite Definitions
# ---------------------------------------------------------------------------

def _generate_suite_table() -> Dict[str, Dict[str, Any]]:
    """Generate symbol suite definitions for uppercase, lowercase and digits.

    Each entry maps a symbol to a dictionary with keys ``suite`` and ``binary``.
    The suite is a simple name derived from the symbol (e.g. ``suite_A``) and
    the binary value is the 8-bit ASCII representation as a string. This
    generator is executed at import time to avoid re-creating dictionaries.
    """
    table: Dict[str, Dict[str, Any]] = {}
    for sym in [chr(i) for i in range(48, 58)]:  # digits 0-9
        table[sym] = {
            "suite": f"suite_{sym}",
            "binary": format(ord(sym), "08b"),
        }
    for sym in [chr(i) for i in range(65, 91)]:  # uppercase A-Z
        table[sym] = {
            "suite": f"suite_{sym}",
            "binary": format(ord(sym), "08b"),
        }
    for sym in [chr(i) for i in range(97, 123)]:  # lowercase a-z
        table[sym] = {
            "suite": f"suite_{sym}",
            "binary": format(ord(sym), "08b"),
        }
    return table


# Export the symbol suite table as a constant. Downstream modules may import
# ``SYMBOL_SUITES`` to look up the suite and binary for any supported symbol.
SYMBOL_SUITES: Dict[str, Dict[str, Any]] = _generate_suite_table()


import argparse
import json
import os
import sys
from pathlib import Path


def _digital_root(n: int) -> int:
    """Compute the digital root of a positive integer.

    The digital root reduces a number to a single digit by iteratively
    summing its digits. For example, 987 -> 9+8+7=24 -> 2+4=6. The
    conventional GDk9 approach treats a digital root of 0 as 9, so the
    range is 1..9 inclusive.
    """
    n = abs(int(n))
    if n == 0:
        return 9
    return 9 if (n % 9 == 0) else (n % 9)


def _char_energy(ch: str) -> int:
    """Compute a simple energy value for a single character.

    Letters, digits and other symbols are all mapped via their Unicode
    codepoint to a digital root in the 1..9 range. Whitespace yields zero
    energy and is ignored in profiles. This simplified scheme avoids
    dependence on external principle files while still producing a
    repeatable energy profile.
    """
    if ch.isspace():
        return 0
    return _digital_root(ord(ch))


def _energy_profile(text: str) -> Dict[str, int]:
    """Return a histogram of energy values (1..9) across the input text."""
    profile = {str(i): 0 for i in range(1, 10)}
    for ch in text:
        e = _char_energy(ch)
        if e == 0:
            continue
        key = str(9 if e == 0 else e)
        profile[key] += 1
    return profile


def _synthesize_sigil(text: str, style: str = "grid") -> str:
    """Create a simple visual representation of the energy profile.

    The default `grid` style renders a 3x3 grid where each cell
    contains the count of characters whose energy falls into that
    digital-root class. The top-left cell corresponds to energy 1,
    proceeding row-wise to energy 9. The header includes the digital
    root of the entire text and its total energy. A `bar` style
    renders counts as horizontal bars for each energy value.
    """
    total = sum(_char_energy(ch) for ch in text if not ch.isspace())
    dr = _digital_root(total) if total else 0
    prof = _energy_profile(text)
    if style == "grid":
        order = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        cells = [str(prof[k]) for k in order]
        rows = [" ".join(cells[i:i + 3]) for i in range(0, 9, 3)]
        title = f"DR={dr} TOTAL={total}"
        return title + "\n" + "\n".join(rows)
    if style == "bar":
        lines: List[str] = []
        for i in range(1, 10):
            k = str(i)
            count = prof[k]
            bar = "#" * min(count, 40)
            lines.append(f"{i}: {bar}")
        return "\n".join(lines)
    return f"DR={dr} TOTAL={total}"


def _read_input(text: str | None, file: str | None) -> str:
    """Load input text from either a direct string or a file.

    A direct string takes precedence. If both are None, stdin is read.
    """
    if text is not None:
        return text
    if file:
        return Path(file).read_text(encoding="utf-8")
    # Fallback to stdin
    return sys.stdin.read()


def _cmd_vectorize(args: argparse.Namespace) -> int:
    """Handle the `vectorize` subcommand.

    This command tokenizes the input into alphanumeric characters and
    prints their suite and binary representations. The output can be
    formatted as JSON or a simple table.
    """
    text = _read_input(args.input, args.file)
    # Use SymbolParser and SymbolMapper stages directly
    parser = SymbolParser()
    mapper = SymbolMapper()
    context: Dict[str, Any] = {}
    symbols = parser.process(text, context)
    mapped = mapper.process(symbols, context)
    if args.json:
        print(json.dumps(mapped, ensure_ascii=False, indent=2))
    else:
        # Print a simple table
        headers = ["idx", "symbol", "suite", "binary"]
        rows = [headers]
        for i, entry in enumerate(mapped):
            rows.append([str(i), entry["symbol"], entry["suite"], entry["binary"] or "None"])
        widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
        for row in rows:
            print("  ".join(row[i].ljust(widths[i]) for i in range(len(row))))
    return 0


def _cmd_analyze(args: argparse.Namespace) -> int:
    """Handle the `analyze` subcommand.

    The analysis runs the full GDk9 pipeline on the input text and
    reports the summary output. Optionally, it can also display the
    internal context metrics accumulated across stages.
    """
    text = _read_input(args.input, args.file)
    pipeline = GDk9Pipeline()
    context: Dict[str, Any] = {}
    result = pipeline.run(text, context=context)
    out = {
        "result": result,
        "metrics": {k: v for k, v in context.items() if k.endswith("_count") or k == "energy_sum"},
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print("Output:", result)
        print("Metrics:", out["metrics"])
    return 0


def _cmd_synthesize(args: argparse.Namespace) -> int:
    """Handle the `synthesize` subcommand.

    This generates a simple sigil/visualisation of the energy profile.
    Supported styles are `grid` (default) and `bar`. The output is
    printed directly to stdout.
    """
    text = _read_input(args.input, args.file)
    style = args.style or "grid"
    print(_synthesize_sigil(text, style=style))
    return 0


def _cmd_crdt_merge(args: argparse.Namespace) -> int:
    """Handle the `crdt-merge` subcommand.

    Merge two JSON objects using a Last-Write-Wins CRDT. The inputs are
    loaded from the provided file paths. The merged result and merge
    statistics are printed as JSON. The underlying merge logic comes
    from the gdk9.crdt module.
    """
    # Use the local CRDT merge implementation defined above. We avoid importing
    # gdk9.crdt here because the gdk9 package might not be installed in all
    # environments. Instead, the ``merge_maps`` function has been copied
    # directly into this script.
    if not args.left or not args.right:
        print("error: both --left and --right must be specified", file=sys.stderr)
        return 2
    left_path = Path(args.left)
    right_path = Path(args.right)
    try:
        left_data = json.loads(left_path.read_text(encoding="utf-8"))
        right_data = json.loads(right_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"error reading input files: {exc}", file=sys.stderr)
        return 2
    merged, stats, winners = merge_maps(left_data, right_data)
    payload = {
        "merged": merged,
        "stats": stats,
        "winners": winners,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def build_cli_parser() -> argparse.ArgumentParser:
    """Construct an argument parser for the GDk9 pipeline CLI.

    The top-level parser defines global options and subcommands for
    vectorisation, analysis, sigil synthesis and CRDT merging. Each
    subcommand has its own set of options documented in the help output.
    """
    parser = argparse.ArgumentParser(
        prog="gdk9_pipeline",
        description=(
            "GDk9 Pipeline CLI – analyse and visualise symbolic sequences with modular stages."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=False)
    # vectorize command
    vec = subparsers.add_parser("vectorize", help="Tokenize input and print suite/binary vectors")
    vec.add_argument("--input", "-i", help="Inline text input")
    vec.add_argument("--file", "-f", help="Path to text file input")
    vec.add_argument("--json", action="store_true", help="Output JSON instead of table")
    vec.set_defaults(func=_cmd_vectorize)
    # analyze command
    anl = subparsers.add_parser("analyze", help="Run full pipeline analysis on input text")
    anl.add_argument("--input", "-i", help="Inline text input")
    anl.add_argument("--file", "-f", help="Path to text file input")
    anl.add_argument("--json", action="store_true", help="Output JSON instead of human-readable")
    anl.set_defaults(func=_cmd_analyze)
    # synthesize command
    syn = subparsers.add_parser("synthesize", help="Create an energy sigil for the input text")
    syn.add_argument("--input", "-i", help="Inline text input")
    syn.add_argument("--file", "-f", help="Path to text file input")
    syn.add_argument("--style", "-s", choices=["grid", "bar"], default="grid", help="Visualisation style")
    syn.set_defaults(func=_cmd_synthesize)
    # crdt merge command
    cm = subparsers.add_parser("crdt-merge", help="Merge two JSON maps using LWW CRDTs")
    cm.add_argument("--left", "-L", help="Path to left JSON file", required=True)
    cm.add_argument("--right", "-R", help="Path to right JSON file", required=True)
    cm.set_defaults(func=_cmd_crdt_merge)
    return parser


def main(argv: List[str] | None = None) -> int:
    """Entrypoint for command-line execution.

    When invoked without subcommands, this function falls back to a
    demonstration of the pipeline on a sample string. Otherwise it
    dispatches to the appropriate subcommand handler.
    """
    parser = build_cli_parser()
    args = parser.parse_args(argv)
    # If no subcommand provided, show demo behaviour
    if not getattr(args, "command", None):
        sample = "GDK9 is awesome! 123"
        pipeline = GDk9Pipeline()
        context: Dict[str, Any] = {}
        output = pipeline.run(sample, context=context)
        print("Input:", sample)
        print("Output:", output)
        metrics = {k: v for k, v in context.items() if k.endswith("_count") or k == "energy_sum"}
        print("Context metrics:", metrics)
        return 0
    # Dispatch to subcommand
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 1
    return int(func(args))


if __name__ == "__main__":
    raise SystemExit(main())
