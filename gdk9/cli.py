from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict
from textwrap import dedent

from .energy import analyze_text, energy_profile, string_energy, vector_energy, harmonic_triads
from .errors import Gdk9Error, InputError, ConfigError, OptimizationError
from .io_utils import read_input
from .principles import Principle, load_principle
from .utilization import attune, sigil
from .tokenize import summarize_tokens_table, to_json_payload, annotate_text, delimiter_set
from .optimize import optimize_attunement, apply_plan, Plan, optimize_substitution, EditPlan, apply_edit_plan
from .log import logger
from .ansi import supports_color, colorize
from .fmt import Box, section, kv, fmt_dr, fmt_float_e, fmt_class, fmt_valid, fmt_form, energy_bar, vlen
from .state import load_state, save_state, list_symbols, set_symbol, merge_state, set_rule
from .imply import make_fusion, make_split, apply_rule, Rule
from .kernel_cli import run_kernel
from . import __version__
from .plugins.loader import (
  list_available as plugins_list_available,
  find_plugin as plugins_find,
  load_plugin as plugins_load,
  apply_plugin as plugins_apply,
  enable_plugin as plugins_enable,
  disable_plugin as plugins_disable,
  auto_boot as plugins_auto_boot,
  reset_config as plugins_reset_config,
)

class SmartFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
  pass


def print_table(rows: list[list[str]], use_color: bool = False) -> None:
  """Render rows[0] as header, remaining as data, with Unicode borders."""
  if not rows:
    return
  t = Box(rows[0], enabled=use_color)
  for row in rows[1:]:
    t.row(row)
  print(t.render())


def cmd_analyze(args: argparse.Namespace, principle: Principle, use_color: bool) -> int:
  text = read_input(args.text, args.file)
  result = analyze_text(text, principle)
  if args.format == "json":
    out: Dict[str, Any] = {}
    for k, units in result.items():
      out[k] = [u.__dict__ for u in units]
    if args.mode == "extended":
      out["vector"] = vector_energy(text, principle)
      out["harmonics"] = harmonic_triads(text, principle)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0
  # Table
  _unit_color = {"document": "bold", "paragraph": "white", "sentence": "dim", "word": None}
  t = Box(["unit", "value", "energy", "total"],
          col_align=["l", "l", "r", "r"], enabled=use_color)
  for k in ["document", "paragraphs", "sentences", "words"]:
    for u in result.get(k, []):
      val = (u.value[:48] + "…") if len(u.value) > 48 else u.value
      unit_s = colorize(u.unit, _unit_color.get(u.unit), use_color)
      e_s = fmt_dr(u.energy, use_color)
      t.row([unit_s, val, e_s, str(u.total)])
  print(t.render())
  if args.mode == "extended":
    vec  = vector_energy(text, principle)
    harm = harmonic_triads(text, principle)
    print()
    tv = Box(["vector", "letters", "digits", "symbols"],
             col_align=["l", "r", "r", "r"], enabled=use_color)
    tv.row(["sum", str(vec["sum"]["letters"]), str(vec["sum"]["digits"]), str(vec["sum"]["symbols"])])
    tv.row(["dr",
            fmt_dr(vec["dr"]["letters"], use_color),
            fmt_dr(vec["dr"]["digits"],  use_color),
            fmt_dr(vec["dr"]["symbols"], use_color)])
    print(tv.render())
    print()
    th = Box(["harmonics", "root", "wave", "peak"],
             col_align=["l", "r", "r", "r"], enabled=use_color)
    th.row(["counts",
            colorize(str(harm["root"]), "cyan",    use_color),
            colorize(str(harm["wave"]), "yellow",  use_color),
            colorize(str(harm["peak"]), "magenta", use_color)])
    print(th.render())
  return 0


def cmd_profile(args: argparse.Namespace, principle: Principle, use_color: bool) -> int:
  text = read_input(args.text, args.file)
  prof = energy_profile(text, principle)
  total, dr = string_energy(text, principle)
  if args.format == "json":
    print(json.dumps({"profile": prof, "total": total, "dr": dr}, indent=2))
    return 0
  max_cnt = max(int(v) for v in prof.values()) or 1
  t = Box(["dr", "cnt", ""], col_align=["c", "r", "l"], enabled=use_color)
  for i in range(1, 10):
    cnt = int(prof[str(i)])
    dr_s  = fmt_dr(i, use_color)
    cnt_s = colorize(str(cnt), "dim" if cnt == 0 else None, use_color)
    bar   = energy_bar(i, cnt, max_cnt, bar_width=22, enabled=use_color)
    t.row([dr_s, cnt_s, bar])
  print(t.render())
  print(kv("total", str(total), use_color) + "  " + kv("dr", fmt_dr(dr, use_color), use_color))
  return 0


def cmd_assign(args: argparse.Namespace, principle: Principle, use_color: bool) -> int:
  text = read_input(args.text, args.file)
  from .energy import char_energy
  t = Box(["char", "energy"], col_align=["c", "r"], enabled=use_color)
  for ch in text:
    if ch == "\n":
      continue
    e = char_energy(ch, principle)
    t.row([colorize(repr(ch)[1:-1], "bold", use_color), fmt_dr(e, use_color)])
  print(t.render())
  return 0


def cmd_attune(args: argparse.Namespace, principle: Principle, use_color: bool) -> int:
  text = read_input(args.text, args.file)
  try:
    if args.method in {"append", "prepend", "intersperse"}:
      plan = optimize_attunement(
        text,
        args.target,
        principle,
        allowed_symbols=args.allowed,
        method=args.method,
        max_steps=args.max_steps,
      )
      logger.debug("plan", plan)
      out_text = apply_plan(text, plan, spread=args.spread)
    elif args.method in {"substitute", "edit"}:
      subs = None
      if args.subs_file:
        import pathlib
        subs_data = json.loads(pathlib.Path(args.subs_file).read_text(encoding='utf-8'))
        subs = subs_data.get('subs') if isinstance(subs_data, dict) else None
        allowed_inserts = subs_data.get('allowed_inserts') if isinstance(subs_data, dict) else None
      else:
        allowed_inserts = args.allowed
      eplan = optimize_substitution(
        text,
        args.target,
        principle,
        subs=subs,
        allow_delete=bool(args.allow_delete),
        allowed_inserts=allowed_inserts,
        max_edits=args.max_steps,
      )
      logger.debug("edit-plan", eplan)
      out_text = apply_edit_plan(text, eplan)
    else:
      # Fallback to legacy single-symbol append
      new_text, total, dr, count = attune(text, args.target, principle, symbol=args.symbol)
      plan = Plan("append", args.target, [(args.symbol, count)], total - (count * 0), 0, total, dr)
      out_text = new_text
  except ValueError as exc:
    raise InputError(str(exc))
  if args.in_place and args.file:
    import pathlib
    pathlib.Path(args.file).write_text(out_text, encoding="utf-8")
  if args.output == "text":
    print(out_text)
    return 0
  if args.method in {"append", "prepend", "intersperse"}:
    payload = {
      "plan": {"method": plan.method, "target": plan.target, "steps": plan.steps},
      "before": {"total": plan.total_before, "dr": plan.dr_before},
      "after": {"total": plan.total_after, "dr": plan.dr_after},
      "attuned": out_text if args.include_text else None,
    }
  else:
    # Edit plan payload
    total_before, dr_before = string_energy(text, principle)
    total_after, dr_after = string_energy(out_text, principle)
    payload = {
      "plan": {
        "method": "edit",
        "ops": [op.__dict__ for op in eplan.ops],
      },
      "before": {"total": total_before, "dr": dr_before},
      "after": {"total": total_after, "dr": dr_after},
      "attuned": out_text if args.include_text else None,
    }
  print(json.dumps(payload, ensure_ascii=False, indent=2))
  return 0


