"""Handbook kernel CLI doctest gate.

Pins ``gdk9 kernel eval|apply|search`` JSON cited in docs/KERNEL.md /
docs/HANDBOOK.md §8 so handbook examples cannot drift from live CLI.

Fixtures: tests/fixtures/kernel_cli_handbook.json
Regenerate: see the ``regenerate`` field in the fixture (or docs/KERNEL.md).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "kernel_cli_handbook.json"
CASE_IDS = ("eval_ABC", "apply_fuse_A_B", "search_A_B_to_AB")


def _load_fixture() -> dict[str, Any]:
  with FIXTURE_PATH.open(encoding="utf-8") as fh:
    return json.load(fh)


@pytest.fixture(scope="module")
def handbook_fixture() -> dict[str, Any]:
  return _load_fixture()


@pytest.fixture(scope="module")
def cases_by_id(handbook_fixture: dict[str, Any]) -> dict[str, dict[str, Any]]:
  cases = handbook_fixture["cases"]
  by_id = {c["id"]: c for c in cases}
  assert tuple(by_id) == CASE_IDS or set(by_id) == set(CASE_IDS)
  for expected_id in CASE_IDS:
    assert expected_id in by_id
  return by_id


def _run_cli(argv: list[str]) -> dict[str, Any]:
  proc = subprocess.run(
    [sys.executable, "-m", "gdk9.cli", *argv],
    capture_output=True,
    text=True,
    check=False,
  )
  assert proc.returncode == 0, (
    f"CLI failed argv={argv!r} rc={proc.returncode}\n"
    f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
  )
  return json.loads(proc.stdout)


def test_fixture_lists_three_handbook_cases(handbook_fixture: dict[str, Any]) -> None:
  assert "cases" in handbook_fixture
  ids = [c["id"] for c in handbook_fixture["cases"]]
  assert ids == list(CASE_IDS)
  assert handbook_fixture.get("regenerate"), "fixture must document regenerate commands"


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_cli_json_matches_fixture(
  cases_by_id: dict[str, dict[str, Any]], case_id: str
) -> None:
  case = cases_by_id[case_id]
  live = _run_cli(list(case["argv"]))
  # Stable key order / exact structural equality with pinned live JSON.
  assert live == case["output"]
  # Round-trip through sorted dumps to catch key-order / float formatting drift
  # in future fixture edits (live vs pin must serialize identically when sorted).
  assert json.dumps(live, sort_keys=True) == json.dumps(case["output"], sort_keys=True)


def test_handbook_section8_numeric_claims(cases_by_id: dict[str, dict[str, Any]]) -> None:
  """Small numeric claims from HANDBOOK §8 / KERNEL smoke examples."""
  eval_out = cases_by_id["eval_ABC"]["output"]
  assert eval_out["total"] == 6.0
  assert eval_out["digital_root"] == 6
  assert eval_out["expression"]["symbols"] == [
    {"name": "A", "energy": 1.0},
    {"name": "B", "energy": 2.0},
    {"name": "C", "energy": 3.0},
  ]

  apply_out = cases_by_id["apply_fuse_A_B"]["output"]
  judgment = apply_out["judgment"]
  assert judgment["conserved"] is True
  assert judgment["delta"] == 0.0
  assert judgment["before"]["total_energy"] == 3.0
  assert judgment["after"]["names"] == ["AB"]
  assert judgment["after"]["total_energy"] == 3.0

  search_out = cases_by_id["search_A_B_to_AB"]["output"]
  assert search_out["found"] is True
  assert search_out["max_depth"] == 2
  assert search_out["rules"] == ["fuse"]
  assert len(search_out["steps"]) == 1
  assert search_out["steps"][0]["judgment"]["rule"] == "fuse"