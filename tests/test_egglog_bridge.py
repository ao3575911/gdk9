"""Optional egglog bridge tests.

``egglog``-marked tests skip cleanly when the optional extra is missing
(``pytest.importorskip``). Default CI (``dev`` / ``dev,secure``) stays green.
The optional CI job installs ``.[dev,egglog]`` on Python ≥3.11 and expects
the marked tests to run for real. See docs/SPIKE-egglog.md.
"""
from __future__ import annotations

import pytest

from gdk9.egglog_bridge.fallback import saturate_fallback

FIXTURE = [26, 10, 9]


def test_egglog_fallback_saturate_default_fixture():
  """Fallback rewriter (no egglog) matches spike fixture DR == 9."""
  result = saturate_fallback(FIXTURE)
  assert result["best_dr"] == 9
  assert result["congruence_dr"] == 9
  assert result["ok"] is True


@pytest.mark.egglog
def test_egglog_saturate_matches_fallback():
  """With egglog installed: saturate_egglog best_dr matches fallback."""
  pytest.importorskip("egglog")
  from gdk9.egglog_bridge.dr_egglog import saturate_egglog

  egg = saturate_egglog(FIXTURE)
  fb = saturate_fallback(FIXTURE)
  assert egg["best_dr"] == 9
  assert egg["ok"] is True
  assert egg["best_dr"] == fb["best_dr"]


@pytest.mark.egglog
def test_egglog_import_or_skip():
  """Explicit skip surface: collecting this test must not red without egglog."""
  pytest.importorskip("egglog")