def cmd_compare(args: argparse.Namespace, principle: Principle, use_color: bool) -> int:
  left  = read_input(args.left,  args.left_file)
  right = read_input(args.right, args.right_file)
  ltot, ldr = string_energy(left,  principle)
  rtot, rdr = string_energy(right, principle)
  delta = rtot - ltot
  t = Box(["side", "total", "dr"], col_align=["l", "r", "r"], enabled=use_color)
  t.row([colorize("left",  "dim",  use_color), str(ltot), fmt_dr(ldr, use_color)])
  t.row([colorize("right", "bold", use_color), str(rtot), fmt_dr(rdr, use_color)])
  print(t.render())
  if delta == 0:
    delta_s = colorize("0", "bright_green", use_color)
  elif delta > 0:
    delta_s = colorize(f"+{delta}", "yellow", use_color)
  else:
    delta_s = colorize(str(delta), "red", use_color)
  print(kv("delta", delta_s, use_color))
  return 0


def cmd_encode(args: argparse.Namespace, principle: Principle) -> int:
  text = read_input(args.text, args.file)
  from .energy import char_energy

  if args.style == "annotate":
    out = []
    for ch in text:
      e = char_energy(ch, principle)
      out.append(f"{ch}[{e}]")
    print("".join(out))
    return 0
  if args.style == "json":
    from .energy import analyze_text as at

    res = at(text, principle)
    payload = {k: [u.__dict__ for u in v] for k, v in res.items()}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0
  raise InputError("Unknown encode style.")


def cmd_decode(args: argparse.Namespace, principle: Principle) -> int:  # pragma: no cover - trivial
  text = read_input(args.text, args.file)
  # Remove simple [n] annotations
  import re

  print(re.sub(r"\[(?:[1-9])\]", "", text))
  return 0


def cmd_synthesize(args: argparse.Namespace, principle: Principle, use_color: bool) -> int:
  text  = read_input(args.text, args.file)
  raw   = sigil(text, principle, style=args.style)
  total, dr = string_energy(text, principle)
  if not use_color:
    print(raw)
    return 0
  lines = raw.splitlines()
  # Colour the header line (DR= TOTAL=) and each cell value
  out = []
  for line in lines:
    if line.startswith("DR="):
      parts = line.split()
      header = "  ".join(
        kv(p.split("=")[0], colorize(p.split("=")[1], "bright_white", True), True)
        for p in parts if "=" in p
      )
      out.append(header)
    else:
      # Colour each digit in grid/bar lines by its DR value
      coloured = ""
      for ch in line:
        if ch.isdigit() and ch != "0":
          coloured += fmt_dr(int(ch), True)
        elif ch == "0":
          coloured += colorize("0", "dim", True)
        elif ch == "#":
          dr_v = int(line[0]) if line and line[0].isdigit() else 9
          coloured += colorize(ch, "bright_white", True)
        else:
          coloured += colorize(ch, "dim", True) if ch in ":-" else ch
      out.append(coloured)
  # Frame the sigil
  inner_w = max(vlen(l) for l in out) if out else 20
  h_bar   = "─" * (inner_w + 4)
  b       = lambda s: colorize(s, "dim", True)
  print(b("┌" + h_bar + "┐"))
  for l in out:
    pad_r = " " * max(0, inner_w - vlen(l))
    print(b("│") + "  " + l + pad_r + "  " + b("│"))
  print(b("└" + h_bar + "┘"))
  return 0


def cmd_principles(args: argparse.Namespace, current: Principle) -> int:
  if args.action == "show":
    payload = {
      "name": current.name,
      "description": current.description,
      "letter_mode": current.letter_mode,
      "number_mode": current.number_mode,
      "normalize_zero_to_nine": current.normalize_zero_to_nine,
      "symbol_energy": current.symbol_energy,
    }
    print(json.dumps(payload, indent=2))
    return 0
  if args.action == "validate":
    try:
      _ = load_principle(args.file)
    except ConfigError as exc:
      print(f"invalid: {exc}")
      return 2
    print("ok")
    return 0
  if args.action == "install":
    if not args.file:
      raise InputError("--file is required for install")
    import shutil
    from pathlib import Path
    try:
      # Validate first
      _ = load_principle(args.file)
      here = Path(__file__).parent
      dst = here / 'data' / 'official.json'
      dst.write_text(Path(args.file).read_text(encoding='utf-8'), encoding='utf-8')
      print(str(dst))
      return 0
    except Exception as exc:
      raise ConfigError(f"Install failed: {exc}")
  raise InputError("Unsupported principles action")


def cmd_optimize(args: argparse.Namespace, principle: Principle) -> int:
  text = read_input(args.text, args.file)
  try:
    plan = optimize_attunement(
      text,
      args.target,
      principle,
      allowed_symbols=args.allowed,
      method=args.method,
      max_steps=args.max_steps,
    )
  except ValueError as exc:
    raise OptimizationError(str(exc))
  print(
    json.dumps(
      {
        "method": plan.method,
        "target": plan.target,
        "steps": plan.steps,
        "before": {"total": plan.total_before, "dr": plan.dr_before},
        "after": {"total": plan.total_after, "dr": plan.dr_after},
      },
      ensure_ascii=False,
      indent=2,
    )
  )
  return 0


