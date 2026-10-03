#!/usr/bin/env python3
"""Watch a file for changes and re-analyze energy on every write.

Usage:
    python scripts/watch_file.py notes.txt
    python scripts/watch_file.py notes.txt --target 7 --interval 1.0

Polls the file's mtime at the given interval (default 1 second). On change,
prints timestamp, total energy, digital root, and delta from previous reading.
Press Ctrl-C to stop.
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path


def _setup_path() -> None:
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_setup_path()

from gdk9.principles import load_principle
from gdk9.energy import string_energy, digital_root as _dr


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _color(dr: int) -> str:
    colors = {1: "\033[91m", 2: "\033[93m", 3: "\033[92m",
              4: "\033[94m", 5: "\033[96m", 6: "\033[95m",
              7: "\033[33m", 8: "\033[34m", 9: "\033[97m"}
    reset = "\033[0m"
    return colors.get(dr, "") + str(dr) + reset


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Live energy watcher for a file.")
    p.add_argument("file", help="File to watch")
    p.add_argument("--interval", "-i", type=float, default=1.0, help="Poll interval in seconds")
    p.add_argument("--principle", "-P", help="Principle file")
    p.add_argument("--target", "-t", type=int, help="Target DR to highlight (1–9)")
    p.add_argument("--no-color", action="store_true", help="Disable ANSI color")
    args = p.parse_args(argv)

    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    principle = load_principle(args.principle)
    use_color = not args.no_color and sys.stdout.isatty()

    prev_mtime = None
    prev_total = None

    print(f"Watching: {path}  (Ctrl-C to stop)")
    print(f"{'Time':12}  {'Total':>8}  {'DR':>4}  {'Delta':>7}  {'Status'}")
    print("-" * 55)

    try:
        while True:
            try:
                mtime = path.stat().st_mtime
            except OSError:
                time.sleep(args.interval)
                continue

            if mtime != prev_mtime:
                text = _read(path)
                total, dr = string_energy(text, principle)
                ts = datetime.now().strftime("%H:%M:%S.%f")[:12]

                delta_s = "—"
                if prev_total is not None:
                    delta = total - prev_total
                    delta_s = f"{delta:+d}"
                    if use_color:
                        if delta > 0:
                            delta_s = f"\033[93m{delta_s}\033[0m"
                        elif delta < 0:
                            delta_s = f"\033[91m{delta_s}\033[0m"
                        else:
                            delta_s = f"\033[92m{delta_s}\033[0m"

                dr_s = _color(dr) if use_color else str(dr)

                status = ""
                if args.target:
                    if dr == args.target:
                        status = ("\033[92m✓ TARGET\033[0m" if use_color else "✓ TARGET")
                    else:
                        need = (args.target - _dr(total, True)) % 9 or 9
                        status = f"need DR+{need}"

                print(f"{ts:12}  {total:>8}  {dr_s:>4}  {delta_s:>7}  {status}")

                prev_mtime = mtime
                prev_total = total

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\nStopped.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
