#!/usr/bin/env python3
"""CLI: saturate a small GDk9 DR fixture via egglog (fallback: gdk9.energy).

Usage:
  python -m gdk9.saturate
  python -m gdk9.saturate --values 26,10,9
  python -m gdk9.saturate --fallback-only
  gdk9-saturate
"""
from __future__ import annotations

import argparse
import json

DEFAULT_FIXTURE = (26, 10, 9)  # DR(26)+DR(10)+9 -> 8+1+9=18 -> 9


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="GDk9 egglog DR saturation spike")
    p.add_argument(
        "--values",
        default=",".join(str(v) for v in DEFAULT_FIXTURE),
        help="comma-separated energy totals (default: 26,10,9)",
    )
    p.add_argument(
        "--fallback-only",
        action="store_true",
        help="skip egglog; use gdk9.energy.digital_root only",
    )
    p.add_argument("--json", action="store_true", help="machine-readable output")
    args = p.parse_args(argv)

    values = [int(x.strip()) for x in args.values.split(",") if x.strip()]

    from gdk9.egglog_bridge.fallback import saturate_fallback

    fb = saturate_fallback(values)

    egg = None
    err = None
    if not args.fallback_only:
        try:
            from gdk9.egglog_bridge.dr_egglog import saturate_egglog

            egg = saturate_egglog(values)
        except Exception as exc:  # noqa: BLE001 — spike must report install/API failure
            err = f"{type(exc).__name__}: {exc}"

    verdict = "NO"
    if egg and egg.get("ok") and fb.get("ok") and egg.get("best_dr") == fb.get("best_dr"):
        verdict = "YES"
    elif args.fallback_only and fb.get("ok"):
        verdict = "FALLBACK-ONLY"
    elif err:
        verdict = "NO"

    payload = {
        "verdict": verdict,
        "fixture": values,
        "egglog": egg,
        "fallback": fb,
        "error": err,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("=== GDk9 egglog bridge spike: saturate ===")
        print(f"fixture: {values}")
        if egg:
            print(f"[egglog] before:    {egg['before']}")
            print(f"[egglog] after_sum: {egg['after_sum']}")
            print(f"[egglog] after_dr:  {egg['after_dr']}")
            print(f"[egglog] best_dr:   {egg['best_dr']}")
        if err:
            print(f"[egglog] ERROR: {err}")
        print(
            f"[fallback] total={fb['total']} folded={fb['folded_terms']} "
            f"best_dr={fb['best_dr']} congruence_dr={fb['congruence_dr']}"
        )
        print(f"VERDICT: {verdict}")
        if verdict == "YES":
            print("collapsed/best form:", egg["after_dr"] if egg else fb["best_dr"])

    return 0 if verdict in {"YES", "FALLBACK-ONLY"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