def build_parser() -> argparse.ArgumentParser:
  p = argparse.ArgumentParser(
    prog="gdk9",
    description=(
      "Gdk9 — symbolic energy tools: analyze, tokenize, attune, and compose rules."
    ),
    formatter_class=SmartFormatter,
    epilog=dedent(
      """
      Examples:
        gdk9 an "Hello, world"                 # quick analysis
        gdk9 tok "<alpha|beta>" -e 1 -F table  # tokenize by energy-1 delimiters
        gdk9 att "phrase" -t 7 -m append -a ".!?" --include-text
        gdk9 sym add NAME 12.5 -S ./state.json  # manage symbols
        gdk9 im ds SPL X1 X2 0.5                # define split rule
        gdk9 im ap SPL X --commit               # apply rule and persist
        gdk9 state merge -i peer.json           # CRDT-merge a peer state
      """
    ),
  )
  p.add_argument(
    "--principle",
    "-P",
    help="Principle file (JSON/YAML). Defaults to built-in Ninefold Grid.",
  )
  p.add_argument(
    "--state",
    "-S",
    help="State file for symbols/rules (default ~/.gdk9/state.json)",
  )
  p.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
  p.add_argument(
    "--version",
    action="version",
    version=(
      f"gdk9 {__version__} — License: AGPL-3.0-or-later\n"
      f"Copyright Adam Grange | adamgrange@proton.me"
    ),
  )
  color_group = p.add_mutually_exclusive_group()
  color_group.add_argument("--color", "-C", action="store_true", help="Force color output")
  color_group.add_argument("--no-color", "-N", action="store_true", help="Disable color output")
  sub = p.add_subparsers(dest="cmd", required=True)

  a = sub.add_parser("analyze", aliases=["an"], help="Analyze text into energies (document→paragraphs→sentences→words)")
  a.add_argument("text", nargs="?", help="Inline text (or use --file or stdin)")
  a.add_argument("--file", "-f", help="Read text from file path")
  a.add_argument("--format", "-F", choices=["table", "json"], default="table", help="Output format")
  a.add_argument("--mode", "-m", choices=["core", "extended"], default="core", help="Include vectors/harmonics in extended mode")

  pr = sub.add_parser("profile", aliases=["prof"], help="Show energy histogram and totals for text")
  pr.add_argument("text", nargs="?")
  pr.add_argument("--file", "-f")
  pr.add_argument("--format", "-F", choices=["table", "json"], default="table", help="Output format")

  asg = sub.add_parser("assign", aliases=["asg"], help="List per-character energy assignments for given text")
  asg.add_argument("text", nargs="?")
  asg.add_argument("--file", "-f")

  att = sub.add_parser("attune", aliases=["att"], help="Adjust text to a target digital-root energy")
  att.add_argument("text", nargs="?")
  att.add_argument("--file", "-f")
  att.add_argument("--target", "-t", type=int, required=True, help="Target energy 1..9")
  att.add_argument("--method", "-m", choices=["append", "prepend", "intersperse", "substitute", "edit"], default="append", help="Attunement method")
  att.add_argument("--allowed", "-a", help="Allowed symbols to use (e.g. '.!?*')")
  att.add_argument("--symbol", default=".", help="Legacy single-symbol fallback")
  att.add_argument("--max-steps", "-s", type=int, default=64, help="Max steps/edits to consider")
  att.add_argument("--spread", "-p", type=int, help="For intersperse, approximate insertion interval")
  att.add_argument("--subs-file", "-S", help="JSON file mapping chars to replacement arrays for substitution/edit")
  att.add_argument("--allow-delete", action="store_true", help="Allow deletions in edit planning")
  att.add_argument("--output", "-o", choices=["json", "text"], default="json", help="Result output type")
  att.add_argument("--include-text", "-I", action="store_true", help="Include attuned text in JSON output")
  att.add_argument("--in-place", "-w", action="store_true", help="Write result back to --file in-place")

  cmp_p = sub.add_parser("compare", aliases=["cmp"], help="Compare total and DR between two inputs")
  cmp_p.add_argument("left", nargs="?")
  cmp_p.add_argument("--left-file", "-L")
  cmp_p.add_argument("right", nargs="?")
  cmp_p.add_argument("--right-file", "-R")

  enc = sub.add_parser("encode", aliases=["enc"], help="Encode text with energy annotations")
  enc.add_argument("text", nargs="?")
  enc.add_argument("--file", "-f")
  enc.add_argument("--style", "-s", choices=["annotate", "json"], default="annotate")

  dec = sub.add_parser("decode", aliases=["dec"], help="Strip simple energy annotations like [3]")
  dec.add_argument("text", nargs="?")
  dec.add_argument("--file", "-f")

  syn = sub.add_parser("synthesize", aliases=["sig"], help="Create a sigil/visual from energy profile")
  syn.add_argument("text", nargs="?")
  syn.add_argument("--file", "-f")
  syn.add_argument("--style", "-s", choices=["grid", "bar"], default="grid")

  tok = sub.add_parser("tokenize", aliases=["tok"], help="Tokenize text by symbol-energy delimiters")
  tok.add_argument("text", nargs="?")
  tok.add_argument("--file", "-f")
  tok.add_argument("--energy", "-e", type=int, default=1, help="Delimiter energy value to use")
  tok.add_argument("--delims", "-d", help="Override delimiter set (e.g., '<>|')")
  tok.add_argument("--keep-delims", "-k", action="store_true", help="Keep delimiters in output tokens")
  tok.add_argument("--drop-delims", "-D", action="store_true", help="Drop delimiters from output tokens")
  tok.add_argument("--no-strip", "-n", action="store_true", help="Do not strip whitespace from tokens")
  tok.add_argument("--no-footer", "-x", action="store_true", help="Suppress summary and delimiter footer")
  tok.add_argument("--summary-only", "-u", action="store_true", help="Only print summary/metrics (no table body)")
  tok.add_argument(
    "-F", "--format",
    choices=["table", "json", "annotate"],
    default="table",
    help="Output format",
  )

  prc = sub.add_parser("principles", aliases=["prin"], help="Work with principles (show/validate/install)")
  prc.add_argument("action", choices=["show", "validate", "install"])
  prc.add_argument("--file", help="Principle file for validation/installation")

  opt = sub.add_parser("optimize", aliases=["opt"], help="Compute minimal-step plan to reach target")
  opt.add_argument("text", nargs="?")
  opt.add_argument("--file", "-f")
  opt.add_argument("--target", type=int, required=True)
  opt.add_argument("--method", choices=["append", "prepend", "intersperse"], default="append")
  opt.add_argument("--allowed", help="Allowed symbols (e.g., '.!?*+')")
  opt.add_argument("--max-steps", type=int, default=64)

  tui = sub.add_parser("tui", aliases=["ui"], help="Interactive live analysis (curses-based)")
  tui.add_argument("--target", type=int, default=9)
  tui.add_argument("--allowed", default=".!?*+")
  tui.add_argument("--method", choices=["append", "prepend", "intersperse"], default="append")

  subs = sub.add_parser("subs", aliases=["sub"], help="Work with substitution profiles")
  subs.add_argument("action", choices=["generate", "example"]) 
  subs.add_argument("--output", "-o", help="Write to file instead of stdout")
  subs.add_argument("--limit", "-l", type=int, default=3, help="Max suggestions per char")

  sym = sub.add_parser("symbol", aliases=["sym"], help="Manage symbols")
  sym_sub = sym.add_subparsers(dest="symbol_cmd", required=True)
  sym_add = sym_sub.add_parser("add", help="Add or update a symbol")
  sym_add.add_argument("name")
  sym_add.add_argument("energy", type=float)
  sym_list = sym_sub.add_parser("list", aliases=["ls"], help="List symbols")

  imp = sub.add_parser("imply", aliases=["im"], help="Define and apply rules")
  imp_sub = imp.add_subparsers(dest="imply_cmd", required=True)
  imp_df = imp_sub.add_parser("define-fusion", aliases=["df", "fuse"], help="Define fusion rule")
  imp_df.add_argument("rule")
  imp_df.add_argument("out_name")
  imp_df.add_argument("arity", type=int)
  imp_ds = imp_sub.add_parser("define-split", aliases=["ds", "split"], help="Define split rule")
  imp_ds.add_argument("rule")
  imp_ds.add_argument("out_a")
  imp_ds.add_argument("out_b")
  imp_ds.add_argument("ratio", type=float)
  imp_list = imp_sub.add_parser("list", aliases=["ls"], help="List rules")
  imp_ap = imp_sub.add_parser("apply", aliases=["ap"], help="Apply rule to input symbol names")
  imp_ap.add_argument("rule")
  imp_ap.add_argument("inputs", nargs="+")
  imp_ap.add_argument("--commit", action="store_true", help="Persist outputs into state symbols")

  ker = sub.add_parser(
    "kernel",
    aliases=["kn"],
    help="Pure kernel smoke path: eval / apply / search (no state I/O)",
  )
  ker_sub = ker.add_subparsers(dest="kernel_cmd", required=True)
  ker_eval = ker_sub.add_parser("eval", aliases=["ev"], help="Evaluate text under KernelPrinciple")
  ker_eval.add_argument("text", help="Input text (each character becomes a symbol)")
  ker_ap = ker_sub.add_parser("apply", aliases=["ap"], help="Apply a builtin fuse/split rule")
  ker_ap.add_argument("rule", help="Builtin rule name: fuse | split")
  ker_ap.add_argument("symbols", nargs="+", help="Ordered symbol names to transform")
  ker_ap.add_argument("--parts", help="Comma-separated split output names (split only)")
  ker_ap.add_argument("--energies", help="Comma-separated split output energies (split only)")
  ker_se = ker_sub.add_parser("search", aliases=["find"], help="Bounded implication search (engine.infer)")
  ker_se.add_argument("source", nargs="+", help="Source symbol names")
  ker_se.add_argument("--target", nargs="+", required=True, help="Target symbol names")
  ker_se.add_argument("--max-depth", type=int, default=4, help="Maximum implication depth")
  ker_se.add_argument(
    "--rules",
    nargs="+",
    default=["fuse"],
    help="Builtin rules to enable (default: fuse)",
  )
  ker_se.add_argument("--parts", help="Comma-separated split output names when using split")
  ker_se.add_argument("--energies", help="Comma-separated split output energies when using split")

  repl = sub.add_parser("repl", aliases=["sh"], help="Interactive REPL for symbols and imply")

  # plugin management
  pl = sub.add_parser("plugin", aliases=["pl"], help="Manage and load plugins (rule packs/grammars)")
  pl_sub = pl.add_subparsers(dest="plugin_cmd", required=True)
  pl_list = pl_sub.add_parser("list", help="List discovered plugins in search paths")
  pl_val = pl_sub.add_parser("validate", help="Validate a plugin pack (YAML/JSON/Python)")
  pl_val.add_argument("name_or_path")
  pl_info = pl_sub.add_parser("info", help="Show plugin metadata")
  pl_info.add_argument("name_or_path")
  pl_load = pl_sub.add_parser("load", help="Load plugin into current state and enable for auto-boot")
  pl_load.add_argument("name_or_path")
  pl_load.add_argument("--no-enable", action="store_true", help="Do not enable for auto-boot")
  pl_en = pl_sub.add_parser("enable", help="Enable plugin for auto-boot by name or path")
  pl_en.add_argument("name_or_path")
  pl_dis = pl_sub.add_parser("disable", help="Disable plugin by name")
  pl_dis.add_argument("name")

  # rich help
  hp = sub.add_parser("help", aliases=["h"], help="Show help or subcommand help (e.g. 'gdk9 help plugin')")
  hp.add_argument("topic", nargs="?", help="Optional topic or subcommand name")
  hb = sub.add_parser("handbook", aliases=["hb"], help="Print comprehensive handbook (EN + RU)")

  # reset/clear
  rst = sub.add_parser("reset", aliases=["clear"], help="Reset state/config to defaults for a fresh start")
  rst.add_argument("--state", "-S", help="State file to reset (default ~/.gdk9/state.json)")
  rst.add_argument("--plugins", action="store_true", help="Reset plugin auto-boot config only (unless combined)")
  rst.add_argument("--all", action="store_true", help="Reset both state and plugins")
  rst.add_argument("--rules-only", action="store_true", help="Only clear rules in state (keep symbols)")
  rst.add_argument("--symbols-only", action="store_true", help="Only clear symbols in state (keep rules)")
  rst.add_argument("--yes", "-y", action="store_true", help="Do not prompt for confirmation")

  st = sub.add_parser("state", help="CRDT-aware state management")
  st_sub = st.add_subparsers(dest="state_cmd", required=True)
  st_merge = st_sub.add_parser("merge", help="Merge another state file into the current one using LWW CRDTs")
  st_merge.add_argument("--incoming", "-i", required=True, help="Path to incoming state file")
  st_merge.add_argument("--dry-run", action="store_true", help="Show merge result without writing")

  # dcg — Directed Cognition Graph
  dcg = sub.add_parser("dcg", help="Directed Cognition Graph: classify, path, vector, shortest, homotopy, info")
  dcg_sub = dcg.add_subparsers(dest="dcg_cmd", required=True)

  dcg_cls = dcg_sub.add_parser("classify", aliases=["cls"], help="Show symmetry class and SymPhi energy for each letter")
  dcg_cls.add_argument("text", help="Text to classify (only alphabetic characters are processed)")
  dcg_cls.add_argument("--format", "-F", choices=["table", "json"], default="table")

  dcg_path = dcg_sub.add_parser("path", aliases=["p"], help="Analyse word as a DCG path and show per-step edge validity")
  dcg_path.add_argument("word")
  dcg_path.add_argument("--format", "-F", choices=["table", "json"], default="table")

  dcg_vec = dcg_sub.add_parser("vector", aliases=["vec"], help="Show 4D vector sum for a word")
  dcg_vec.add_argument("word")
  dcg_vec.add_argument("--format", "-F", choices=["table", "json"], default="table")

  dcg_sp = dcg_sub.add_parser("shortest", aliases=["sp"], help="Shortest DCG path between two letters (Dijkstra)")
  dcg_sp.add_argument("src", help="Source letter")
  dcg_sp.add_argument("dst", help="Destination letter")
  dcg_sp.add_argument("--format", "-F", choices=["table", "json"], default="table")

  dcg_hom = dcg_sub.add_parser("homotopy", aliases=["hom"], help="Check homotopy equivalence of two words")
  dcg_hom.add_argument("word_a")
  dcg_hom.add_argument("word_b")
  dcg_hom.add_argument("--tol", type=float, default=1.0, help="Energy and vector-distance tolerance (default 1.0)")
  dcg_hom.add_argument("--format", "-F", choices=["table", "json"], default="table")

  dcg_info = dcg_sub.add_parser("info", help="Show DCG graph statistics")
  dcg_info.add_argument("--format", "-F", choices=["table", "json"], default="table")

  # crypto (experimental)
  cr = sub.add_parser("crypto", aliases=["crypt"], help="Experimental ciphers: edpc (playful) or secure (requires 'cryptography')")
  cr_sub = cr.add_subparsers(dest="crypto_cmd", required=True)
  cr_enc = cr_sub.add_parser("encrypt", help="Encrypt text with a key")
  cr_enc.add_argument("text", nargs="?")
  cr_enc.add_argument("--file", "-f")
  cr_enc.add_argument("--key", "-k", required=True)
  cr_enc.add_argument("--mode", "-m", choices=["edpc", "secure"], default="edpc")
  cr_dec = cr_sub.add_parser("decrypt", help="Decrypt text with a key")
  cr_dec.add_argument("text", nargs="?")
  cr_dec.add_argument("--file", "-f")
  cr_dec.add_argument("--key", "-k", required=True)
  cr_dec.add_argument("--mode", "-m", choices=["edpc", "secure"], default="edpc")

  return p


