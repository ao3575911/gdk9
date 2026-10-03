from __future__ import annotations

import curses
import time
from dataclasses import dataclass
from typing import Optional

from .principles import Principle
from .energy import string_energy, energy_profile, vector_energy, harmonic_triads
from .optimize import optimize_attunement, apply_plan


@dataclass
class TuiOptions:
  target: int = 9
  allowed: str = ".!?*+"
  method: str = "append"


def _draw_profile(win, prof):
  win.addstr(0, 0, "Profile 1-9:")
  for i in range(1, 10):
    win.addstr(1, (i - 1) * 3, f"{i}:{prof[str(i)]:2d}")


def _draw_vector(win, vec):
  win.addstr(0, 0, "Vector sums/dr:")
  win.addstr(1, 0, f"L {vec['sum']['letters']:3d} (dr {vec['dr']['letters']})")
  win.addstr(2, 0, f"D {vec['sum']['digits']:3d} (dr {vec['dr']['digits']})")
  win.addstr(3, 0, f"S {vec['sum']['symbols']:3d} (dr {vec['dr']['symbols']})")


def _draw_harm(win, harm):
  win.addstr(0, 0, "Harmonics:")
  win.addstr(1, 0, f"root {harm['root']:3d}")
  win.addstr(2, 0, f"wave {harm['wave']:3d}")
  win.addstr(3, 0, f"peak {harm['peak']:3d}")


def _draw_help(win):
  win.addstr(0, 0, "F2 target  F3 method  F4 attune  F10 quit")


def start(principle: Optional[Principle] = None, opts: Optional[TuiOptions] = None) -> int:
  pr = principle or Principle.default()
  options = opts or TuiOptions()

  def _main(stdscr):
    curses.curs_set(1)
    stdscr.nodelay(True)
    max_y, max_x = stdscr.getmaxyx()
    input_win = curses.newwin(3, max_x, 0, 0)
    status_win = curses.newwin(3, max_x, 3, 0)
    prof_win = curses.newwin(2, max_x, 6, 0)
    vec_win = curses.newwin(5, max_x // 2, 8, 0)
    harm_win = curses.newwin(5, max_x // 2, 8, max_x // 2)
    help_win = curses.newwin(1, max_x, max_y - 1, 0)

    buf = ""
    last_draw = 0.0

    while True:
      now = time.time()
      ch = stdscr.getch()
      if ch != -1:
        if ch in (curses.KEY_EXIT, 27, curses.KEY_F10):
          break
        if ch in (curses.KEY_BACKSPACE, 127):
          buf = buf[:-1]
        elif ch == curses.KEY_F2:
          options.target = (options.target % 9) + 1
        elif ch == curses.KEY_F3:
          options.method = {"append": "intersperse", "intersperse": "prepend", "prepend": "append"}[options.method]
        elif ch == curses.KEY_F4:
          try:
            plan = optimize_attunement(buf, options.target, pr, allowed_symbols=options.allowed, method=options.method)
            buf2 = apply_plan(buf, plan)
            buf = buf2
          except Exception:
            pass
        elif ch == 10:  # Enter
          buf += "\n"
        elif 0 <= ch < 256:
          buf += chr(ch)

      if now - last_draw > 0.05:  # ~20 FPS max
        last_draw = now
        input_win.erase()
        status_win.erase()
        prof_win.erase()
        vec_win.erase()
        harm_win.erase()
        help_win.erase()

        input_win.addstr(0, 0, "Input:")
        input_win.addstr(1, 0, buf[: max_x - 1])
        total, dr = string_energy(buf, pr)
        status_win.addstr(0, 0, f"TOTAL {total}  DR {dr}  -> target {options.target}  method {options.method}")
        prof = energy_profile(buf, pr)
        _draw_profile(prof_win, prof)
        vec = vector_energy(buf, pr)
        _draw_vector(vec_win, vec)
        harm = harmonic_triads(buf, pr)
        _draw_harm(harm_win, harm)
        _draw_help(help_win)

        for w in (input_win, status_win, prof_win, vec_win, harm_win, help_win):
          w.noutrefresh()
        curses.doupdate()

      time.sleep(0.01)

  curses.wrapper(_main)
  return 0

