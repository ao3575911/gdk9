GDk9 Pipeline


from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple

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


if __name__ == "__main__":
    # Demonstrate pipeline usage with sample input
    sample = "GDK9 is awesome! 123"
    pipeline = GDk9Pipeline()
    # Provide an empty context to collect metrics
    context: Dict[str, Any] = {}
    output = pipeline.run(sample, context=context)
    print("Input:", sample)
    print("Output:", output)
    # Print collected metrics stored in context
    metrics = {k: v for k, v in context.items() if k.endswith("_count") or k == "energy_sum"}
    print("Context metrics:", metrics)
