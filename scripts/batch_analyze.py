#!/usr/bin/env python3
"""Batch-analyze all .txt and .md files in a directory.

Usage:
    python scripts/batch_analyze.py [DIR] [--format csv|json] [--out FILE]

Outputs a report with per-file: path, total energy, digital root, word count,
and harmonic triad counts (root/wave/peak).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


def _setup_path() -> None:
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_setup_path()

from gdk9.principles import load_principle
from gdk9.energy import string_energy, harmonic_triads, analyze_text


EXTENSIONS = {".txt", ".md", ".rst", ".csv", ".log"}


def analyze_file(path: Path, principle) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return {"path": str(path), "error": str(e)}

    total, dr = string_energy(text, principle)
    harm = harmonic_triads(text, principle)
    result = analyze_text(text, principle)
    word_count = len(result.get("words", []))

    return {
        "path": str(path),
        "total": total,
        "dr": dr,
        "words": word_count,
        "chars": len(text),
        "root": harm["root"],
        "wave": harm["wave"],
        "peak": harm["peak"],
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Batch energy analysis of text files.")
    p.add_argument("directory", nargs="?", default=".", help="Directory to scan (default: .)")
    p.add_argument("--format", "-F", choices=["csv", "json"], default="csv")
    p.add_argument("--out", "-o", help="Output file (default: stdout)")
    p.add_argument("--principle", "-P", help="Custom principle file")
    p.add_argument("--recursive", "-r", action="store_true", help="Scan subdirectories")
    p.add_argument("--ext", help="Comma-separated extra extensions (e.g. '.py,.js')")
    args = p.parse_args(argv)

    principle = load_principle(args.principle)
    root_dir = Path(args.directory)

    if not root_dir.is_dir():
        print(f"error: {root_dir} is not a directory", file=sys.stderr)
        return 2

    exts = set(EXTENSIONS)
    if args.ext:
        for e in args.ext.split(","):
            exts.add(e.strip() if e.strip().startswith(".") else "." + e.strip())

    pattern = "**/*" if args.recursive else "*"
    files = [f for f in root_dir.glob(pattern) if f.is_file() and f.suffix in exts]
    files.sort()

    if not files:
        print(f"No files found in {root_dir} with extensions {sorted(exts)}", file=sys.stderr)
        return 0

    records = [analyze_file(f, principle) for f in files]

    out = open(args.out, "w", encoding="utf-8", newline="") if args.out else sys.stdout

    try:
        if args.format == "json":
            json.dump(records, out, indent=2, ensure_ascii=False)
            out.write("\n")
        else:
            fields = ["path", "total", "dr", "words", "chars", "root", "wave", "peak", "error"]
            writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for rec in records:
                writer.writerow(rec)
    finally:
        if args.out:
            out.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
