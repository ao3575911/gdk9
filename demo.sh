#!/usr/bin/env bash
#
# GDk9 v0.3.0 — asciinema demo
#
# Record:   asciinema rec gdk9-demo.cast -c "bash demo.sh" --idle-time-limit 2
# Preview:  asciinema play gdk9-demo.cast
# Upload:   asciinema upload gdk9-demo.cast
#
# Pre-flight:
#   1. pip install -e .        # gdk9 must be on PATH
#   2. brew install pv         # optional, for the typing animation
#   3. resize terminal to ~100x30
#   4. export PS1='$ '         # clean prompt
#   5. clear
#
# Target length: ~60–75 seconds.
#

set -e

TYPE_SPEED=28        # chars/sec when "typing"
DEMO_PROMPT="$ "

# print + execute, with simulated typing if pv is available
pe() {
  printf "%s" "$DEMO_PROMPT"
  if command -v pv >/dev/null 2>&1; then
    printf "%s" "$1" | pv -qL $TYPE_SPEED
  else
    printf "%s" "$1"
  fi
  echo
  sleep 0.4
  eval "$1"
  echo
  sleep 1.2
}

# print a comment line (slower, for reading)
pc() {
  printf "\033[2m# %s\033[0m\n" "$1"
  sleep 1.3
}

clear

pc "GDk9 v0.3.0 — symbolic energy CLI"
pc "Python >= 3.9, zero runtime deps"
sleep 1

pc "1. confirm install"
pe 'gdk9 --version'

pc "2. classify a word: see each letter's energy and symmetry class"
pe 'gdk9 --color dcg classify FWEM'

pc "3. energy profile of a full sentence (digital-root histogram)"
pe 'gdk9 --color profile "The quick brown fox jumps over the lazy dog"'

pc "4. compare two inputs side-by-side"
pe 'python scripts/profile_compare.py "hello world" "energy flow"'

pc "5. full JSON export — pipe into anything"
pe 'python scripts/export_json.py "AVWM" | head -20'

pc "6. plugins shipped in v0.3.0"
pe 'ls plugins/'

pc ""
pc "  pip install git+https://github.com/ao3575911/gdk9.git@v0.3.0"
pc "  github.com/ao3575911/gdk9"
sleep 3