def main(argv: list[str] | None = None) -> int:
  parser = build_parser()
  args = parser.parse_args(argv)
  try:
    logger.set_enabled(bool(args.debug))
    use_color = (getattr(args, "color", False)) or (supports_color() and not getattr(args, "no_color", False))
    principle = load_principle(args.principle)
    state_path = getattr(args, "state", None)
    # Auto-boot enabled plugins (merge symbol_energy and rules into state/principle)
    state_aut = load_state(state_path)
    principle, state_aut, loaded_plugins = plugins_auto_boot(principle, state_aut)
    if loaded_plugins:
      save_state(state_aut, state_path)
    if args.cmd == "analyze":
      return cmd_analyze(args, principle, use_color)
    if args.cmd == "profile":
      return cmd_profile(args, principle, use_color)
    if args.cmd == "assign":
      return cmd_assign(args, principle, use_color)
    if args.cmd == "attune":
      return cmd_attune(args, principle, use_color)
    if args.cmd == "compare":
      return cmd_compare(args, principle, use_color)
    if args.cmd == "encode":
      return cmd_encode(args, principle)
    if args.cmd == "decode":
      return cmd_decode(args, principle)
    if args.cmd == "synthesize":
      return cmd_synthesize(args, principle, use_color)
    if args.cmd == "dcg":
      from .dcg import (
        get_dcg, symmetry_class, sym_energy, vectorize,
        word_sym_energy, word_vector, homotopy_equivalent,
      )
      g   = get_dcg()
      fmt = getattr(args, "format", "table")

      # ── classify ──────────────────────────────────────────────────────────
      if args.dcg_cmd in ("classify", "cls"):
        letters = [c for c in args.text if c.isalpha()]
        if not letters:
          raise InputError("No alphabetic characters in input")
        records = []
        for ch in letters:
          sc  = symmetry_class(ch)
          e   = sym_energy(ch)
          vec = vectorize(ch)
          records.append({"char": ch, "class": sc, "energy": round(e, 6),
                          "vector": [round(x, 6) for x in vec]})
        if fmt == "json":
          print(json.dumps(records, ensure_ascii=False, indent=2))
          return 0
        print(section("dcg · classify", enabled=use_color))
        t = Box(["char", "form", "class", "energy",
                 "v₀ pos", "v₁ tid", "v₂ √E", "v₃ sinθ"],
                col_align=["c", "c", "l", "r", "r", "r", "r", "r"],
                enabled=use_color)
        for r in records:
          ch  = r["char"]
          sc  = r["class"]
          e   = r["energy"]
          vec = r["vector"]
          form = "DC" if ch.isupper() else "ac"
          form_s = colorize("DC", "bold", use_color) if ch.isupper() \
                   else colorize("ac", "dim", use_color)
          t.row([colorize(ch, "bold", use_color),
                 form_s,
                 fmt_class(sc, use_color),
                 fmt_float_e(e, use_color),
                 colorize(f"{vec[0]:.1f}", "dim",   use_color),
                 colorize(f"{vec[1]:.0f}", "dim",   use_color),
                 colorize(f"{vec[2]:.4f}", "cyan",  use_color),
                 colorize(f"{vec[3]:.4f}", "yellow",use_color)])
        print(t.render())
        return 0

      # ── path ──────────────────────────────────────────────────────────────
      if args.dcg_cmd in ("path", "p"):
        info = g.word_path_info(args.word)
        if fmt == "json":
          print(json.dumps(info, ensure_ascii=False, indent=2))
          return 0
        print(section("dcg · path", enabled=use_color))
        steps = info["steps"]
        t = Box(["#", "char", "class", "energy", "from", "✓"],
                col_align=["r", "c", "l", "r", "c", "c"], enabled=use_color)
        invalid_count = 0
        for i, s in enumerate(steps):
          ef = colorize(s.get("edge_from", "—"), "dim", use_color)
          if "valid_step" not in s:
            val_s = colorize("—", "dim", use_color)
          else:
            v = s["valid_step"]
            val_s = fmt_valid(v, use_color)
            if not v:
              invalid_count += 1
          t.row([colorize(str(i), "dim", use_color),
                 colorize(s["char"], "bold", use_color),
                 fmt_class(s["class"], use_color),
                 fmt_float_e(s["energy"], use_color),
                 ef, val_s])
        print(t.render())
        if info["is_valid_path"]:
          path_s = fmt_valid(True, use_color) + colorize(" valid path", "bright_green", use_color)
        else:
          path_s = fmt_valid(False, use_color) + colorize(f" {invalid_count} invalid step(s)", "bright_red", use_color)
        e_s = colorize(f"{info['total_energy']:.4f}", "bright_white", use_color)
        print(kv("energy", e_s, use_color) + "   " + path_s)
        print(kv("vector", colorize(str([round(x,3) for x in info["vector_sum"]]), "dim", use_color), use_color))
        return 0

      # ── vector ────────────────────────────────────────────────────────────
      if args.dcg_cmd in ("vector", "vec"):
        vec = word_vector(args.word)
        e   = word_sym_energy(args.word)
        if fmt == "json":
          print(json.dumps({"word": args.word, "total_energy": round(e, 6),
                            "vector": [round(x, 6) for x in vec]}, indent=2))
          return 0
        print(section("dcg · vector", enabled=use_color))
        labels = ["pos_sum", "type_id_sum", "√E_sum", "sinθ_sum"]
        colors = ["white", "dim", "cyan", "yellow"]
        t = Box(["dim", "label", "value"], col_align=["c", "l", "r"], enabled=use_color)
        for i, (lbl, col, val) in enumerate(zip(labels, colors, vec)):
          t.row([colorize(str(i), "dim", use_color),
                 colorize(lbl, col, use_color),
                 colorize(f"{val:.4f}", "bright_white", use_color)])
        print(t.render())
        print(kv("total_energy", fmt_float_e(e, use_color), use_color))
        return 0

      # ── shortest ──────────────────────────────────────────────────────────
      if args.dcg_cmd in ("shortest", "sp"):
        if len(args.src) != 1 or not args.src.isalpha():
          raise InputError("src must be a single alphabetic character")
        if len(args.dst) != 1 or not args.dst.isalpha():
          raise InputError("dst must be a single alphabetic character")
        path = g.shortest_path(args.src, args.dst)
        if path is None:
          raise InputError(f"No path from {args.src!r} to {args.dst!r}")
        cost = g.shortest_path_cost(args.src, args.dst)
        if fmt == "json":
          detail = [{"char": c, "class": symmetry_class(c), "energy": round(sym_energy(c), 6)}
                    for c in path]
          print(json.dumps({"src": args.src, "dst": args.dst, "path": detail,
                            "length": len(path), "cost": cost}, indent=2))
          return 0
        print(section("dcg · shortest path", enabled=use_color))
        t = Box(["#", "char", "class", "energy", "cost"],
                col_align=["r", "c", "l", "r", "r"], enabled=use_color)
        for i, ch in enumerate(path):
          w = g.edge_weight(path[i-1], ch) if i > 0 else None
          w_s = colorize(f"{w:.1f}", "dim", use_color) if w else colorize("—", "dim", use_color)
          t.row([colorize(str(i), "dim", use_color),
                 colorize(ch, "bold", use_color),
                 fmt_class(symmetry_class(ch), use_color),
                 fmt_float_e(sym_energy(ch), use_color),
                 w_s])
        print(t.render())
        # Arrow chain
        arrow = colorize(" → ", "dim", use_color)
        chain = arrow.join(colorize(c, "bold", use_color) for c in path)
        print(chain)
        print(kv("length", colorize(str(len(path)), "bright_white", use_color), use_color)
              + "   " + kv("cost", colorize(f"{cost:.1f}", "yellow", use_color), use_color))
        return 0

      # ── homotopy ──────────────────────────────────────────────────────────
      if args.dcg_cmd in ("homotopy", "hom"):
        equiv, detail = homotopy_equivalent(args.word_a, args.word_b, tol=args.tol)
        if fmt == "json":
          print(json.dumps(detail, indent=2))
          return 0
        print(section("dcg · homotopy", enabled=use_color))
        wa_s = colorize(args.word_a, "bold",    use_color)
        wb_s = colorize(args.word_b, "cyan",    use_color)
        t = Box(["metric", wa_s, wb_s, ""],
                col_align=["l", "r", "r", "l"], enabled=use_color)
        t.row([colorize("energy",          "dim", use_color),
               colorize(str(detail["word_a"]["energy"]), "cyan",   use_color),
               colorize(str(detail["word_b"]["energy"]), "cyan",   use_color), ""])
        t.divider()
        t.row([colorize("energy_diff",     "dim", use_color),
               colorize(str(detail["energy_diff"]),     "yellow",  use_color), "", ""])
        t.row([colorize("vector_distance", "dim", use_color),
               colorize(str(detail["vector_distance"]), "yellow",  use_color), "", ""])
        print(t.render())
        if equiv:
          verdict = (fmt_valid(True,  use_color) + "  "
                     + colorize("EQUIVALENT", "bright_green", use_color)
                     + colorize(f"  (tol={args.tol})", "dim", use_color))
        else:
          verdict = (fmt_valid(False, use_color) + "  "
                     + colorize("NOT equivalent", "bright_red",   use_color)
                     + colorize(f"  (tol={args.tol})", "dim",     use_color))
        print("  " + verdict)
        return 0

      # ── info ──────────────────────────────────────────────────────────────
      if args.dcg_cmd == "info":
        nc      = g.node_count()
        ec      = g.edge_count()
        by_type = g.edge_count_by_type()
        if fmt == "json":
          print(json.dumps({"nodes": nc, "edges": ec, "edges_by_type": by_type}, indent=2))
          return 0
        print(section("dcg · info", enabled=use_color))
        _type_color = {
          "dc_ac": "bright_cyan",
          "within_idempotent": "cyan", "within_biphasic": "yellow",
          "within_involutive": "magenta", "within_asymmetric": "red",
          "asymmetric_to_biphasic": "bright_red", "biphasic_to_idempotent": "bright_yellow",
          "idempotent_to_involutive": "bright_cyan", "involutive_to_asymmetric": "bright_magenta",
        }
        t = Box(["edge type", "count"], col_align=["l", "r"], enabled=use_color)
        for k, v in sorted(by_type.items()):
          col = _type_color.get(k)
          t.row([colorize(k, col, use_color), colorize(str(v), "bright_white", use_color)])
        print(t.render())
        print(kv("nodes", colorize(str(nc), "bright_white", use_color), use_color)
              + "   " + kv("edges", colorize(str(ec), "bright_white", use_color), use_color))
        return 0

    if args.cmd == "crypto":
      from .crypto import encrypt as c_encrypt, decrypt as c_decrypt, encrypt_secure, decrypt_secure
      text = read_input(getattr(args, 'text', None), getattr(args, 'file', None))
      mode = getattr(args, 'mode', 'edpc')
      if args.crypto_cmd == 'encrypt':
        print(c_encrypt(text, args.key, principle) if mode == 'edpc' else encrypt_secure(text, args.key))
        return 0
      if args.crypto_cmd == 'decrypt':
        print(c_decrypt(text, args.key, principle) if mode == 'edpc' else decrypt_secure(text, args.key))
        return 0
    if args.cmd == "reset":
      target_state = getattr(args, "state", None)
      only_rules = bool(args.rules_only)
      only_symbols = bool(args.symbols_only)
      do_plugins = bool(args.plugins or args.all)
      # Confirmation unless --yes
      if not getattr(args, "yes", False):
        print("This will reset your Gdk9 environment:")
        print(f"- State file: {'default (~/.gdk9/state.json)' if not target_state else target_state}")
        print(f"- State scope: {'rules-only' if only_rules else ('symbols-only' if only_symbols else 'full')}")
        print(f"- Plugins config: {'yes' if do_plugins else 'no'}")
        resp = input("Proceed? type 'yes' to confirm: ").strip().lower()
        if resp != 'yes':
          print("aborted")
          return 2
      # Reset state
      if only_rules or only_symbols:
        cur = load_state(target_state)
        if only_rules:
          cur['rules'] = {}
        if only_symbols:
          cur['symbols'] = {}
        save_state(cur, target_state)
      else:
        save_state({"symbols": {}, "rules": {}}, target_state)
      # Reset plugins if requested
      if do_plugins:
        from pathlib import Path
        plugins_reset_config()
      print(json.dumps({"ok": True, "reset": {"state": True, "plugins": do_plugins, "scope": ("rules-only" if only_rules else ("symbols-only" if only_symbols else "full")) }}, indent=2))
      return 0
    if args.cmd == "state":
      base = load_state(state_path)
      incoming = load_state(args.incoming)
      merged, stats = merge_state(base, incoming)
      if not args.dry_run:
        save_state(merged, state_path)
      print(
        json.dumps(
          {
            "ok": True,
            "state": state_path or "~/.gdk9/state.json",
            "dry_run": bool(args.dry_run),
            "stats": stats,
          },
          indent=2,
        )
      )
      return 0
    if args.cmd == "tokenize":
      text = read_input(args.text, args.file)
      keep = bool(getattr(args, "keep_delims", False)) or (not bool(getattr(args, "drop_delims", False)))
      strip_tokens = not bool(args.no_strip)
      if args.format == "json":
        print(
          to_json_payload(
            text,
            principle,
            energy=args.energy,
            delims=args.delims,
            keep_delims=keep,
            strip_tokens=strip_tokens,
          )
        )
        return 0
      if args.format == "annotate":
        print(
          annotate_text(
            text,
            principle,
            energy=args.energy,
            delims=args.delims,
            keep_delims=keep,
            strip_tokens=strip_tokens,
          )
        )
        return 0
      # table
      if not getattr(args, "summary_only", False):
        rows = summarize_tokens_table(
          text,
          principle,
          energy=args.energy,
          delims=args.delims,
          keep_delims=keep,
          strip_tokens=strip_tokens,
          use_color=(getattr(args, "color", False)) or (supports_color() and not getattr(args, "no_color", False)),
        )
        print_table(rows, use_color)
      # footer with metrics and delimiter set unless suppressed
      if not getattr(args, "no_footer", False):
        dset = args.delims if args.delims is not None else delimiter_set(principle, energy=args.energy)
        from .tokenize import tokens_with_energy, summarize_metrics_lines
        toks = tokens_with_energy(
          text,
          principle,
          energy=args.energy,
          delims=args.delims,
          keep_delims=keep,
          strip_tokens=strip_tokens,
        )
        for line in summarize_metrics_lines(text, toks, principle, dset, use_color):
          print(line)
      return 0
    if args.cmd == "principles":
      return cmd_principles(args, principle)
    if args.cmd == "optimize":
      return cmd_optimize(args, principle)
    if args.cmd == "help":
      topic = getattr(args, "topic", None)
      if not topic:
        parser.print_help()
        return 0
      # try subparser help
      try:
        sub = parser._subparsers._group_actions[0].choices[topic]  # type: ignore[attr-defined]
      except Exception:
        # try alias resolution
        for k, v in parser._subparsers._group_actions[0].choices.items():  # type: ignore[attr-defined]
          if hasattr(v, 'aliases') and topic in getattr(v, 'aliases', []):
            sub = v
            break
        else:
          print(f"Unknown help topic: {topic}")
          return 2
      sub.print_help()
      return 0
    if args.cmd == "handbook":
      from pathlib import Path
      here = Path(__file__).resolve().parent
      hb = here.parent / 'docs' / 'HANDBOOK.md'
      if hb.exists():
        print(hb.read_text(encoding='utf-8'))
      else:
        print("Handbook not found in package; refer to docs/HANDBOOK.md in the repository.")
      return 0
    if args.cmd == "tui":
      from .tui import start, TuiOptions
      return start(principle, TuiOptions(target=args.target, allowed=args.allowed, method=args.method))
    if args.cmd == "subs":
      if args.action == "example":
        print(json.dumps({"subs": {"i": ["1", "!"], "s": ["$"], "e": ["3"]}, "allowed_inserts": ".!?+"}, indent=2))
        return 0
      if args.action == "generate":
        from .subs import build_subs_json
        payload = build_subs_json(principle, limit=args.limit)
        if args.output:
          from pathlib import Path
          Path(args.output).write_text(payload, encoding='utf-8')
          print(args.output)
        else:
          print(payload)
        return 0
    if args.cmd == "symbol":
      state = load_state(state_path)
      if args.symbol_cmd == "add":
        from .imply import validate_symbol_name
        validate_symbol_name(args.name)
        set_symbol(state, args.name, float(args.energy))
        save_state(state, state_path)
        print(json.dumps({"ok": True, "symbol": {args.name: float(args.energy)}}, indent=2))
        return 0
      if args.symbol_cmd == "list":
        print(json.dumps({"symbols": list_symbols(load_state(state_path))}, indent=2))
        return 0
    if args.cmd == "kernel":
      return run_kernel(args, principle)
    if args.cmd == "imply":
      state = load_state(state_path)
      rules = state.setdefault("rules", {})
      if args.imply_cmd == "define-fusion":
        r = make_fusion(args.rule, args.out_name, args.arity)
        set_rule(state, r.name, r.to_json())
        save_state(state, state_path)
        print(json.dumps({"ok": True, "rule": r.to_json()}, indent=2))
        return 0
      if args.imply_cmd == "define-split":
        r = make_split(args.rule, args.out_a, args.out_b, args.ratio)
        set_rule(state, r.name, r.to_json())
        save_state(state, state_path)
        print(json.dumps({"ok": True, "rule": r.to_json()}, indent=2))
        return 0
      if args.imply_cmd == "list":
        print(json.dumps({"rules": rules}, indent=2))
        return 0
      if args.imply_cmd == "apply":
        if args.rule not in rules:
          raise InputError(f"Unknown rule: {args.rule}")
        rj = rules[args.rule]
        r = Rule(name=rj["name"], type=rj["type"], arity=int(rj["arity"]), params=rj.get("params", {}))
        tol = 1e-9
        if isinstance(principle.description, str) and "tolerance" in principle.description:
          pass
        res = apply_rule(r, state.get("symbols", {}), args.inputs, tol=tol)
        if args.commit:
          # write outputs back into symbols
          for o in res.get("outputs", []):
            set_symbol(state, o["name"], float(o["energy"]))
          save_state(state, state_path)
          res = {**res, "committed": True}
        print(json.dumps(res, indent=2))
        return 0
    if args.cmd == "plugin":
      if args.plugin_cmd == "list":
        print(json.dumps({"plugins": plugins_list_available()}, indent=2))
        return 0
      if args.plugin_cmd == "validate":
        ppath = plugins_find(args.name_or_path)
        _ = plugins_load(ppath)
        print(json.dumps({"ok": True, "path": str(ppath)}, indent=2))
        return 0
      if args.plugin_cmd == "info":
        ppath = plugins_find(args.name_or_path)
        plg = plugins_load(ppath)
        print(json.dumps({
          "name": plg.name,
          "version": plg.version,
          "description": plg.description,
          "rules": [r.to_json() for r in plg.rules],
          "symbol_energy": plg.symbol_energy,
          "symbols": plg.symbols,
          "source": str(plg.source),
        }, ensure_ascii=False, indent=2))
        return 0
      if args.plugin_cmd == "load":
        ppath = plugins_find(args.name_or_path)
        plg = plugins_load(ppath)
        pr, st, stats = plugins_apply(plg, principle, load_state(state_path))
        save_state(st, state_path)
        if not args.no_enable:
          plugins_enable(plg.name, ppath)
        print(json.dumps({"ok": True, "name": plg.name, "applied": stats, "enabled": (not args.no_enable)}, indent=2))
        return 0
      if args.plugin_cmd == "enable":
        ppath = plugins_find(args.name_or_path)
        plg = plugins_load(ppath)
        plugins_enable(plg.name, ppath)
        print(json.dumps({"ok": True, "enabled": plg.name}, indent=2))
        return 0
      if args.plugin_cmd == "disable":
        plugins_disable(args.name)
        print(json.dumps({"ok": True, "disabled": args.name}, indent=2))
        return 0
    if args.cmd == "repl":
      # Minimal REPL
      spath = state_path
      print("gdk9 repl. Type 'help' or 'quit'.")
      while True:
        try:
          line = input("gdk9> ").strip()
        except EOFError:
          break
        if not line:
          continue
        if line in {"quit", "exit"}:
          break
        if line == "help":
          print("commands: symbol add <NAME> <E>, symbol list, imply define-fusion <RULE> <OUT> <ARITY>, imply define-split <RULE> <A> <B> <RATIO>, imply list, imply apply <RULE> <INPUTS...>")
          continue
        try:
          parts = line.split()
          if parts[:2] == ["symbol", "add"] and len(parts) == 4:
            ns, e = parts[2], float(parts[3])
            st = load_state(spath)
            from .imply import validate_symbol_name
            validate_symbol_name(ns)
            set_symbol(st, ns, e)
            save_state(st, spath)
            print("ok")
            continue
          if parts[:2] == ["symbol", "list"]:
            print(json.dumps({"symbols": list_symbols(load_state(spath))}, indent=2))
            continue
          if parts[:3] == ["imply", "define-fusion",] and len(parts) == 5:
            _, _, rn, out, ar = parts
            st = load_state(spath)
            r = make_fusion(rn, out, int(ar))
            set_rule(st, rn, r.to_json())
            save_state(st, spath)
            print("ok")
            continue
          if parts[:3] == ["imply", "define-split"] and len(parts) == 6:
            _, _, rn, a, b, ratio = parts
            st = load_state(spath)
            r = make_split(rn, a, b, float(ratio))
            set_rule(st, rn, r.to_json())
            save_state(st, spath)
            print("ok")
            continue
          if parts[:2] == ["imply", "list"]:
            print(json.dumps({"rules": load_state(spath).get("rules", {})}, indent=2))
            continue
          if parts[:2] == ["imply", "apply"] and len(parts) >= 4:
            _, _, rn, *ins = parts
            commit = False
            if ins and ins[-1] in {"--commit", "commit"}:
              commit = True
              ins = ins[:-1]
            st = load_state(spath)
            rj = st.get("rules", {}).get(rn)
            if not rj:
              print("error: unknown rule")
              continue
            r = Rule(name=rj["name"], type=rj["type"], arity=int(rj["arity"]), params=rj.get("params", {}))
            res = apply_rule(r, st.get("symbols", {}), ins, tol=1e-9)
            if commit:
              for o in res.get("outputs", []):
                set_symbol(st, o["name"], float(o["energy"]))
              save_state(st, spath)
              res = {**res, "committed": True}
            print(json.dumps(res, indent=2))
            continue
          print("error: unknown command")
        except Exception as exc:
          print(f"error: {exc}")
      return 0
    parser.print_help()
    return 0
  except (Gdk9Error, ConfigError, InputError, OptimizationError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    return 2
  except BrokenPipeError:
    return 0


if __name__ == "__main__":  # pragma: no cover
  raise SystemExit(main())
